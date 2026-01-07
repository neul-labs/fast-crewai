"""
High-performance SQLite wrapper using Rust backend.

This module provides a drop-in replacement for CrewAI's database
operations with connection pooling and performance improvements.
"""

import json
import logging
import os
import pathlib
import sqlite3
from typing import Any, Dict, List, Optional, Union

from ._constants import HAS_ACCELERATION_IMPLEMENTATION

# Configure module logger
_logger = logging.getLogger(__name__)

# Constants for configuration
DEFAULT_POOL_SIZE = 5
DEFAULT_QUERY_LIMIT = 1000
MAX_QUERY_LIMIT = 10000

# Try to import the Rust implementation
if HAS_ACCELERATION_IMPLEMENTATION:
    try:
        from ._core import RustSQLiteWrapper as _RustSQLiteWrapper

        _RUST_AVAILABLE = True
    except ImportError:
        _RUST_AVAILABLE = False
else:
    _RUST_AVAILABLE = False


def _validate_db_path(db_path: str) -> None:
    """
    Validate database path to prevent path traversal attacks.

    Args:
        db_path: Path to validate

    Raises:
        ValueError: If path contains traversal sequences or is absolute outside allowed directory
    """
    import platform

    # Resolve the path to handle relative paths
    resolved = pathlib.Path(db_path).resolve()

    # Check for path traversal sequences
    if ".." in db_path or "\\" in db_path and ".." in db_path:
        raise ValueError(f"Invalid database path: contains path traversal sequence")

    # Ensure the resolved path is within the current working directory or allowed locations
    cwd = pathlib.Path.cwd().resolve()
    allowed_prefixes = [
        cwd,
        pathlib.Path("/tmp"),
        pathlib.Path.home(),
    ]

    # On macOS, tempfile uses /var/folders/... so we need to allow that
    system = platform.system()
    if system == "Darwin":
        allowed_prefixes.append(pathlib.Path("/var/folders"))

    is_allowed = any(
        str(resolved).startswith(str(prefix.resolve())) or resolved == prefix.resolve()
        for prefix in allowed_prefixes
    )

    if not is_allowed:
        raise ValueError(
            f"Database path must be within allowed directories. "
            f"Allowed prefixes: {[str(p) for p in allowed_prefixes]}"
        )


class AcceleratedSQLiteWrapper:
    """
    High-performance SQLite wrapper using Rust backend.

    This class provides a drop-in replacement for CrewAI's database operations
    with connection pooling and performance improvements while maintaining full
    API compatibility.
    """

    def __init__(self, db_path: str, pool_size: int = DEFAULT_POOL_SIZE, use_rust: Optional[bool] = None):
        """
        Initialize the SQLite wrapper.

        Args:
            db_path: Path to the SQLite database file
            pool_size: Connection pool size (for Rust implementation)
            use_rust: Whether to use the Rust implementation. If None,
                     automatically detects based on availability and
                     environment variables.

        Raises:
            ValueError: If db_path contains invalid sequences
        """
        # Validate the database path
        _validate_db_path(db_path)

        self.db_path = db_path
        self.pool_size = pool_size

        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv("FAST_CREWAI_DATABASE", "auto").lower()
            if env_setting == "true":
                self._use_rust = True
            elif env_setting == "false":
                self._use_rust = False
            else:  # 'auto' or other values
                self._use_rust = _RUST_AVAILABLE
        else:
            self._use_rust = use_rust and _RUST_AVAILABLE

        # Initialize the appropriate implementation
        if self._use_rust:
            try:
                self._wrapper = _RustSQLiteWrapper(db_path, pool_size)
                self._implementation = "rust"
            except Exception as e:
                # Fallback to Python implementation
                self._use_rust = False
                self._wrapper = None
                self._implementation = "python"
                self._initialize_python_db()
                _logger.warning(
                    "Failed to initialize Rust SQLite wrapper, falling back to Python: %s", e
                )
        else:
            self._wrapper = None
            self._implementation = "python"
            self._initialize_python_db()

    def _initialize_python_db(self):
        """Initialize the Python SQLite database."""
        # Ensure the database file exists and has the proper schema
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Create tables if they don't exist
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS long_term_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_description TEXT,
                        metadata TEXT,
                        datetime TEXT,
                        score REAL
                    )
                """
                )
                conn.commit()
        except Exception as e:
            _logger.warning("Failed to initialize Python SQLite database: %s", e)

    def execute_query(self, query: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query.

        Args:
            query: SQL query to execute
            params: Parameters for the query (dict for named params, tuple for positional)

        Returns:
            List of result rows as dictionaries
        """
        if self._use_rust:
            try:
                # Rust implementation requires dict with named parameters
                # Convert tuple to dict if needed, using :param1, :param2 style
                if isinstance(params, tuple):
                    # For tuple params, fall back to Python as Rust expects dict
                    return self._python_execute_query(query, params)
                params_dict = params or {}
                result_dicts = self._wrapper.execute_query(query, params_dict)
                return result_dicts
            except Exception as e:
                # Fallback to Python implementation on error
                _logger.debug("Rust query execution failed, using Python fallback: %s", e)
                return self._python_execute_query(query, params)
        else:
            return self._python_execute_query(query, params)

    def _python_execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Python implementation of query execution for fallback."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                rows = cursor.fetchall()
                # Convert rows to dictionaries
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Database query failed: {str(e)}")

    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            Number of affected rows
        """
        if self._use_rust:
            try:
                # Convert params to a format Rust can handle
                params_dict = params or {}
                affected_rows = self._wrapper.execute_update(query, params_dict)
                return affected_rows
            except Exception as e:
                # Fallback to Python implementation on error
                _logger.debug("Rust update execution failed, using Python fallback: %s", e)
                self._use_rust = False
                return self._python_execute_update(query, params)
        else:
            return self._python_execute_update(query, params)

    def _python_execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Python implementation of update execution for fallback."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            raise Exception(f"Database update failed: {str(e)}")

    def execute_batch(self, queries: List[tuple]) -> List[int]:
        """
        Execute multiple queries in a transaction.

        Args:
            queries: List of (query, params) tuples

        Returns:
            List of affected row counts for each query
        """
        if self._use_rust:
            try:
                # Convert to format Rust can handle
                rust_queries = []
                for query, params in queries:
                    params_dict = params or {}
                    rust_queries.append((query, params_dict))

                affected_counts = self._wrapper.execute_batch(rust_queries)
                return affected_counts
            except Exception as e:
                # Fallback to Python implementation on error
                _logger.debug("Rust batch execution failed, using Python fallback: %s", e)
                self._use_rust = False
                return self._python_execute_batch(queries)
        else:
            return self._python_execute_batch(queries)

    def _python_execute_batch(self, queries: List[tuple]) -> List[int]:
        """Python implementation of batch execution for fallback."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                affected_counts = []

                for query, params in queries:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    affected_counts.append(cursor.rowcount)

                conn.commit()
                return affected_counts
        except Exception as e:
            raise Exception(f"Database batch execution failed: {str(e)}")

    def save_memory(
        self,
        task_description: str,
        metadata: Dict[str, Any],
        datetime: str,
        score: Union[int, float],
    ) -> Optional[int]:
        """
        Save a memory entry to the database.

        Args:
            task_description: Description of the task
            metadata: Metadata associated with the memory
            datetime: Timestamp of the memory
            score: Score or priority of the memory

        Returns:
            The ID of the inserted row, or None on failure
        """
        if self._use_rust:
            try:
                # Use the new Rust insert_memory method for better performance
                row_id = self._wrapper.insert_memory(
                    task_description, json.dumps(metadata), datetime, float(score)
                )
                return row_id
            except Exception as e:
                _logger.debug("Rust insert_memory failed, using Python fallback: %s", e)
                self._use_rust = False
                return self._python_save_memory(task_description, metadata, datetime, score)
        else:
            return self._python_save_memory(task_description, metadata, datetime, score)

    def _python_save_memory(
        self,
        task_description: str,
        metadata: Dict[str, Any],
        datetime: str,
        score: Union[int, float],
    ) -> Optional[int]:
        """Python implementation of save_memory for fallback."""
        query = """
            INSERT INTO long_term_memories (task_description, metadata, datetime, score)
            VALUES (?, ?, ?, ?)
        """
        params = (task_description, json.dumps(metadata), datetime, float(score))
        self._python_execute_update(query, params)
        return None  # Python implementation doesn't return row ID

    def search_memories_fts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories using FTS5 full-text search (Rust only).

        This method uses SQLite FTS5 with BM25 ranking for fast, relevance-ranked
        full-text search. Falls back to simple LIKE queries in Python.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching memory entries ranked by relevance
        """
        if self._use_rust:
            try:
                # Use the new Rust FTS5 search method
                results = self._wrapper.search_memories(query, limit)
                # Parse metadata from JSON strings
                parsed_results = []
                for row in results:
                    try:
                        metadata = json.loads(row.get("metadata", "{}"))
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                    parsed_results.append(
                        {
                            "id": row.get("id"),
                            "task_description": row.get("task_description"),
                            "metadata": metadata,
                            "datetime": row.get("datetime"),
                            "score": float(row.get("score", 0)),
                            "rank": float(row.get("rank", 0)),
                        }
                    )
                return parsed_results
            except Exception as e:
                _logger.debug("Rust FTS5 search failed, using Python fallback: %s", e)
                return self._python_search_memories(query, limit)
        else:
            return self._python_search_memories(query, limit)

    def _python_search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Python implementation of search using LIKE queries."""
        # Validate and sanitize the limit parameter
        if not isinstance(limit, int):
            limit = 10
        limit = max(1, min(limit, MAX_QUERY_LIMIT))

        search_query = """
            SELECT id, task_description, metadata, datetime, score
            FROM long_term_memories
            WHERE task_description LIKE ? OR metadata LIKE ?
            ORDER BY datetime DESC
            LIMIT ?
        """
        search_pattern = f"%{query}%"
        rows = self._python_execute_query(search_query, (search_pattern, search_pattern, limit))
        parsed_results = []
        for row in rows:
            try:
                metadata = json.loads(row.get("metadata", "{}"))
            except (json.JSONDecodeError, TypeError):
                metadata = {}
            parsed_results.append(
                {
                    "id": row.get("id"),
                    "task_description": row.get("task_description"),
                    "metadata": metadata,
                    "datetime": row.get("datetime"),
                    "score": float(row.get("score", 0)),
                    "rank": 0.0,  # Python fallback doesn't have BM25 ranking
                }
            )
        return parsed_results

    def get_all_memories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all memories ordered by datetime (most recent first).

        Args:
            limit: Maximum number of results to return

        Returns:
            List of memory entries
        """
        # Validate and sanitize the limit parameter
        if not isinstance(limit, int):
            limit = 100
        limit = max(1, min(limit, MAX_QUERY_LIMIT))
        if self._use_rust:
            try:
                results = self._wrapper.get_all_memories(limit)
                parsed_results = []
                for row in results:
                    try:
                        metadata = json.loads(row.get("metadata", "{}"))
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                    parsed_results.append(
                        {
                            "id": row.get("id"),
                            "task_description": row.get("task_description"),
                            "metadata": metadata,
                            "datetime": row.get("datetime"),
                            "score": float(row.get("score", 0)),
                        }
                    )
                return parsed_results
            except Exception as e:
                _logger.debug("Rust get_all_memories failed, using Python fallback: %s", e)
                return self._python_get_all_memories(limit)
        else:
            return self._python_get_all_memories(limit)

    def _python_get_all_memories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Python implementation of get_all_memories."""
        # Validate and sanitize the limit parameter
        if not isinstance(limit, int):
            limit = 100
        limit = max(1, min(limit, MAX_QUERY_LIMIT))

        query = """
            SELECT id, task_description, metadata, datetime, score
            FROM long_term_memories
            ORDER BY datetime DESC
            LIMIT ?
        """
        rows = self._python_execute_query(query, (limit,))
        parsed_results = []
        for row in rows:
            try:
                metadata = json.loads(row.get("metadata", "{}"))
            except (json.JSONDecodeError, TypeError):
                metadata = {}
            parsed_results.append(
                {
                    "id": row.get("id"),
                    "task_description": row.get("task_description"),
                    "metadata": metadata,
                    "datetime": row.get("datetime"),
                    "score": float(row.get("score", 0)),
                }
            )
        return parsed_results

    def load_memories(
        self, task_description: str, latest_n: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Load memory entries from the database.

        Args:
            task_description: Description of the task to load memories for
            latest_n: Number of latest memories to load

        Returns:
            List of memory entries or None if not found

        Raises:
            ValueError: If latest_n is out of valid range
        """
        # Validate and sanitize the limit parameter
        if not isinstance(latest_n, int):
            raise ValueError("latest_n must be an integer")
        if latest_n < 1:
            latest_n = 1
        if latest_n > MAX_QUERY_LIMIT:
            latest_n = MAX_QUERY_LIMIT

        query = """
            SELECT metadata, datetime, score
            FROM long_term_memories
            WHERE task_description = ?
            ORDER BY datetime DESC, score ASC
            LIMIT ?
        """
        params = (task_description, latest_n)
        rows = self.execute_query(query, params)

        if rows:
            results = []
            for row in rows:
                try:
                    metadata = (
                        json.loads(row["metadata"])
                        if isinstance(row["metadata"], str)
                        else row["metadata"]
                    )
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

                results.append(
                    {
                        "metadata": metadata,
                        "datetime": row["datetime"],
                        "score": row["score"],
                    }
                )
            return results

        return None

    def reset(self) -> None:
        """Reset the database by deleting all entries."""
        query = "DELETE FROM long_term_memories"
        self.execute_update(query)

    @property
    def implementation(self) -> str:
        """Get the current implementation type."""
        return self._implementation

    def __repr__(self) -> str:
        """String representation of the wrapper."""
        return (
            f"AcceleratedSQLiteWrapper(implementation={self.implementation}, "
            f"db_path={self.db_path})"
        )

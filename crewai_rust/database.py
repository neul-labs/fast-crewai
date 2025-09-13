"""
High-performance SQLite wrapper using Rust backend.

This module provides a drop-in replacement for CrewAI's database
operations with connection pooling and performance improvements.
"""

import os
import json
import sqlite3
from typing import Any, Dict, List, Optional, Union
from . import HAS_RUST_IMPLEMENTATION

# Try to import the Rust implementation
if HAS_RUST_IMPLEMENTATION:
    try:
        from ._core import RustSQLiteWrapper as _RustSQLiteWrapper
        _RUST_AVAILABLE = True
    except ImportError:
        _RUST_AVAILABLE = False
else:
    _RUST_AVAILABLE = False


class RustSQLiteWrapper:
    """
    High-performance SQLite wrapper using Rust backend.
    
    This class provides a drop-in replacement for CrewAI's database operations
    with connection pooling and performance improvements while maintaining full
    API compatibility.
    """
    
    def __init__(
        self, 
        db_path: str,
        pool_size: int = 5,
        use_rust: Optional[bool] = None
    ):
        """
        Initialize the SQLite wrapper.
        
        Args:
            db_path: Path to the SQLite database file
            pool_size: Connection pool size (for Rust implementation)
            use_rust: Whether to use the Rust implementation. If None, 
                     automatically detects based on availability and 
                     environment variables.
        """
        self.db_path = db_path
        self.pool_size = pool_size
        
        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv('CREWAI_RUST_DATABASE', 'auto').lower()
            if env_setting == 'true':
                self._use_rust = True
            elif env_setting == 'false':
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
                print(f"Warning: Failed to initialize Rust SQLite wrapper, falling back to Python: {e}")
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
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS long_term_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_description TEXT,
                        metadata TEXT,
                        datetime TEXT,
                        score REAL
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Warning: Failed to initialize Python SQLite database: {e}")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            List of result rows as dictionaries
        """
        if self._use_rust:
            try:
                # Convert params to a format Rust can handle
                params_dict = params or {}
                result_dicts = self._wrapper.execute_query(query, params_dict)
                return result_dicts
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust query execution failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_execute_query(query, params)
        else:
            return self._python_execute_query(query, params)
    
    def _python_execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
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
    
    def execute_update(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> int:
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
                print(f"Warning: Rust update execution failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_execute_update(query, params)
        else:
            return self._python_execute_update(query, params)
    
    def _python_execute_update(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> int:
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
    
    def execute_batch(
        self, 
        queries: List[tuple]
    ) -> List[int]:
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
                print(f"Warning: Rust batch execution failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_execute_batch(queries)
        else:
            return self._python_execute_batch(queries)
    
    def _python_execute_batch(
        self, 
        queries: List[tuple]
    ) -> List[int]:
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
        score: Union[int, float]
    ) -> None:
        """
        Save a memory entry to the database.
        
        Args:
            task_description: Description of the task
            metadata: Metadata associated with the memory
            datetime: Timestamp of the memory
            score: Score or priority of the memory
        """
        query = """
            INSERT INTO long_term_memories (task_description, metadata, datetime, score)
            VALUES (?, ?, ?, ?)
        """
        params = (
            task_description,
            json.dumps(metadata),
            datetime,
            float(score)
        )
        self.execute_update(query, params)
    
    def load_memories(
        self,
        task_description: str,
        latest_n: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Load memory entries from the database.
        
        Args:
            task_description: Description of the task to load memories for
            latest_n: Number of latest memories to load
            
        Returns:
            List of memory entries or None if not found
        """
        query = f"""
            SELECT metadata, datetime, score
            FROM long_term_memories
            WHERE task_description = ?
            ORDER BY datetime DESC, score ASC
            LIMIT {latest_n}
        """
        params = (task_description,)
        rows = self.execute_query(query, params)
        
        if rows:
            results = []
            for row in rows:
                try:
                    metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
                
                results.append({
                    'metadata': metadata,
                    'datetime': row['datetime'],
                    'score': row['score']
                })
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
        return f"RustSQLiteWrapper(implementation={self.implementation}, db_path={self.db_path})"
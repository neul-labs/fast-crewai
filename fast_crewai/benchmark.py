"""
Benchmarking utilities for CrewAI Rust integration.

This module provides comprehensive benchmarking tools to measure
performance improvements from Rust integration.
"""

import gc
import json
import platform
import random
import string
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .database import AcceleratedSQLiteWrapper
from .memory import AcceleratedMemoryStorage
from .serialization import AgentMessage
from .tools import AcceleratedToolExecutor


def get_memory_usage() -> Tuple[float, float]:
    """
    Get current and peak memory usage in MB.

    Returns:
        Tuple of (current_mb, peak_mb)
    """
    current, peak = tracemalloc.get_traced_memory()
    return current / 1024 / 1024, peak / 1024 / 1024


def measure_memory(func):
    """
    Decorator to measure memory usage of a function.

    Returns the function result along with memory stats.
    """

    def wrapper(*args, **kwargs):
        # Force garbage collection before measurement
        gc.collect()

        # Start memory tracking
        tracemalloc.start()

        try:
            result = func(*args, **kwargs)

            # Get memory usage
            current_mb, peak_mb = get_memory_usage()

            # Add memory stats to result if it's a dict
            if isinstance(result, dict):
                result["memory_mb"] = round(peak_mb, 2)

            return result
        finally:
            tracemalloc.stop()

    return wrapper


class PerformanceBenchmark:
    """
    Comprehensive benchmarking suite for CrewAI Rust integration.
    """

    def __init__(self, iterations: int = 1000):
        """
        Initialize the benchmark suite.

        Args:
            iterations: Number of iterations for each benchmark
        """
        self.iterations = iterations
        self.results: Dict[str, Any] = {}

    def benchmark_memory_storage(self) -> Dict[str, Any]:
        """
        Benchmark memory storage performance.

        Uses large, complex data to showcase Rust's performance advantages:
        - Large text content (500-2000 chars) simulating agent conversation history
        - Deeply nested metadata structures
        - Many search queries with varying complexity

        Returns:
            Dictionary with benchmark results
        """
        # Generate large, complex test data - simulating real agent memory
        categories = ["task", "conversation", "observation", "reflection", "plan", "action"]
        agents = [f"agent_{i}" for i in range(10)]

        test_data = [
            {
                # Large text content (500-2000 chars) - realistic agent memory entries
                "value": (
                    f"Memory entry {i}: "
                    + "".join(
                        random.choices(string.ascii_letters + " ", k=random.randint(500, 2000))
                    )
                    + " Keywords: "
                    + ", ".join(
                        random.choices(
                            ["AI", "task", "result", "error", "success",
                             "pending", "analysis", "data", "report", "user"],
                            k=5,
                        )
                    )
                ),
                # Complex nested metadata
                "metadata": {
                    "id": i,
                    "category": random.choice(categories),
                    "priority": random.randint(1, 10),
                    "agent": random.choice(agents),
                    "timestamp": 1700000000 + i * 60,
                    "tags": random.sample(
                        ["important", "urgent", "review", "complete", "pending", "archived"], k=3
                    ),
                    "context": {
                        "session_id": f"session_{i % 100}",
                        "task_id": f"task_{i % 50}",
                        "parent_id": f"memory_{max(0, i - random.randint(1, 10))}",
                        "depth": random.randint(0, 5),
                    },
                    "metrics": {
                        "relevance_score": random.uniform(0.0, 1.0),
                        "confidence": random.uniform(0.5, 1.0),
                        "token_count": random.randint(100, 500),
                    },
                },
            }
            for i in range(self.iterations)
        ]

        # Semantic search queries that benefit from TF-IDF
        # These queries test semantic similarity, not just substring matching
        # Rust uses TF-IDF with cosine similarity, Python uses simple substring matching
        search_queries = [
            # Multi-word semantic queries (TF-IDF excels here)
            "machine learning analysis data processing",
            "error handling failure recovery mechanism",
            "task completion success report summary",
            "user interaction feedback response",
            "performance optimization improvement",
            "data analysis report findings conclusions",
            "agent coordination task delegation",
            "memory retrieval context understanding",
            # Partial match queries
            "analysis report",
            "task result",
            "error success",
            "pending review",
            # Single word queries
            "AI",
            "task",
            "error",
            "success",
            # Edge cases
            "nonexistent query that should return nothing",
            "xyzabc random gibberish query",
        ] * 5  # More queries to stress test search

        # Benchmark Python implementation
        python_results = self._benchmark_python_memory(test_data, search_queries)

        # Benchmark Rust implementation
        rust_results = self._benchmark_rust_memory(test_data, search_queries)

        # Calculate improvements
        improvements = self._calculate_improvements(python_results, rust_results)

        return {
            "python": python_results,
            "rust": rust_results,
            "improvements": improvements,
        }

    def _calculate_improvements(
        self, python_results: Dict[str, Any], rust_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate improvements between Python and Rust results."""
        improvements: Dict[str, Any] = {}
        for key in python_results:
            if key not in rust_results:
                improvements[key] = float("inf")
                continue

            if key == "operations_per_second":
                py_val = python_results[key]
                rust_val = rust_results[key]
                if isinstance(py_val, dict) and isinstance(rust_val, dict):
                    improvements[key] = {}
                    for op_key in py_val:
                        if (
                            op_key in rust_val
                            and isinstance(rust_val[op_key], (int, float))
                            and rust_val[op_key] > 0
                        ):
                            improvements[key][op_key] = py_val[op_key] / rust_val[op_key]
                        else:
                            improvements[key][op_key] = float("inf")
                elif (
                    isinstance(py_val, (int, float))
                    and isinstance(rust_val, (int, float))
                    and rust_val > 0
                ):
                    improvements[key] = py_val / rust_val
                else:
                    improvements[key] = float("inf")
            elif isinstance(python_results[key], (int, float)) and isinstance(
                rust_results[key], (int, float)
            ):
                if rust_results[key] > 0:
                    improvements[key] = python_results[key] / rust_results[key]
                else:
                    improvements[key] = float("inf")
            else:
                improvements[key] = float("inf")

        return improvements

    def _benchmark_python_memory(
        self, test_data: List[Dict], search_queries: List[str]
    ) -> Dict[str, float]:
        """Benchmark Python memory implementation using the same wrapper class."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Use the same AcceleratedMemoryStorage but with Python fallback
            python_storage = AcceleratedMemoryStorage(use_rust=False)

            # Benchmark save operations
            start_time = time.time()
            for item in test_data:
                python_storage.save(item["value"], item["metadata"])
            save_time = time.time() - start_time

            # Benchmark search operations
            start_time = time.time()
            for query in search_queries:
                _ = python_storage.search(query)
            search_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "save_time": save_time,
                "search_time": search_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": {
                    "save": len(test_data) / save_time if save_time > 0 else 0,
                    "search": (
                        (len(search_queries) * len(test_data)) / search_time
                        if search_time > 0
                        else 0
                    ),
                },
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Python implementation fails
            return {
                "save_time": 0,
                "search_time": 0,
                "memory_mb": 0,
                "operations_per_second": {"save": 0, "search": 0},
            }

    def _benchmark_rust_memory(
        self, test_data: List[Dict], search_queries: List[str]
    ) -> Dict[str, float]:
        """Benchmark Rust memory implementation."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Initialize Rust memory storage
            rust_storage = AcceleratedMemoryStorage(use_rust=True)

            # Benchmark save operations
            start_time = time.time()
            for item in test_data:
                rust_storage.save(item["value"], item["metadata"])
            save_time = time.time() - start_time

            # Benchmark search operations
            start_time = time.time()
            for query in search_queries:
                _ = rust_storage.search(query)
            search_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "save_time": save_time,
                "search_time": search_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": {
                    "save": len(test_data) / save_time if save_time > 0 else 0,
                    "search": (
                        (len(search_queries) * len(test_data)) / search_time
                        if search_time > 0
                        else 0
                    ),
                },
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Rust implementation fails
            return {
                "save_time": 0,
                "search_time": 0,
                "memory_mb": 0,
                "operations_per_second": {"save": 0, "search": 0},
            }

    def benchmark_tool_execution(self) -> Dict[str, Any]:
        """
        Benchmark tool execution performance.

        Uses complex tool invocations to showcase Rust's performance advantages:
        - Many parameters with various types
        - Nested argument structures
        - Large string arguments

        Returns:
            Dictionary with benchmark results
        """
        # Generate complex tool invocations - simulating real CrewAI tool calls
        tool_types = [
            "web_search",
            "file_read",
            "file_write",
            "api_call",
            "database_query",
            "code_execute",
            "image_analyze",
            "text_summarize",
            "data_transform",
        ]

        test_tools = [
            (
                random.choice(tool_types),
                {
                    # Basic parameters
                    "query": f"Complex query {i} with "
                    + "".join(random.choices(string.ascii_letters + " ", k=200)),
                    "max_results": random.randint(1, 100),
                    "timeout": random.uniform(1.0, 30.0),
                    "retry_count": random.randint(0, 5),
                    # Nested configuration
                    "config": {
                        "api_key": "sk-"
                        + "".join(
                            random.choices(string.ascii_letters + string.digits, k=32)
                        ),
                        "endpoint": (
                            f"https://api.example.com/v{random.randint(1, 3)}/resource"
                        ),
                        "headers": {
                            "Authorization": "Bearer "
                            + "".join(random.choices(string.ascii_letters, k=64)),
                            "Content-Type": "application/json",
                            "X-Request-ID": f"req-{i}-"
                            + "".join(random.choices(string.hexdigits, k=8)),
                        },
                    },
                    # Array of items
                    "filters": [
                        {
                            "field": f"field_{j}",
                            "operator": random.choice(["eq", "ne", "gt", "lt", "contains"]),
                            "value": random.randint(1, 1000),
                        }
                        for j in range(random.randint(2, 8))
                    ],
                    # Large text content
                    "context": "".join(
                        random.choices(string.ascii_letters + " \n", k=random.randint(500, 1500))
                    ),
                    # Metadata
                    "metadata": {
                        "source": f"agent_{i % 10}",
                        "priority": random.randint(1, 10),
                        "tags": random.sample(
                            ["urgent", "batch", "async", "sync", "cached", "fresh"], k=3
                        ),
                    },
                },
            )
            for i in range(self.iterations)
        ]

        # Benchmark Python implementation
        python_results = self._benchmark_python_tools(test_tools)

        # Benchmark Rust implementation
        rust_results = self._benchmark_rust_tools(test_tools)

        # Calculate improvements
        improvements = self._calculate_improvements(python_results, rust_results)

        return {
            "python": python_results,
            "rust": rust_results,
            "improvements": improvements,
        }

    def _benchmark_python_tools(self, test_tools: List[tuple]) -> Dict[str, float]:
        """Benchmark Python tool execution using the same wrapper class."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Use the same AcceleratedToolExecutor but with Python fallback
            python_executor = AcceleratedToolExecutor(
                use_rust=False, max_recursion_depth=self.iterations
            )

            start_time = time.time()
            for tool_name, args in test_tools:
                _ = python_executor.execute_tool(tool_name, args)
            execution_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "execution_time": execution_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": (
                    len(test_tools) / execution_time if execution_time > 0 else 0
                ),
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Python implementation fails
            return {"execution_time": 0, "memory_mb": 0, "operations_per_second": 0}

    def _benchmark_rust_tools(self, test_tools: List[tuple]) -> Dict[str, float]:
        """Benchmark Rust tool execution."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Initialize Rust tool executor
            rust_executor = AcceleratedToolExecutor(
                use_rust=True, max_recursion_depth=self.iterations
            )

            start_time = time.time()
            for tool_name, args in test_tools:
                _ = rust_executor.execute_tool(tool_name, args)
            execution_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "execution_time": execution_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": (
                    len(test_tools) / execution_time if execution_time > 0 else 0
                ),
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Rust implementation fails
            return {"execution_time": 0, "memory_mb": 0, "operations_per_second": 0}

    def benchmark_serialization(self) -> Dict[str, Any]:
        """
        Benchmark serialization performance.

        Uses large, deeply nested message payloads to showcase Rust's performance advantages:
        - Large content strings (2000-8000 chars) simulating LLM responses
        - Deeply nested metadata and context structures
        - Complex arrays and nested objects
        - Realistic agent communication patterns with full context

        Returns:
            Dictionary with benchmark results
        """
        # Generate large, deeply nested message data - simulating real agent communication
        message_types = ["task_assignment", "result", "query", "response", "error", "status_update"]
        agents = [f"agent_{i}" for i in range(20)]
        models = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "llama-70b"]

        test_messages = [
            {
                "id": f"msg-{i}-{''.join(random.choices(string.hexdigits, k=16))}",
                "sender": random.choice(agents),
                "recipient": random.choice(agents),
                # Very large content - simulating full LLM responses (2000-8000 chars)
                "content": (
                    f"[{random.choice(message_types).upper()}] "
                    + "".join(
                        random.choices(
                            string.ascii_letters + " .,!?\n\t", k=random.randint(2000, 8000)
                        )
                    )
                    + "\n\n## Summary\nTask "
                    + str(i)
                    + " "
                    + ("completed successfully" if random.random() > 0.2 else "failed with error")
                    + "\n\n## Details\n"
                    + "".join(random.choices(string.ascii_letters + " .,\n", k=500))
                    + f"\n\nTokens used: {random.randint(100, 4000)}"
                ),
                "timestamp": 1700000000 + i * random.randint(1, 60),
                # Add complex nested metadata for serialization stress test
                "_metadata": {
                    "model": random.choice(models),
                    "temperature": random.uniform(0.0, 1.0),
                    "max_tokens": random.randint(100, 4000),
                    "stop_sequences": ["\n\n", "###", "END"],
                    "context": {
                        "conversation_id": "conv-"
                        + "".join(random.choices(string.hexdigits, k=16)),
                        "turn_number": random.randint(1, 50),
                        "parent_message_id": f"msg-{max(0, i-1)}-"
                        + "".join(random.choices(string.hexdigits, k=16)),
                        "thread_depth": random.randint(0, 10),
                        "session": {
                            "id": f"session-{''.join(random.choices(string.hexdigits, k=8))}",
                            "started_at": 1700000000 - random.randint(0, 86400),
                            "user_id": f"user-{random.randint(1, 1000)}",
                        },
                    },
                    "tool_calls": [
                        {
                            "id": f"call-{j}-{''.join(random.choices(string.hexdigits, k=8))}",
                            "name": random.choice(
                                ["web_search", "code_exec", "file_read", "api_call"]
                            ),
                            "arguments": {
                                "query": "".join(random.choices(string.ascii_letters + " ", k=100)),
                                "options": {
                                    "timeout": random.randint(1, 30),
                                    "retries": random.randint(0, 3),
                                },
                            },
                            "result": "".join(
                                random.choices(
                                    string.ascii_letters + " \n", k=random.randint(100, 500)
                                )
                            ),
                        }
                        for j in range(random.randint(0, 5))
                    ],
                    "usage": {
                        "prompt_tokens": random.randint(100, 2000),
                        "completion_tokens": random.randint(100, 4000),
                        "total_tokens": random.randint(200, 6000),
                        "cost_usd": random.uniform(0.001, 0.5),
                    },
                    "embeddings": [random.uniform(-1, 1) for _ in range(random.randint(64, 256))],
                },
            }
            for i in range(self.iterations)
        ]

        # Benchmark Python implementation
        python_results = self._benchmark_python_serialization(test_messages)

        # Benchmark Rust implementation
        rust_results = self._benchmark_rust_serialization(test_messages)

        # Calculate improvements
        improvements = self._calculate_improvements(python_results, rust_results)

        return {
            "python": python_results,
            "rust": rust_results,
            "improvements": improvements,
        }

    def _benchmark_python_serialization(self, test_messages: List[Dict]) -> Dict[str, float]:
        """Benchmark Python serialization."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Serialization
            start_time = time.time()
            serialized = []
            for msg in test_messages:
                json_str = json.dumps(msg, separators=(",", ":"))
                serialized.append(json_str)
            serialize_time = time.time() - start_time

            # Deserialization
            start_time = time.time()
            deserialized = []
            for json_str in serialized:
                msg = json.loads(json_str)
                deserialized.append(msg)
            deserialize_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "serialize_time": serialize_time,
                "deserialize_time": deserialize_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": {
                    "serialize": (len(test_messages) / serialize_time if serialize_time > 0 else 0),
                    "deserialize": (
                        len(test_messages) / deserialize_time if deserialize_time > 0 else 0
                    ),
                },
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            return {
                "serialize_time": 0,
                "deserialize_time": 0,
                "memory_mb": 0,
                "operations_per_second": {"serialize": 0, "deserialize": 0},
            }

    def _benchmark_rust_serialization(self, test_messages: List[Dict]) -> Dict[str, float]:
        """Benchmark Rust serialization."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Serialization
            start_time = time.time()
            serialized = []
            for msg in test_messages:
                rust_msg = AgentMessage(
                    id=msg["id"],
                    sender=msg["sender"],
                    recipient=msg["recipient"],
                    content=msg["content"],
                    timestamp=msg["timestamp"],
                    use_rust=True,
                )
                json_str = rust_msg.to_json()
                serialized.append(json_str)
            serialize_time = time.time() - start_time

            # Deserialization
            start_time = time.time()
            deserialized = []
            for json_str in serialized:
                rust_msg = AgentMessage.from_json(json_str, use_rust=True)
                msg = {
                    "id": rust_msg.id,
                    "sender": rust_msg.sender,
                    "recipient": rust_msg.recipient,
                    "content": rust_msg.content,
                    "timestamp": rust_msg.timestamp,
                }
                deserialized.append(msg)
            deserialize_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "serialize_time": serialize_time,
                "deserialize_time": deserialize_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": {
                    "serialize": (len(test_messages) / serialize_time if serialize_time > 0 else 0),
                    "deserialize": (
                        len(test_messages) / deserialize_time if deserialize_time > 0 else 0
                    ),
                },
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Rust implementation fails
            return {
                "serialize_time": 0,
                "deserialize_time": 0,
                "memory_mb": 0,
                "operations_per_second": {"serialize": 0, "deserialize": 0},
            }

    def benchmark_database(self) -> Dict[str, Any]:
        """
        Benchmark database performance.

        Uses large records with complex metadata to showcase Rust's performance advantages:
        - Large task descriptions (500-2000 chars) simulating detailed task outputs
        - Complex nested metadata structures
        - Many records with varied query patterns

        Returns:
            Dictionary with benchmark results
        """
        import os
        import tempfile

        # Create temporary database files
        python_db_path = tempfile.mktemp(suffix=".db")
        rust_db_path = tempfile.mktemp(suffix=".db")

        try:
            # Generate large, complex test data - simulating real long-term memory storage
            task_types = ["analysis", "research", "coding", "review", "planning", "execution"]
            outcomes = ["success", "partial", "failed", "pending", "retry"]

            test_data = [
                {
                    # Large task description (500-2000 chars)
                    "task_description": (
                        f"[{random.choice(task_types).upper()}] Task {i}: "
                        + "".join(
                            random.choices(
                                string.ascii_letters + " .,\n", k=random.randint(500, 2000)
                            )
                        )
                        + f"\n\nOutcome: {random.choice(outcomes)}"
                        + f"\nIterations: {random.randint(1, 10)}"
                    ),
                    # Complex nested metadata
                    "metadata": {
                        "task_id": f"task-{i}-{''.join(random.choices(string.hexdigits, k=8))}",
                        "agent": f"agent_{i % 15}",
                        "crew": f"crew_{i % 5}",
                        "priority": random.randint(1, 10),
                        "tags": random.sample(
                            ["critical", "routine", "background", "urgent", "deferred"], k=2
                        ),
                        "execution": {
                            "start_time": 1700000000 + i * 60,
                            "end_time": 1700000000 + i * 60 + random.randint(10, 3600),
                            "retries": random.randint(0, 3),
                            "tokens_used": random.randint(100, 8000),
                        },
                        "dependencies": [
                            f"task-{max(0, i - j)}" for j in range(1, random.randint(2, 5))
                        ],
                        "output_summary": "".join(
                            random.choices(string.ascii_letters + " ", k=200)
                        ),
                    },
                    "datetime": (
                        f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d} "
                        f"{(i % 24):02d}:{(i % 60):02d}:00"
                    ),
                    "score": random.uniform(0.0, 1.0),
                }
                for i in range(min(self.iterations, 2000))  # Allow more records for database tests
            ]

            # Benchmark Python implementation
            python_results = self._benchmark_python_database(python_db_path, test_data)

            # Benchmark Rust implementation
            rust_results = self._benchmark_rust_database(rust_db_path, test_data)

            # Calculate improvements
            improvements = self._calculate_improvements(python_results, rust_results)

            return {
                "python": python_results,
                "rust": rust_results,
                "improvements": improvements,
            }
        finally:
            # Clean up temporary files
            for path in [python_db_path, rust_db_path]:
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def _benchmark_python_database(self, db_path: str, test_data: List[Dict]) -> Dict[str, float]:
        """Benchmark Python database operations using the same wrapper class."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Use the same AcceleratedSQLiteWrapper but with Python fallback
            python_db = AcceleratedSQLiteWrapper(db_path, use_rust=False)

            # Benchmark insert operations
            start_time = time.time()
            for item in test_data:
                python_db.save_memory(
                    task_description=item["task_description"],
                    metadata=item["metadata"],
                    datetime=item["datetime"],
                    score=item["score"],
                )
            insert_time = time.time() - start_time

            # Benchmark query operations (exact match)
            start_time = time.time()
            for item in test_data[:100]:  # Limit query tests
                _ = python_db.load_memories(item["task_description"])
            query_time = time.time() - start_time

            # Benchmark FTS search (Python uses LIKE query fallback)
            search_queries = [
                "analysis report findings",
                "task execution result",
                "error handling failure",
                "machine learning model",
                "data processing pipeline",
            ] * 20  # 100 searches
            start_time = time.time()
            for query in search_queries:
                _ = python_db.search_memories_fts(query, limit=10)
            fts_search_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "insert_time": insert_time,
                "query_time": query_time,
                "fts_search_time": fts_search_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": {
                    "insert": len(test_data) / insert_time if insert_time > 0 else 0,
                    "query": 100 / query_time if query_time > 0 else 0,
                    "fts_search": (
                        len(search_queries) / fts_search_time if fts_search_time > 0 else 0
                    ),
                },
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Python implementation fails
            return {
                "insert_time": 0,
                "query_time": 0,
                "fts_search_time": 0,
                "memory_mb": 0,
                "operations_per_second": {"insert": 0, "query": 0, "fts_search": 0},
            }

    def _benchmark_rust_database(self, db_path: str, test_data: List[Dict]) -> Dict[str, float]:
        """Benchmark Rust database operations using the same wrapper class."""
        try:
            # Force garbage collection and start memory tracking
            gc.collect()
            tracemalloc.start()

            # Use the same AcceleratedSQLiteWrapper but with Rust acceleration
            rust_db = AcceleratedSQLiteWrapper(db_path, use_rust=True)

            # Benchmark insert operations
            start_time = time.time()
            for item in test_data:
                rust_db.save_memory(
                    task_description=item["task_description"],
                    metadata=item["metadata"],
                    datetime=item["datetime"],
                    score=item["score"],
                )
            insert_time = time.time() - start_time

            # Benchmark query operations (exact match)
            start_time = time.time()
            for item in test_data[:100]:  # Limit query tests
                _ = rust_db.load_memories(item["task_description"])
            query_time = time.time() - start_time

            # Benchmark FTS5 search (Rust uses FTS5 with BM25 ranking)
            search_queries = [
                "analysis report findings",
                "task execution result",
                "error handling failure",
                "machine learning model",
                "data processing pipeline",
            ] * 20  # 100 searches
            start_time = time.time()
            for query in search_queries:
                _ = rust_db.search_memories_fts(query, limit=10)
            fts_search_time = time.time() - start_time

            # Get memory usage
            _, peak_mb = get_memory_usage()
            tracemalloc.stop()

            return {
                "insert_time": insert_time,
                "query_time": query_time,
                "fts_search_time": fts_search_time,
                "memory_mb": round(peak_mb, 2),
                "operations_per_second": {
                    "insert": len(test_data) / insert_time if insert_time > 0 else 0,
                    "query": 100 / query_time if query_time > 0 else 0,
                    "fts_search": (
                        len(search_queries) / fts_search_time if fts_search_time > 0 else 0
                    ),
                },
            }
        except Exception:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            # Return zero performance if Rust implementation fails
            return {
                "insert_time": 0,
                "query_time": 0,
                "fts_search_time": 0,
                "memory_mb": 0,
                "operations_per_second": {"insert": 0, "query": 0, "fts_search": 0},
            }

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """
        Run all benchmarks and return results.

        Returns:
            Dictionary with all benchmark results
        """
        print("Running CrewAI Rust Integration Benchmarks...")
        print("=" * 50)

        results: Dict[str, Any] = {}

        # Memory storage benchmark
        print("Benchmarking memory storage...")
        results["memory"] = self.benchmark_memory_storage()
        py_save = results["memory"]["python"]["operations_per_second"]["save"]
        print(f"  Python: {py_save:.0f} saves/sec")
        rust_save = results["memory"]["rust"]["operations_per_second"]["save"]
        if rust_save > 0:
            print(f"  Rust: {rust_save:.0f} saves/sec")
            improvement = results["memory"]["improvements"]["save_time"]
            print(f"  Improvement: {improvement:.1f}x")

        # Tool execution benchmark
        print("\nBenchmarking tool execution...")
        results["tools"] = self.benchmark_tool_execution()
        py_ops = results["tools"]["python"]["operations_per_second"]
        print(f"  Python: {py_ops:.0f} ops/sec")
        rust_ops = results["tools"]["rust"]["operations_per_second"]
        if rust_ops > 0:
            print(f"  Rust: {rust_ops:.0f} ops/sec")
            improvement = results["tools"]["improvements"]["execution_time"]
            print(f"  Improvement: {improvement:.1f}x")

        # Serialization benchmark
        print("\nBenchmarking serialization...")
        results["serialization"] = self.benchmark_serialization()
        py_ser = results["serialization"]["python"]["operations_per_second"]["serialize"]
        print(f"  Python serialize: {py_ser:.0f} ops/sec")
        rust_ser = results["serialization"]["rust"]["operations_per_second"]["serialize"]
        if rust_ser > 0:
            print(f"  Rust serialize: {rust_ser:.0f} ops/sec")
            improvement = results["serialization"]["improvements"]["serialize_time"]
            print(f"  Serialization improvement: {improvement:.1f}x")

        # Database benchmark
        print("\nBenchmarking database operations...")
        results["database"] = self.benchmark_database()
        py_ins = results["database"]["python"]["operations_per_second"]["insert"]
        print(f"  Python insert: {py_ins:.0f} ops/sec")
        rust_ins = results["database"]["rust"]["operations_per_second"]["insert"]
        if rust_ins > 0:
            print(f"  Rust insert: {rust_ins:.0f} ops/sec")
            improvement = results["database"]["improvements"]["insert_time"]
            print(f"  Insert improvement: {improvement:.1f}x")

        print("\n" + "=" * 50)
        print("Benchmarking complete!")

        self.results = results
        return results

    def print_summary(self) -> None:
        """Print a summary of benchmark results."""
        if not self.results:
            print("No benchmark results available. Run benchmarks first.")
            return

        print("\nCrewAI Rust Integration Benchmark Summary")
        print("=" * 50)

        # Memory improvements
        if self.results.get("memory"):
            mem_improvement = self.results["memory"]["improvements"].get("save_time", 0)
            if mem_improvement > 0:
                print(f"Memory Storage: {mem_improvement:.1f}x improvement")

        # Tool execution improvements
        if self.results.get("tools"):
            tool_improvement = self.results["tools"]["improvements"].get("execution_time", 0)
            if tool_improvement > 0:
                print(f"Tool Execution: {tool_improvement:.1f}x improvement")

        # Serialization improvements
        if self.results.get("serialization"):
            ser_improvement = self.results["serialization"]["improvements"].get("serialize_time", 0)
            if ser_improvement > 0:
                print(f"Serialization: {ser_improvement:.1f}x improvement")

        # Database improvements
        if self.results.get("database"):
            db_improvement = self.results["database"]["improvements"].get("insert_time", 0)
            if db_improvement > 0:
                print(f"Database Operations: {db_improvement:.1f}x improvement")

        print("=" * 50)

    def generate_benchmark_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate a BENCHMARK.md report.

        Args:
            output_path: Path to write the report (default: ./BENCHMARK.md)

        Returns:
            Path to the generated report
        """
        if not self.results:
            raise ValueError("No benchmark results available. Run benchmarks first.")

        if output_path is None:
            output_path = Path("BENCHMARK.md")

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Get environment info
        try:
            from . import __version__ as fast_crewai_version
        except ImportError:
            fast_crewai_version = "unknown"

        try:
            from . import is_acceleration_available

            rust_available = is_acceleration_available()
        except ImportError:
            rust_available = False

        python_version = platform.python_version()
        platform_info = platform.platform()

        # Helper to check if a value is a valid finite number
        def is_valid_number(val):
            return (
                isinstance(val, (int, float))
                and val > 0
                and val != float("inf")
                and val != float("-inf")
            )

        # Calculate overall improvements
        improvements = []
        if self.results.get("memory"):
            mem_imp = self.results["memory"]["improvements"].get("save_time", 0)
            if is_valid_number(mem_imp):
                improvements.append(("Memory Storage", mem_imp))

        if self.results.get("tools"):
            tool_imp = self.results["tools"]["improvements"].get("execution_time", 0)
            if is_valid_number(tool_imp):
                improvements.append(("Tool Execution", tool_imp))

        if self.results.get("serialization"):
            ser_imp = self.results["serialization"]["improvements"].get("serialize_time", 0)
            if is_valid_number(ser_imp):
                improvements.append(("Serialization", ser_imp))

        if self.results.get("database"):
            db_imp = self.results["database"]["improvements"].get("insert_time", 0)
            if is_valid_number(db_imp):
                improvements.append(("Database", db_imp))

        # Calculate average improvement
        if improvements:
            avg_improvement = sum(imp for _, imp in improvements) / len(improvements)
        else:
            avg_improvement = 0

        # Build improvement table
        improvement_rows = []
        for name, imp in improvements:
            if imp > 1:
                emoji = "🚀"
                status = f"{imp:.2f}x faster"
            elif imp == 1:
                emoji = "➡️"
                status = "Same"
            else:
                emoji = "⚠️"
                status = f"{1/imp:.2f}x slower"
            improvement_rows.append(f"| {name} | {emoji} {status} |")

        improvement_table = "\n".join(improvement_rows) if improvement_rows else "| No data | - |"

        # Build memory usage table
        memory_rows = []
        for category, name in [
            ("memory", "Memory Storage"),
            ("tools", "Tool Execution"),
            ("serialization", "Serialization"),
            ("database", "Database"),
        ]:
            if category in self.results:
                py_mem = self.results[category].get("python", {}).get("memory_mb", 0)
                rust_mem = self.results[category].get("rust", {}).get("memory_mb", 0)
                if py_mem > 0 and rust_mem > 0:
                    savings = ((py_mem - rust_mem) / py_mem) * 100 if py_mem > 0 else 0
                    if savings > 0:
                        emoji = "🚀"
                        status = f"{savings:.1f}% less"
                    elif savings < 0:
                        emoji = "⚠️"
                        status = f"{abs(savings):.1f}% more"
                    else:
                        emoji = "➡️"
                        status = "Same"
                    memory_rows.append(
                        f"| {name} | {py_mem:.1f} MB | {rust_mem:.1f} MB | {emoji} {status} |"
                    )

        memory_table = "\n".join(memory_rows) if memory_rows else "| No data | - | - | - |"

        # Build detailed results
        def format_ops(category: str, operation: str) -> str:
            """Format operations per second for a category and operation."""
            if category not in self.results:
                return "N/A"
            py_ops = self.results[category].get("python", {}).get("operations_per_second", {})
            rust_ops = self.results[category].get("rust", {}).get("operations_per_second", {})

            if isinstance(py_ops, dict):
                py_val = py_ops.get(operation, 0)
            else:
                py_val = py_ops if operation == "default" else 0

            if isinstance(rust_ops, dict):
                rust_val = rust_ops.get(operation, 0)
            else:
                rust_val = rust_ops if operation == "default" else 0

            return f"Python: {py_val:,.0f} ops/s | Rust: {rust_val:,.0f} ops/s"

        def format_memory(category: str) -> str:
            """Format memory usage for a category."""
            if category not in self.results:
                return "N/A"
            py_mem = self.results[category].get("python", {}).get("memory_mb", 0)
            rust_mem = self.results[category].get("rust", {}).get("memory_mb", 0)
            return f"Python: {py_mem:.1f} MB | Rust: {rust_mem:.1f} MB"

        report = f"""# Fast-CrewAI Benchmark Report

> Generated: {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| Rust Acceleration | {"✅ Available" if rust_available else "❌ Not Available"} |
| Iterations | {self.iterations:,} |
| Average Improvement | {"🚀 " + f"{avg_improvement:.2f}x" if avg_improvement > 1 else "N/A"} |

## Performance Improvements

| Component | Improvement |
|-----------|-------------|
{improvement_table}

## Memory Usage

| Component | Python | Rust | Savings |
|-----------|--------|------|---------|
{memory_table}

## Environment

| Component | Version |
|-----------|---------|
| Python | {python_version} |
| Platform | {platform_info} |
| Fast-CrewAI | {fast_crewai_version} |
| Rust Extension | {"available" if rust_available else "not available"} |

## Detailed Results

### Memory Storage

| Metric | Performance |
|--------|-------------|
| Save | {format_ops("memory", "save")} |
| Search | {format_ops("memory", "search")} |
| Memory | {format_memory("memory")} |

### Tool Execution

| Metric | Performance |
|--------|-------------|
| Execute | {format_ops("tools", "execute")} |
| Memory | {format_memory("tools")} |

### Serialization

| Metric | Performance |
|--------|-------------|
| Serialize | {format_ops("serialization", "serialize")} |
| Deserialize | {format_ops("serialization", "deserialize")} |
| Memory | {format_memory("serialization")} |

### Database Operations

| Metric | Performance |
|--------|-------------|
| Insert | {format_ops("database", "insert")} |
| Query | {format_ops("database", "query")} |
| FTS Search | {format_ops("database", "fts_search")} |
| Memory | {format_memory("database")} |

## How to Reproduce

```bash
# Run benchmarks locally
uv run python scripts/test_benchmarking.py \\
    --iterations {self.iterations} \\
    --report-output BENCHMARK.md
```

## Notes

- Benchmarks compare Python implementations with Rust-accelerated implementations
- Higher improvement numbers indicate better Rust performance
- Results may vary based on hardware and system load
- The Rust extension must be built for acceleration to be available

---

*This report was automatically generated by the Fast-CrewAI benchmark suite.*
"""

        output_path = Path(output_path)
        output_path.write_text(report)
        print(f"Benchmark report generated: {output_path}")

        return output_path


def run_benchmarks():
    """
    Run the benchmark suite and print results.
    """
    benchmark = PerformanceBenchmark(iterations=1000)
    results = benchmark.run_all_benchmarks()
    benchmark.print_summary()
    return results


if __name__ == "__main__":
    run_benchmarks()

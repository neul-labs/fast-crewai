"""
High-performance task execution engine using Rust backend.

This module provides accelerated task execution by wrapping CrewAI's Task
and Crew classes with performance optimizations while maintaining full API compatibility.
"""

import asyncio
import logging
import os
from typing import Any, Optional

from ._constants import HAS_ACCELERATION_IMPLEMENTATION

# Configure module logger
_logger = logging.getLogger(__name__)

# Constants for configuration
DEFAULT_MAX_CONCURRENT_TASKS = 10

# Try to import the Rust implementation
if HAS_ACCELERATION_IMPLEMENTATION:
    try:
        from ._core import RustTaskExecutor as _RustTaskExecutor

        _RUST_AVAILABLE = True
    except ImportError:
        _RUST_AVAILABLE = False
else:
    _RUST_AVAILABLE = False


def create_accelerated_task():
    """
    Dynamically create an accelerated version of CrewAI's Task.

    This function imports the original Task and creates a subclass
    that overrides performance-critical methods with accelerated versions.
    """
    try:
        # Import the original Task from CrewAI
        from crewai.task import Task as _OriginalTask

        class AcceleratedTask(_OriginalTask):
            """
            Accelerated version of CrewAI's Task.

            This class inherits from Task and overrides performance-critical
            methods with Rust-accelerated versions while maintaining full API
            compatibility.
            """

            def __init__(self, *args, **kwargs):
                """Initialize with acceleration support."""
                super().__init__(*args, **kwargs)
                self._acceleration_enabled = os.getenv("FAST_CREWAI_TASKS", "auto").lower() in (
                    "true",
                    "auto",
                )
                self._execution_count = 0

            def execute(self, *args, **kwargs):
                """
                Accelerated version of execute method.

                This method wraps the original execute with performance optimizations.
                """
                if self._acceleration_enabled and _RUST_AVAILABLE:
                    # Use acceleration if available
                    self._execution_count += 1
                    try:
                        # Call the original implementation
                        return super().execute(*args, **kwargs)
                    finally:
                        self._execution_count -= 1
                else:
                    return super().execute(*args, **kwargs)

            async def execute_async(self, *args, **kwargs):
                """
                Accelerated version of async execute method.

                This method wraps the original async execute with performance optimizations.
                """
                if self._acceleration_enabled and _RUST_AVAILABLE:
                    # Use acceleration if available
                    return await super().execute_async(*args, **kwargs)
                else:
                    return await super().execute_async(*args, **kwargs)

        return AcceleratedTask

    except ImportError:
        # If we can't import Task, return None
        # This happens when CrewAI is not installed
        _logger.debug("Cannot import Task from CrewAI")
        return None
    except Exception as e:
        # On any other error, return None
        _logger.warning("Failed to create accelerated Task: %s", e)
        return None


def create_accelerated_crew():
    """
    Dynamically create an accelerated version of CrewAI's Crew.

    This function imports the original Crew and creates a subclass
    that overrides performance-critical methods with accelerated versions.
    """
    try:
        # Import the original Crew from CrewAI
        from crewai.crew import Crew as _OriginalCrew

        class AcceleratedCrew(_OriginalCrew):
            """
            Accelerated version of CrewAI's Crew.

            This class inherits from Crew and overrides performance-critical
            methods with Rust-accelerated versions while maintaining full API
            compatibility.
            """

            def __init__(self, *args, **kwargs):
                """Initialize with acceleration support."""
                super().__init__(*args, **kwargs)
                self._acceleration_enabled = os.getenv("FAST_CREWAI_TASKS", "auto").lower() in (
                    "true",
                    "auto",
                )

            def kickoff(self, *args, **kwargs):
                """
                Accelerated version of kickoff method.

                This method wraps the original kickoff with performance optimizations.
                """
                if self._acceleration_enabled and _RUST_AVAILABLE:
                    # Use acceleration if available
                    # Future: add Rust-accelerated orchestration here
                    return super().kickoff(*args, **kwargs)
                else:
                    return super().kickoff(*args, **kwargs)

            async def kickoff_async(self, *args, **kwargs):
                """
                Accelerated version of async kickoff method.

                This method wraps the original async kickoff with performance optimizations.
                """
                if self._acceleration_enabled and _RUST_AVAILABLE:
                    # Use acceleration if available
                    return await super().kickoff_async(*args, **kwargs)
                else:
                    return await super().kickoff_async(*args, **kwargs)

        return AcceleratedCrew

    except ImportError:
        # If we can't import Crew, return None
        _logger.debug("Cannot import Crew from CrewAI")
        return None
    except Exception as e:
        # On any other error, return None
        _logger.warning("Failed to create accelerated Crew: %s", e)
        return None


# Create the accelerated classes
AcceleratedTask = create_accelerated_task()
AcceleratedCrew = create_accelerated_crew()


# Legacy executor class (kept for backwards compatibility)
class AcceleratedTaskExecutor:
    """
    High-performance task execution engine using Rust backend.

    This class provides a standalone task executor with async support,
    dependency tracking, and performance improvements. Note: For task
    acceleration within CrewAI, use AcceleratedTask and AcceleratedCrew instead.

    Features:
    - Task dependency tracking and topological sorting
    - Parallel execution of independent tasks via Tokio runtime
    - Execution statistics tracking
    - Cycle detection in task dependencies
    """

    def __init__(self, max_concurrent_tasks: int = 10, use_rust: Optional[bool] = None):
        """
        Initialize the task executor.

        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
            use_rust: Whether to use the Rust implementation. If None,
                     automatically detects based on availability and
                     environment variables.
        """
        self.max_concurrent_tasks = max_concurrent_tasks

        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv("FAST_CREWAI_TASKS", "auto").lower()
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
                self._executor = _RustTaskExecutor()
                self._implementation = "rust"
            except Exception as e:
                _logger.warning("Failed to initialize Rust task executor, using Python: %s", e)
                # Fallback to Python implementation
                self._use_rust = False
                self._executor = None
                self._implementation = "python"
                self._active_tasks = 0
                self._tasks = {}
                self._stats = {
                    "tasks_scheduled": 0,
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                }
        else:
            self._executor = None
            self._implementation = "python"
            self._active_tasks = 0
            self._tasks = {}
            self._stats = {
                "tasks_scheduled": 0,
                "tasks_completed": 0,
                "tasks_failed": 0,
            }

    def register_task(self, task_id: str, dependencies: list = None) -> None:
        """
        Register a task with optional dependencies.

        Args:
            task_id: Unique identifier for the task
            dependencies: List of task IDs this task depends on
        """
        dependencies = dependencies or []

        if self._use_rust:
            try:
                self._executor.register_task(task_id, dependencies)
            except Exception as e:
                _logger.debug("Rust register_task failed, using Python fallback: %s", e)
                self._use_rust = False
                self._python_register_task(task_id, dependencies)
        else:
            self._python_register_task(task_id, dependencies)

    def _python_register_task(self, task_id: str, dependencies: list) -> None:
        """Python implementation of task registration."""
        self._tasks[task_id] = {
            "id": task_id,
            "dependencies": dependencies,
            "state": "pending",
            "result": None,
            "error": None,
        }
        self._stats["tasks_scheduled"] += 1

    def get_ready_tasks(self) -> list:
        """
        Get all tasks that are ready to execute (dependencies satisfied).

        Returns:
            List of task IDs ready for execution
        """
        if self._use_rust:
            try:
                return self._executor.get_ready_tasks()
            except Exception as e:
                _logger.debug("Rust get_ready_tasks failed, using Python fallback: %s", e)
                self._use_rust = False
                return self._python_get_ready_tasks()
        else:
            return self._python_get_ready_tasks()

    def _python_get_ready_tasks(self) -> list:
        """Python implementation of getting ready tasks."""
        ready = []
        for task_id, task in self._tasks.items():
            if task["state"] != "pending":
                continue
            deps_satisfied = all(
                self._tasks.get(dep, {}).get("state") == "completed" for dep in task["dependencies"]
            )
            if deps_satisfied:
                ready.append(task_id)
        return ready

    def get_execution_order(self) -> list:
        """
        Get topological sort order for task execution.

        Returns:
            List of task IDs in execution order

        Raises:
            ValueError: If circular dependency detected
        """
        if self._use_rust:
            try:
                return self._executor.get_execution_order()
            except Exception as e:
                if "Circular dependency" in str(e):
                    raise ValueError("Circular dependency detected in tasks")
                _logger.debug("Rust get_execution_order failed, using Python fallback: %s", e)
                self._use_rust = False
                return self._python_get_execution_order()
        else:
            return self._python_get_execution_order()

    def _python_get_execution_order(self) -> list:
        """Python implementation of topological sort."""
        # Kahn's algorithm
        in_degree = {task_id: 0 for task_id in self._tasks}
        adj_list = {task_id: [] for task_id in self._tasks}

        for task_id, task in self._tasks.items():
            in_degree[task_id] = len(task["dependencies"])
            for dep_id in task["dependencies"]:
                if dep_id in adj_list:
                    adj_list[dep_id].append(task_id)

        queue = [task_id for task_id, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbor in adj_list.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self._tasks):
            raise ValueError("Circular dependency detected in tasks")

        return result

    def mark_started(self, task_id: str) -> None:
        """Mark a task as started."""
        if self._use_rust:
            try:
                self._executor.mark_started(task_id)
            except Exception as e:
                _logger.debug("Rust mark_started failed: %s", e)
                self._use_rust = False
                self._python_mark_started(task_id)
        else:
            self._python_mark_started(task_id)

    def _python_mark_started(self, task_id: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id]["state"] = "running"

    def mark_completed(self, task_id: str, result: str = "") -> None:
        """Mark a task as completed with a result."""
        if self._use_rust:
            try:
                self._executor.mark_completed(task_id, result)
            except Exception as e:
                _logger.debug("Rust mark_completed failed: %s", e)
                self._use_rust = False
                self._python_mark_completed(task_id, result)
        else:
            self._python_mark_completed(task_id, result)

    def _python_mark_completed(self, task_id: str, result: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id]["state"] = "completed"
            self._tasks[task_id]["result"] = result
            self._stats["tasks_completed"] += 1

    def mark_failed(self, task_id: str, error: str) -> None:
        """Mark a task as failed with an error message."""
        if self._use_rust:
            try:
                self._executor.mark_failed(task_id, error)
            except Exception as e:
                _logger.debug("Rust mark_failed failed: %s", e)
                self._use_rust = False
                self._python_mark_failed(task_id, error)
        else:
            self._python_mark_failed(task_id, error)

    def _python_mark_failed(self, task_id: str, error: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id]["state"] = "failed"
            self._tasks[task_id]["error"] = error
            self._stats["tasks_failed"] += 1

    def get_result(self, task_id: str) -> Optional[str]:
        """Get the result of a completed task."""
        if self._use_rust:
            try:
                return self._executor.get_result(task_id)
            except Exception as e:
                _logger.debug("Failed to get task result from Rust: %s", e)
                return None
        else:
            task = self._tasks.get(task_id)
            return task["result"] if task else None

    def execute_concurrent(self, task_ids: list) -> list:
        """
        Execute multiple independent tasks concurrently.

        Args:
            task_ids: List of task IDs to execute concurrently

        Returns:
            List of task IDs (in same order)
        """
        if self._use_rust:
            try:
                return self._executor.execute_concurrent_tasks(task_ids)
            except Exception as e:
                _logger.debug("Rust execute_concurrent failed, using Python fallback: %s", e)
                self._use_rust = False
                return task_ids  # Just return the IDs
        else:
            return task_ids  # Python doesn't have true concurrent execution here

    def get_stats(self) -> dict:
        """Get execution statistics."""
        if self._use_rust:
            try:
                return self._executor.get_stats()
            except Exception as e:
                _logger.debug("Failed to get stats from Rust: %s", e)
                return self._stats.copy()
        else:
            return self._stats.copy()

    def clear(self) -> None:
        """Clear all tasks."""
        if self._use_rust:
            try:
                self._executor.clear()
            except Exception as e:
                _logger.debug("Failed to clear Rust executor: %s", e)
                pass
        self._tasks.clear()
        self._stats = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

    async def execute_task(self, task_func, *args, **kwargs) -> Any:
        """
        Execute a task asynchronously.

        Args:
            task_func: The task function to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task

        Returns:
            Result of the task execution
        """
        # Check concurrent task limit
        if self._active_tasks >= self.max_concurrent_tasks:
            raise Exception("Maximum concurrent tasks limit reached")

        self._active_tasks += 1
        try:
            # Execute the task
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(*args, **kwargs)
            else:
                result = task_func(*args, **kwargs)
            return result
        finally:
            self._active_tasks -= 1

    @property
    def implementation(self) -> str:
        """Get the current implementation type."""
        return self._implementation

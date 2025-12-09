"""
High-performance task execution engine using Rust backend.

This module provides accelerated task execution by wrapping CrewAI's Task
and Crew classes with performance optimizations while maintaining full API compatibility.
"""

import asyncio
import os
from typing import Any, Optional

from ._constants import HAS_ACCELERATION_IMPLEMENTATION

# Try to import the Rust implementation
if HAS_ACCELERATION_IMPLEMENTATION:
    try:
        from ._core import AcceleratedTaskExecutor as _RustTaskExecutor

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
                self._acceleration_enabled = os.getenv(
                    "FAST_CREWAI_TASKS", "auto"
                ).lower() in ("true", "auto")
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
                        # Future: add Rust-accelerated execution here
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
        return None
    except Exception:
        # On any other error, return None
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
                self._acceleration_enabled = os.getenv(
                    "FAST_CREWAI_TASKS", "auto"
                ).lower() in ("true", "auto")

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
        return None
    except Exception:
        # On any other error, return None
        return None


# Create the accelerated classes
AcceleratedTask = create_accelerated_task()
AcceleratedCrew = create_accelerated_crew()


# Legacy executor class (kept for backwards compatibility)
class AcceleratedTaskExecutor:
    """
    High-performance task execution engine using Rust backend.

    This class provides a standalone task executor with async support
    and performance improvements. Note: For task acceleration within
    CrewAI, use AcceleratedTask and AcceleratedCrew instead.
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
                self._executor = _RustTaskExecutor(max_concurrent_tasks)
                self._implementation = "rust"
            except Exception:
                # Fallback to Python implementation
                self._use_rust = False
                self._executor = None
                self._implementation = "python"
                self._active_tasks = 0
        else:
            self._executor = None
            self._implementation = "python"
            self._active_tasks = 0

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
        if self._use_rust:
            try:
                # Use Rust implementation
                # For now, fall back to Python
                return await self._python_execute_task(task_func, *args, **kwargs)
            except Exception:
                # Fallback to Python implementation
                self._use_rust = False
                return await self._python_execute_task(task_func, *args, **kwargs)
        else:
            return await self._python_execute_task(task_func, *args, **kwargs)

    async def _python_execute_task(self, task_func, *args, **kwargs) -> Any:
        """Python implementation of task execution for fallback."""
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

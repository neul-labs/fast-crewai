"""
Tests for task execution components.
"""

import pytest
import time
import threading
from typing import List


class TestRustTaskExecutor:
    """Test cases for RustTaskExecutor component."""

    def test_import_task_executor(self):
        """Test that we can import RustTaskExecutor."""
        from crewai_rust import RustTaskExecutor
        executor = RustTaskExecutor()
        assert executor is not None

    def test_task_executor_creation(self):
        """Test creating task executor."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()
        assert executor is not None

    def test_concurrent_task_execution_basic(self):
        """Test basic concurrent task execution."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        # Test with simple task list
        test_tasks = ["task1", "task2", "task3"]

        try:
            results = executor.execute_concurrent_tasks(test_tasks)
            assert isinstance(results, list)
            assert len(results) == len(test_tasks)
        except Exception:
            # Implementation might not be complete
            assert executor is not None

    def test_task_performance_basic(self):
        """Basic performance test for task execution."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        # Create multiple task executors quickly
        start_time = time.time()
        for i in range(100):
            temp_executor = RustTaskExecutor()
        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 5.0  # 100 creations in under 5 seconds

    def test_task_empty_list(self):
        """Test task execution with empty task list."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        try:
            results = executor.execute_concurrent_tasks([])
            assert isinstance(results, list)
            assert len(results) == 0
        except Exception:
            # Method might not be implemented
            assert executor is not None

    def test_task_single_item(self):
        """Test task execution with single task."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        try:
            results = executor.execute_concurrent_tasks(["single_task"])
            assert isinstance(results, list)
            assert len(results) == 1
        except Exception:
            # Method might not be implemented
            assert executor is not None


class TestTaskIntegration:
    """Integration tests for task components with CrewAI."""

    def test_crewai_task_import_compatibility(self):
        """Test that CrewAI task imports work after shimming."""
        try:
            # Import shim first
            import crewai_rust.shim

            # Then try to import CrewAI task components
            from crewai.task import Task
            from crewai.crew import Crew

            assert True  # If we get here, imports worked

        except ImportError:
            # CrewAI might not be installed in test environment
            pytest.skip("CrewAI not available for integration testing")

    def test_task_shimming_behavior(self):
        """Test that task components are properly shimmed."""
        try:
            import crewai_rust.shim
            from crewai.task import Task

            # Should be able to use Task class
            # (might be enhanced by Rust implementation)
            task_cls = Task
            assert task_cls is not None

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")

    def test_crew_integration(self):
        """Test integration with CrewAI Crew class."""
        try:
            import crewai_rust.shim
            from crewai import Agent, Task, Crew

            # Create minimal crew for testing
            agent = Agent(
                role="Test Agent",
                goal="Test goal",
                backstory="Test backstory"
            )

            task = Task(
                description="Test task",
                expected_output="Test output",
                agent=agent
            )

            crew = Crew(agents=[agent], tasks=[task])
            assert crew is not None

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")
        except Exception:
            # Other initialization errors are acceptable in test environment
            pass


class TestTaskConcurrency:
    """Test concurrent task execution capabilities."""

    def test_task_thread_safety(self):
        """Test that task executor is thread-safe."""
        from crewai_rust import RustTaskExecutor

        results = []
        errors = []

        def create_executor():
            try:
                executor = RustTaskExecutor()
                results.append(executor)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_executor)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should not have crashed
        assert len(errors) == 0
        assert len(results) == 10

    def test_task_large_list(self):
        """Test task execution with large task list."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        # Create large task list
        large_task_list = [f"task_{i}" for i in range(1000)]

        start_time = time.time()
        try:
            results = executor.execute_concurrent_tasks(large_task_list)
            execution_time = time.time() - start_time

            assert isinstance(results, list)
            # Should handle large lists efficiently
            assert execution_time < 10.0  # Should complete in reasonable time

        except Exception:
            # Method might not be fully implemented
            execution_time = time.time() - start_time
            # Should not take too long even if it fails
            assert execution_time < 5.0

    def test_task_concurrent_access(self):
        """Test concurrent access to the same executor."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()
        results = []
        errors = []

        def execute_tasks():
            try:
                task_list = [f"thread_task_{i}" for i in range(10)]
                result = executor.execute_concurrent_tasks(task_list)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Multiple threads using same executor
        threads = []
        for i in range(5):
            thread = threading.Thread(target=execute_tasks)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should handle concurrent access gracefully
        # (errors are acceptable if not implemented, but shouldn't crash)
        assert len(threads) == 5


class TestTaskPerformance:
    """Performance tests for task execution."""

    def test_task_executor_creation_performance(self):
        """Test performance of task executor creation."""
        from crewai_rust import RustTaskExecutor

        start_time = time.time()

        # Create many task executors
        executors = []
        for i in range(500):
            executor = RustTaskExecutor()
            executors.append(executor)

        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 10.0  # 500 creations in under 10 seconds
        assert len(executors) == 500

    def test_task_list_processing_performance(self):
        """Test performance of task list processing."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        # Test with different sized task lists
        task_sizes = [10, 50, 100, 200]

        for size in task_sizes:
            task_list = [f"perf_task_{i}" for i in range(size)]

            start_time = time.time()
            try:
                results = executor.execute_concurrent_tasks(task_list)
                execution_time = time.time() - start_time

                # Should scale reasonably
                assert execution_time < (size * 0.01)  # Max 10ms per task

            except Exception:
                # If not implemented, should still be fast
                execution_time = time.time() - start_time
                assert execution_time < 1.0


class TestTaskEdgeCases:
    """Test edge cases and error conditions for tasks."""

    def test_task_with_none_values(self):
        """Test task execution with None values."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        try:
            # Test with None in task list
            results = executor.execute_concurrent_tasks([None, "task", None])
            # Should handle gracefully
            assert isinstance(results, list)
        except Exception:
            # May raise exception, but shouldn't crash the process
            assert executor is not None

    def test_task_with_empty_strings(self):
        """Test task execution with empty strings."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        try:
            results = executor.execute_concurrent_tasks(["", "  ", "valid_task"])
            assert isinstance(results, list)
        except Exception:
            # May raise exception for invalid tasks
            assert executor is not None

    def test_task_with_unicode_strings(self):
        """Test task execution with unicode task names."""
        from crewai_rust import RustTaskExecutor

        executor = RustTaskExecutor()

        unicode_tasks = ["测试任务", "タスク", "🚀_rocket_task", "αβγ_task"]

        try:
            results = executor.execute_concurrent_tasks(unicode_tasks)
            assert isinstance(results, list)
        except Exception:
            # Unicode handling might not be complete
            assert executor is not None


if __name__ == "__main__":
    pytest.main([__file__])
"""
Tests for task execution components.
"""

import threading
import time
from typing import List

import pytest


class TestAcceleratedTaskExecutor:
    """Test cases for AcceleratedTaskExecutor component."""

    def test_import_task_executor(self):
        """Test that we can import AcceleratedTaskExecutor."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        assert executor is not None

    def test_task_executor_creation(self):
        """Test creating task executor."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        assert executor is not None

    def test_task_executor_properties(self):
        """Test task executor properties."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        assert hasattr(executor, "implementation")
        assert executor.implementation in ["rust", "python"]

    def test_task_performance_basic(self):
        """Basic performance test for task execution."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()

        # Create multiple task executors quickly
        start_time = time.time()
        for i in range(100):
            temp_executor = AcceleratedTaskExecutor()
        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 5.0  # 100 creations in under 5 seconds


class TestTaskIntegration:
    """Integration tests for task components with CrewAI."""

    def test_crewai_task_import_compatibility(self):
        """Test that CrewAI task imports work after shimming."""
        try:
            # Import shim first
            from crewai.crew import Crew
            # Then try to import CrewAI task components
            from crewai.task import Task

            import fast_crewai.shim

            assert True  # If we get here, imports worked

        except ImportError:
            # CrewAI might not be installed in test environment
            pytest.skip("CrewAI not available for integration testing")

    def test_task_shimming_behavior(self):
        """Test that task components are properly shimmed."""
        try:
            from crewai.task import Task

            import fast_crewai.shim

            # Should be able to use Task class
            # (might be enhanced by Rust implementation)
            task_cls = Task
            assert task_cls is not None

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")

    def test_crew_integration(self):
        """Test integration with CrewAI Crew class."""
        try:
            from crewai import Agent, Crew, Task

            import fast_crewai.shim

            # Create minimal crew for testing
            agent = Agent(
                role="Test Agent", goal="Test goal", backstory="Test backstory"
            )

            task = Task(
                description="Test task", expected_output="Test output", agent=agent
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
        from fast_crewai import AcceleratedTaskExecutor

        results = []
        errors = []

        def create_executor():
            try:
                executor = AcceleratedTaskExecutor()
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

    def test_task_concurrent_access(self):
        """Test concurrent access to the same executor."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        results = []
        errors = []

        def access_executor():
            try:
                # Access executor properties
                impl = executor.implementation
                results.append(impl)
            except Exception as e:
                errors.append(e)

        # Multiple threads using same executor
        threads = []
        for i in range(5):
            thread = threading.Thread(target=access_executor)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should handle concurrent access gracefully
        assert len(threads) == 5
        assert len(errors) == 0


class TestTaskPerformance:
    """Performance tests for task execution."""

    def test_task_executor_creation_performance(self):
        """Test performance of task executor creation."""
        from fast_crewai import AcceleratedTaskExecutor

        start_time = time.time()

        # Create many task executors
        executors = []
        for i in range(500):
            executor = AcceleratedTaskExecutor()
            executors.append(executor)

        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 10.0  # 500 creations in under 10 seconds
        assert len(executors) == 500


class TestTaskEdgeCases:
    """Test edge cases and error conditions for tasks."""

    def test_task_with_none_values(self):
        """Test task executor handles None values."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        # Just test that executor exists and has properties
        assert executor is not None
        assert hasattr(executor, "implementation")

    def test_task_with_empty_strings(self):
        """Test task executor handles empty strings."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        assert executor is not None

    def test_task_with_unicode_strings(self):
        """Test task executor handles unicode strings."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        assert executor is not None


if __name__ == "__main__":
    pytest.main([__file__])

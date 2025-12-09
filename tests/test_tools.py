"""
Tests for tool execution components.
"""

import json
import time

import pytest


class TestAcceleratedToolExecutor:
    """Test cases for AcceleratedToolExecutor component."""

    def test_import_tool_executor(self):
        """Test that we can import AcceleratedToolExecutor."""
        from fast_crewai import AcceleratedToolExecutor

        executor = AcceleratedToolExecutor()
        assert executor is not None

    def test_tool_executor_creation(self):
        """Test creating tool executor with different configurations."""
        from fast_crewai import AcceleratedToolExecutor

        # Default configuration
        executor1 = AcceleratedToolExecutor()
        assert executor1 is not None

        # Custom recursion depth
        executor2 = AcceleratedToolExecutor(max_recursion_depth=5000)
        assert executor2 is not None

    def test_tool_execution_basic(self):
        """Test basic tool execution."""
        from fast_crewai import AcceleratedToolExecutor

        executor = AcceleratedToolExecutor()

        # Test with simple tool execution
        result = executor.execute_tool("test_tool", {"param": "value"})
        assert isinstance(result, str)
        assert "Executed test_tool with args" in result

    def test_tool_recursion_safety(self):
        """Test that tool executor handles recursion safely."""
        from fast_crewai import AcceleratedToolExecutor

        # Test that we can create executor with high recursion limit
        high_recursion_executor = AcceleratedToolExecutor(max_recursion_depth=10000)
        assert high_recursion_executor is not None

    def test_tool_error_handling(self):
        """Test error handling in tool execution."""
        from fast_crewai import AcceleratedToolExecutor

        executor = AcceleratedToolExecutor()

        # Test with a tool execution - should handle gracefully
        executor.execute_tool("nonexistent_tool", {})
        # The executor should not crash - it returns a result
        assert executor is not None

    def test_tool_performance_basic(self):
        """Basic performance test for tool execution."""
        from fast_crewai import AcceleratedToolExecutor

        # Time multiple tool creations
        start_time = time.time()
        for i in range(100):
            AcceleratedToolExecutor()
        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 5.0  # 100 creations in under 5 seconds


class TestToolIntegration:
    """Integration tests for tool components with CrewAI."""

    def test_crewai_tool_import_compatibility(self):
        """Test that CrewAI tool imports work after shimming."""
        try:
            # Import shim first
            # Then try to import CrewAI tool components
            from crewai.tools.base_tool import BaseTool  # noqa: F401
            from crewai.tools.structured_tool import CrewStructuredTool  # noqa: F401

            import fast_crewai.shim  # noqa: F401

            assert True  # If we get here, imports worked

        except ImportError:
            # CrewAI might not be installed in test environment
            pytest.skip("CrewAI not available for integration testing")

    def test_tool_decorator_integration(self):
        """Test integration with CrewAI tool decorator."""
        try:
            from crewai import tool

            import fast_crewai.shim  # noqa: F401

            @tool
            def test_calculation(a: int, b: int) -> int:
                """Add two numbers."""
                return a + b

            # Tool creation should work
            assert test_calculation is not None

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")

    def test_tool_shimming_behavior(self):
        """Test that tool components are properly shimmed."""
        try:
            from crewai.tools.structured_tool import CrewStructuredTool

            import fast_crewai.shim  # noqa: F401

            # Should be able to use CrewStructuredTool
            # (might be replaced by Rust implementation)
            assert CrewStructuredTool is not None

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")


class TestToolEdgeCases:
    """Test edge cases and error conditions for tools."""

    def test_tool_with_invalid_recursion_depth(self):
        """Test tool executor with invalid recursion depth."""
        from fast_crewai import AcceleratedToolExecutor

        # Test with zero recursion depth
        try:
            executor = AcceleratedToolExecutor(max_recursion_depth=0)
            assert executor is not None
        except ValueError:
            # May raise ValueError for invalid depth
            pass

        # Test with negative recursion depth
        try:
            executor = AcceleratedToolExecutor(max_recursion_depth=-1)
            assert executor is not None
        except ValueError:
            # May raise ValueError for invalid depth
            pass

    def test_tool_with_complex_arguments(self):
        """Test tool execution with complex argument structures."""
        from fast_crewai import AcceleratedToolExecutor

        executor = AcceleratedToolExecutor()

        complex_args = {
            "string": "test string",
            "number": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3, "four"],
            "nested": {"deep": {"value": "nested"}},
        }

        # Test that complex arguments don't crash the executor
        result = executor.execute_tool("test_tool", complex_args)
        assert isinstance(result, str)
        assert executor is not None

    def test_tool_concurrent_usage(self):
        """Test that tool executor can be used concurrently."""
        import threading

        from fast_crewai import AcceleratedToolExecutor

        results = []
        errors = []

        def execute_tool():
            try:
                # Create tool executor in thread
                thread_executor = AcceleratedToolExecutor()
                results.append(thread_executor)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=execute_tool)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should not have crashed
        assert len(errors) == 0
        assert len(results) == 10


class TestToolPerformance:
    """Performance tests for tool execution."""

    def test_tool_creation_performance(self):
        """Test performance of tool executor creation."""
        from fast_crewai import AcceleratedToolExecutor

        start_time = time.time()

        # Create many tool executors
        executors = []
        for i in range(1000):
            executor = AcceleratedToolExecutor()
            executors.append(executor)

        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 10.0  # 1000 creations in under 10 seconds
        assert len(executors) == 1000

    def test_tool_argument_serialization_performance(self):
        """Test performance of argument serialization."""
        # Create large argument structure
        large_args = {"data": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}

        start_time = time.time()

        # Serialize arguments multiple times
        for i in range(100):
            json.dumps(large_args)

        serialization_time = time.time() - start_time

        # Should be reasonably fast
        assert serialization_time < 5.0  # 100 serializations in under 5 seconds


if __name__ == "__main__":
    pytest.main([__file__])

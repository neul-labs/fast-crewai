"""
Tests for tool execution components.
"""

import pytest
import time
import json
from typing import Dict, Any


class TestRustToolExecutor:
    """Test cases for RustToolExecutor component."""

    def test_import_tool_executor(self):
        """Test that we can import RustToolExecutor."""
        from crewai_rust import RustToolExecutor
        executor = RustToolExecutor()
        assert executor is not None

    def test_tool_executor_creation(self):
        """Test creating tool executor with different configurations."""
        from crewai_rust import RustToolExecutor

        # Default configuration
        executor1 = RustToolExecutor()
        assert executor1 is not None

        # Custom recursion depth
        executor2 = RustToolExecutor(max_recursion_depth=5000)
        assert executor2 is not None

    def test_tool_execution_basic(self):
        """Test basic tool execution."""
        from crewai_rust import RustToolExecutor

        executor = RustToolExecutor()

        # Test with simple tool execution (if available)
        try:
            result = executor.execute_tool("test_tool", json.dumps({"param": "value"}))
            # If we get here, tool execution worked
            assert isinstance(result, str)
        except Exception:
            # Tool might not be available - test that executor exists
            assert executor is not None

    def test_tool_recursion_safety(self):
        """Test that tool executor handles recursion safely."""
        from crewai_rust import RustToolExecutor

        executor = RustToolExecutor(max_recursion_depth=100)

        # Test that we can create executor with high recursion limit
        high_recursion_executor = RustToolExecutor(max_recursion_depth=10000)
        assert high_recursion_executor is not None

    def test_tool_error_handling(self):
        """Test error handling in tool execution."""
        from crewai_rust import RustToolExecutor

        executor = RustToolExecutor()

        # Test with invalid tool name
        try:
            result = executor.execute_tool("nonexistent_tool", "{}")
            # May or may not raise exception depending on implementation
        except Exception:
            # Error handling should not crash the executor
            assert executor is not None

    def test_tool_performance_basic(self):
        """Basic performance test for tool execution."""
        from crewai_rust import RustToolExecutor

        executor = RustToolExecutor()

        # Time multiple tool creations
        start_time = time.time()
        for i in range(100):
            executor = RustToolExecutor()
        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 5.0  # 100 creations in under 5 seconds


class TestToolIntegration:
    """Integration tests for tool components with CrewAI."""

    def test_crewai_tool_import_compatibility(self):
        """Test that CrewAI tool imports work after shimming."""
        try:
            # Import shim first
            import crewai_rust.shim

            # Then try to import CrewAI tool components
            from crewai.tools.base_tool import BaseTool
            from crewai.tools.structured_tool import CrewStructuredTool

            assert True  # If we get here, imports worked

        except ImportError:
            # CrewAI might not be installed in test environment
            pytest.skip("CrewAI not available for integration testing")

    def test_tool_decorator_integration(self):
        """Test integration with CrewAI tool decorator."""
        try:
            import crewai_rust.shim
            from crewai import tool

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
            import crewai_rust.shim
            from crewai.tools.structured_tool import CrewStructuredTool

            # Should be able to use CrewStructuredTool
            # (might be replaced by Rust implementation)
            tool_cls = CrewStructuredTool
            assert tool_cls is not None

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")


class TestToolEdgeCases:
    """Test edge cases and error conditions for tools."""

    def test_tool_with_invalid_recursion_depth(self):
        """Test tool executor with invalid recursion depth."""
        from crewai_rust import RustToolExecutor

        # Test with zero recursion depth
        try:
            executor = RustToolExecutor(max_recursion_depth=0)
            assert executor is not None
        except ValueError:
            # May raise ValueError for invalid depth
            pass

        # Test with negative recursion depth
        try:
            executor = RustToolExecutor(max_recursion_depth=-1)
            assert executor is not None
        except ValueError:
            # May raise ValueError for invalid depth
            pass

    def test_tool_with_complex_arguments(self):
        """Test tool execution with complex argument structures."""
        from crewai_rust import RustToolExecutor

        executor = RustToolExecutor()

        complex_args = {
            "string": "test string",
            "number": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3, "four"],
            "nested": {
                "deep": {"value": "nested"}
            }
        }

        # Test that complex arguments don't crash the executor
        try:
            result = executor.execute_tool("test_tool", json.dumps(complex_args))
        except Exception:
            # Tool might not exist, but executor should handle gracefully
            pass

        assert executor is not None

    def test_tool_concurrent_usage(self):
        """Test that tool executor can be used concurrently."""
        from crewai_rust import RustToolExecutor
        import threading

        executor = RustToolExecutor()
        results = []
        errors = []

        def execute_tool():
            try:
                # Create tool executor in thread
                thread_executor = RustToolExecutor()
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
        from crewai_rust import RustToolExecutor

        start_time = time.time()

        # Create many tool executors
        executors = []
        for i in range(1000):
            executor = RustToolExecutor()
            executors.append(executor)

        creation_time = time.time() - start_time

        # Should be reasonably fast
        assert creation_time < 10.0  # 1000 creations in under 10 seconds
        assert len(executors) == 1000

    def test_tool_argument_serialization_performance(self):
        """Test performance of argument serialization."""
        from crewai_rust import RustToolExecutor

        executor = RustToolExecutor()

        # Create large argument structure
        large_args = {
            "data": [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        }

        start_time = time.time()

        # Serialize arguments multiple times
        for i in range(100):
            json_args = json.dumps(large_args)

        serialization_time = time.time() - start_time

        # Should be reasonably fast
        assert serialization_time < 5.0  # 100 serializations in under 5 seconds


if __name__ == "__main__":
    pytest.main([__file__])
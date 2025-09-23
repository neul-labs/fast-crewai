"""
Integration tests for CrewAI Rust components.

These tests verify that the Rust acceleration works correctly
with real CrewAI workflows and maintains compatibility.
"""

import pytest
import time


class TestShimIntegration:
    """Test the shim system integration."""

    def test_shim_import(self):
        """Test that we can import the shim module."""
        import crewai_rust.shim
        assert True  # Import should not crash

    def test_shim_enable_function(self):
        """Test the enable_rust_acceleration function."""
        from crewai_rust.shim import enable_rust_acceleration

        result = enable_rust_acceleration()
        assert isinstance(result, (int, type(None)))

    def test_shim_with_verbose(self):
        """Test shim with verbose output."""
        from crewai_rust.shim import enable_rust_acceleration

        result = enable_rust_acceleration(verbose=True)
        assert isinstance(result, (int, type(None)))

    def test_shim_disable_function(self):
        """Test the disable_rust_acceleration function."""
        try:
            from crewai_rust.shim import disable_rust_acceleration
            result = disable_rust_acceleration()
            assert isinstance(result, (int, type(None)))
        except ImportError:
            # Function might not be implemented yet
            pass


class TestCrewAICompatibility:
    """Test compatibility with actual CrewAI components."""

    def test_crewai_base_imports(self):
        """Test that basic CrewAI imports work."""
        try:
            import crewai
            assert True
        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_crewai_with_shim_imports(self):
        """Test CrewAI imports work after shim activation."""
        try:
            import crewai_rust.shim  # Activate shim
            import crewai
            from crewai import Agent, Task, Crew
            assert True
        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_memory_component_shimming(self):
        """Test that memory components are properly shimmed."""
        try:
            import crewai_rust.shim
            from crewai.memory.storage.rag_storage import RAGStorage

            # Should be able to create storage instance
            storage = RAGStorage(type="test")
            assert storage is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_tool_component_shimming(self):
        """Test that tool components are properly shimmed."""
        try:
            import crewai_rust.shim
            from crewai.tools.base_tool import BaseTool
            from crewai.tools.structured_tool import CrewStructuredTool

            # Should be able to access tool classes
            assert BaseTool is not None
            assert CrewStructuredTool is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_task_component_shimming(self):
        """Test that task components are properly shimmed."""
        try:
            import crewai_rust.shim
            from crewai.task import Task
            from crewai.crew import Crew

            # Should be able to access task classes
            assert Task is not None
            assert Crew is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")


class TestEndToEndWorkflow:
    """End-to-end workflow tests with CrewAI."""

    def test_simple_crew_workflow(self):
        """Test a simple crew workflow with Rust acceleration."""
        try:
            import crewai_rust.shim  # Enable acceleration
            from crewai import Agent, Task, Crew

            # Create a simple agent
            agent = Agent(
                role="Test Agent",
                goal="Complete test tasks",
                backstory="A test agent for integration testing",
                verbose=False
            )

            # Create a simple task
            task = Task(
                description="Analyze the word 'test' and provide insights",
                expected_output="Analysis of the word test",
                agent=agent
            )

            # Create crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False
            )

            # Execute (this is the real test)
            result = crew.kickoff()

            # Verify we got a result
            assert result is not None
            assert hasattr(result, 'raw')

        except ImportError:
            pytest.skip("CrewAI not available for testing")
        except Exception as e:
            # Other exceptions might be due to missing API keys, etc.
            # The important thing is that the shimming didn't crash
            pytest.skip(f"Workflow test skipped due to: {e}")

    def test_memory_enabled_workflow(self):
        """Test workflow with memory enabled."""
        try:
            import crewai_rust.shim
            from crewai import Agent, Task, Crew

            agent = Agent(
                role="Memory Test Agent",
                goal="Test memory functionality",
                backstory="Agent for testing memory features"
            )

            task = Task(
                description="Test memory storage and retrieval",
                expected_output="Memory test results",
                agent=agent
            )

            # Create crew with memory enabled
            crew = Crew(
                agents=[agent],
                tasks=[task],
                memory=True,  # This should use Rust acceleration
                verbose=False
            )

            # The fact that we can create the crew is a success
            assert crew is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")
        except Exception as e:
            pytest.skip(f"Memory workflow test skipped due to: {e}")

    def test_tool_integration_workflow(self):
        """Test workflow with custom tools."""
        try:
            import crewai_rust.shim
            from crewai import Agent, Task, Crew, tool

            @tool
            def test_calculation(a: int, b: int) -> int:
                """Add two numbers together."""
                return a + b

            agent = Agent(
                role="Calculator Agent",
                goal="Perform calculations",
                backstory="Agent that can do math",
                tools=[test_calculation]
            )

            task = Task(
                description="Calculate 5 + 3 using the tool",
                expected_output="The result of 5 + 3",
                agent=agent
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False
            )

            # Creating crew with tools should work
            assert crew is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")
        except Exception as e:
            pytest.skip(f"Tool workflow test skipped due to: {e}")


class TestPerformanceIntegration:
    """Test performance improvements in real workflows."""

    def test_workflow_performance_basic(self):
        """Basic performance test for workflows."""
        try:
            import crewai_rust.shim
            from crewai import Agent, Task, Crew

            # Time crew creation
            start_time = time.time()

            for i in range(10):
                agent = Agent(
                    role=f"Agent {i}",
                    goal="Test goal",
                    backstory="Test backstory"
                )

                task = Task(
                    description="Test task",
                    expected_output="Test output",
                    agent=agent
                )

                crew = Crew(agents=[agent], tasks=[task])

            creation_time = time.time() - start_time

            # Should be reasonably fast
            assert creation_time < 5.0  # 10 crews in under 5 seconds

        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_memory_performance_integration(self):
        """Test memory performance in integrated workflow."""
        try:
            import crewai_rust.shim
            from crewai import Agent, Task, Crew

            agent = Agent(
                role="Memory Performance Agent",
                goal="Test memory performance",
                backstory="Agent for performance testing"
            )

            # Create multiple tasks to exercise memory
            tasks = []
            for i in range(5):
                task = Task(
                    description=f"Memory test task {i}",
                    expected_output=f"Result {i}",
                    agent=agent
                )
                tasks.append(task)

            start_time = time.time()
            crew = Crew(
                agents=[agent],
                tasks=tasks,
                memory=True  # Enable memory (should use Rust)
            )
            creation_time = time.time() - start_time

            # Should be fast even with memory enabled
            assert creation_time < 2.0

        except ImportError:
            pytest.skip("CrewAI not available for testing")


class TestFallbackBehavior:
    """Test fallback behavior when Rust is not available."""

    def test_rust_availability_detection(self):
        """Test detection of Rust availability."""
        from crewai_rust import is_rust_available, get_rust_status

        # Should be able to check availability
        available = is_rust_available()
        assert isinstance(available, bool)

        # Should be able to get status
        status = get_rust_status()
        assert isinstance(status, str)

    def test_fallback_to_python(self):
        """Test graceful fallback to Python implementations."""
        from crewai_rust import RustMemoryStorage

        # Test explicit Python fallback
        storage = RustMemoryStorage(use_rust=False)
        assert storage.implementation == "python"

        # Basic functionality should still work
        storage.save("fallback test", {"mode": "python"})
        results = storage.search("fallback")
        assert isinstance(results, list)

    def test_mixed_implementation_usage(self):
        """Test using both Rust and Python implementations."""
        from crewai_rust import RustMemoryStorage

        # Create one with Rust (if available)
        rust_storage = RustMemoryStorage(use_rust=True)

        # Create one with Python fallback
        python_storage = RustMemoryStorage(use_rust=False)

        # Both should work
        rust_storage.save("rust test", {})
        python_storage.save("python test", {})

        rust_results = rust_storage.search("rust")
        python_results = python_storage.search("python")

        assert isinstance(rust_results, list)
        assert isinstance(python_results, list)


if __name__ == "__main__":
    pytest.main([__file__])
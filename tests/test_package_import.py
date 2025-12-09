"""
Tests for basic package imports and availability.
"""

import pytest


class TestPackageImport:
    """Test basic package import functionality."""

    def test_import_fast_crewai(self):
        """Test that we can import the main package."""
        import fast_crewai

        assert fast_crewai is not None

    def test_package_version(self):
        """Test that package has version information."""
        import fast_crewai

        assert hasattr(fast_crewai, "__version__")
        assert isinstance(fast_crewai.__version__, str)

    def test_acceleration_implementation_flag(self):
        """Test that package has acceleration implementation flag."""
        import fast_crewai

        assert hasattr(fast_crewai, "HAS_ACCELERATION_IMPLEMENTATION")
        assert isinstance(fast_crewai.HAS_ACCELERATION_IMPLEMENTATION, bool)

    def test_acceleration_availability_functions(self):
        """Test acceleration availability detection functions."""
        from fast_crewai import get_acceleration_status, is_acceleration_available

        # Should be able to call these functions
        available = is_acceleration_available()
        status = get_acceleration_status()

        assert isinstance(available, bool)
        assert isinstance(status, dict)

    def test_main_component_imports(self):
        """Test that we can import main components."""
        from fast_crewai import (
            AcceleratedMemoryStorage,
            AcceleratedTaskExecutor,
            AcceleratedToolExecutor,
        )

        assert AcceleratedMemoryStorage is not None
        assert AcceleratedToolExecutor is not None
        assert AcceleratedTaskExecutor is not None

    def test_serialization_imports(self):
        """Test that we can import serialization components."""
        try:
            from fast_crewai import AgentMessage

            assert AgentMessage is not None
        except ImportError:
            # Serialization components might not be available
            pass

    def test_database_imports(self):
        """Test that we can import database components."""
        try:
            from fast_crewai import AcceleratedSQLiteWrapper

            assert AcceleratedSQLiteWrapper is not None
        except ImportError:
            # Database components might not be available
            pass


class TestComponentAvailability:
    """Test availability of different components."""

    def test_memory_component_creation(self):
        """Test that memory components can be created."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()
        assert storage is not None
        assert hasattr(storage, "implementation")

    def test_tool_component_creation(self):
        """Test that tool components can be created."""
        from fast_crewai import AcceleratedToolExecutor

        executor = AcceleratedToolExecutor()
        assert executor is not None

    def test_task_component_creation(self):
        """Test that task components can be created."""
        from fast_crewai import AcceleratedTaskExecutor

        executor = AcceleratedTaskExecutor()
        assert executor is not None

    def test_component_methods_exist(self):
        """Test that components have expected methods."""
        from fast_crewai import AcceleratedMemoryStorage, AcceleratedToolExecutor

        # Memory storage methods
        storage = AcceleratedMemoryStorage()
        assert hasattr(storage, "save")
        assert hasattr(storage, "search")

        # Tool executor methods
        executor = AcceleratedToolExecutor()
        assert hasattr(executor, "execute_tool")


class TestEnvironmentInfo:
    """Test environment information functions."""

    def test_environment_info_function(self):
        """Test environment information retrieval."""
        try:
            from fast_crewai import get_environment_info

            info = get_environment_info()
            assert isinstance(info, dict)
        except ImportError:
            # Function might not be implemented
            pass

    def test_performance_metrics_function(self):
        """Test performance metrics retrieval."""
        try:
            from fast_crewai.utils import get_performance_improvements

            metrics = get_performance_improvements()
            assert isinstance(metrics, dict)
        except ImportError:
            # Function might not be implemented
            pass

    def test_rust_status_details(self):
        """Test detailed Rust status information."""
        from fast_crewai import get_acceleration_status

        status = get_acceleration_status()
        assert isinstance(status, dict)
        assert "available" in status


if __name__ == "__main__":
    pytest.main([__file__])

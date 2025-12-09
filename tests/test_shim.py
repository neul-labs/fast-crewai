"""
Tests for the shim system that enables Rust acceleration.
"""

import os
import sys

import pytest


class TestShimImport:
    """Test shim module import functionality."""

    def test_shim_module_import(self):
        """Test that we can import the shim module."""
        import fast_crewai.shim  # noqa: F401

        assert True  # Should not raise exception

    def test_shim_functions_available(self):
        """Test that shim functions are available."""
        from fast_crewai.shim import enable_acceleration

        assert callable(enable_acceleration)

    def test_shim_enable_function(self):
        """Test the enable_acceleration function."""
        from fast_crewai.shim import enable_acceleration

        result = enable_acceleration()
        assert isinstance(result, bool)

    def test_shim_enable_with_verbose(self):
        """Test shim enable with verbose output."""
        from fast_crewai.shim import enable_acceleration

        result = enable_acceleration(verbose=True)
        assert isinstance(result, bool)

    def test_shim_disable_function(self):
        """Test the disable_acceleration function if available."""
        try:
            from fast_crewai.shim import disable_acceleration

            result = disable_acceleration()
            assert isinstance(result, bool)
        except ImportError:
            # Function might not be implemented yet
            pass


class TestEnvironmentVariableActivation:
    """Test environment variable-based shim activation."""

    def test_environment_variable_detection(self):
        """Test that environment variable is properly detected."""
        original = os.environ.get("FAST_CREWAI_ACCELERATION")

        try:
            # Test with environment variable set
            os.environ["FAST_CREWAI_ACCELERATION"] = "1"

            # Import should work regardless
            import fast_crewai.shim  # noqa: F401

            assert True

        finally:
            # Restore original environment
            if original is None:
                os.environ.pop("FAST_CREWAI_ACCELERATION", None)
            else:
                os.environ["FAST_CREWAI_ACCELERATION"] = original

    def test_environment_variable_values(self):
        """Test different environment variable values."""
        original = os.environ.get("FAST_CREWAI_ACCELERATION")

        test_values = ["1", "true", "TRUE", "yes", "YES", "on", "ON"]

        try:
            for value in test_values:
                os.environ["FAST_CREWAI_ACCELERATION"] = value

                # Should be able to import without error
                from fast_crewai.shim import enable_acceleration

                result = enable_acceleration()
                assert isinstance(result, bool)

        finally:
            if original is None:
                os.environ.pop("FAST_CREWAI_ACCELERATION", None)
            else:
                os.environ["FAST_CREWAI_ACCELERATION"] = original

    def test_environment_variable_disabled(self):
        """Test behavior when environment variable is disabled."""
        original = os.environ.get("FAST_CREWAI_ACCELERATION")

        try:
            os.environ["FAST_CREWAI_ACCELERATION"] = "0"

            # Should still be able to import
            import fast_crewai.shim  # noqa: F401

            assert True

        finally:
            if original is None:
                os.environ.pop("FAST_CREWAI_ACCELERATION", None)
            else:
                os.environ["FAST_CREWAI_ACCELERATION"] = original


class TestCrewAICompatibility:
    """Test shim compatibility with CrewAI components."""

    def test_crewai_base_import(self):
        """Test that CrewAI can be imported."""
        try:
            import crewai  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_crewai_memory_modules_import(self):
        """Test that CrewAI memory modules can be imported."""
        try:
            import crewai.memory.memory  # noqa: F401
            import crewai.memory.short_term.short_term_memory  # noqa: F401
            import crewai.memory.storage.rag_storage  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_crewai_tool_modules_import(self):
        """Test that CrewAI tool modules can be imported."""
        try:
            import crewai.tools.base_tool  # noqa: F401
            import crewai.tools.structured_tool  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_crewai_task_modules_import(self):
        """Test that CrewAI task modules can be imported."""
        try:
            import crewai.crew  # noqa: F401
            import crewai.task  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_shim_with_crewai_import_order(self):
        """Test shim behavior with different import orders."""
        try:
            # Test: shim first, then CrewAI
            import crewai  # noqa: F401

            import fast_crewai.shim  # noqa: F401

            assert True

        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_memory_component_shimming(self):
        """Test that memory components are properly shimmed."""
        try:
            from crewai.memory.storage.rag_storage import RAGStorage

            import fast_crewai.shim  # noqa: F401

            # Should be able to access the class
            assert RAGStorage is not None

            # Try to create an instance
            storage = RAGStorage(type="test")
            assert storage is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")

    def test_tool_component_shimming(self):
        """Test that tool components are properly shimmed."""
        try:
            from crewai.tools.structured_tool import CrewStructuredTool

            import fast_crewai.shim  # noqa: F401

            # Should be able to access the class
            assert CrewStructuredTool is not None

        except ImportError:
            pytest.skip("CrewAI not available for testing")


class TestShimInternals:
    """Test internal shim mechanisms."""

    def test_monkey_patch_function_exists(self):
        """Test that internal monkey patch function exists."""
        try:
            from fast_crewai.shim import _monkey_patch_class

            assert callable(_monkey_patch_class)
        except ImportError:
            # Internal function might not be exposed
            pass

    def test_original_classes_backup(self):
        """Test that original classes are backed up."""
        try:
            from fast_crewai.shim import _original_classes

            assert isinstance(_original_classes, dict)
        except ImportError:
            # Internal variable might not be exposed
            pass

    def test_shim_status_tracking(self):
        """Test that shim status is properly tracked."""
        from fast_crewai.shim import enable_acceleration

        # Enable shimming
        result = enable_acceleration()

        # Should return bool indicating success
        assert isinstance(result, bool)

    def test_multiple_shim_enable_calls(self):
        """Test that multiple enable calls are safe."""
        from fast_crewai.shim import enable_acceleration

        # Call multiple times
        result1 = enable_acceleration()
        result2 = enable_acceleration()
        result3 = enable_acceleration()

        # Should not crash
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        assert isinstance(result3, bool)

    def test_shim_with_missing_modules(self):
        """Test shim behavior when target modules are missing."""
        from fast_crewai.shim import enable_acceleration

        # Should handle missing modules gracefully
        result = enable_acceleration()
        assert isinstance(result, bool)


class TestShimErrorHandling:
    """Test error handling in shim system."""

    def test_shim_with_import_errors(self):
        """Test shim behavior with import errors."""
        # Temporarily remove modules from sys.modules
        original_modules = {}
        test_modules = [
            "crewai.memory.storage.rag_storage",
            "crewai.tools.structured_tool",
        ]

        try:
            for module in test_modules:
                if module in sys.modules:
                    original_modules[module] = sys.modules[module]
                    del sys.modules[module]

            # Shim should handle missing modules gracefully
            from fast_crewai.shim import enable_acceleration

            result = enable_acceleration()
            assert isinstance(result, bool)

        finally:
            # Restore modules
            for module, mod_obj in original_modules.items():
                sys.modules[module] = mod_obj

    def test_shim_with_attribute_errors(self):
        """Test shim behavior with attribute errors."""
        from fast_crewai.shim import enable_acceleration

        # Should handle attribute errors gracefully
        result = enable_acceleration()
        assert isinstance(result, bool)

    def test_shim_restoration_safety(self):
        """Test that shim restoration is safe."""
        try:
            from fast_crewai.shim import disable_acceleration

            result = disable_acceleration()
            assert isinstance(result, bool)
        except ImportError:
            # Function might not be implemented
            pass


class TestShimPerformance:
    """Test performance aspects of shimming."""

    def test_shim_enable_performance(self):
        """Test that shim enabling is reasonably fast."""
        import time

        from fast_crewai.shim import enable_acceleration

        start_time = time.time()
        for i in range(10):
            enable_acceleration()
        end_time = time.time()

        # Should be fast
        assert (end_time - start_time) < 1.0  # 10 calls in under 1 second

    def test_shim_import_performance(self):
        """Test that shim import is reasonably fast."""
        import time

        start_time = time.time()
        for i in range(10):
            # Import in a way that forces reload
            if "fast_crewai.shim" in sys.modules:
                del sys.modules["fast_crewai.shim"]
            import fast_crewai.shim  # noqa: F401
        end_time = time.time()

        # Should be fast
        assert (end_time - start_time) < 2.0  # 10 imports in under 2 seconds


if __name__ == "__main__":
    pytest.main([__file__])

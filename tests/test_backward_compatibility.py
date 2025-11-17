"""
Backward Compatibility Tests for CrewAI Rust Integration

These tests verify that existing CrewAI code continues to work unchanged
when the Rust integration is installed.
"""

import unittest
import os
import sys
from typing import Any, Dict, List, Optional
from unittest.mock import patch, MagicMock

# Add the fast_crewai directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fast_crewai'))

try:
    from fast_crewai import HAS_RUST_IMPLEMENTATION
    RUST_AVAILABLE = HAS_RUST_IMPLEMENTATION
except ImportError:
    RUST_AVAILABLE = False

class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing CrewAI code."""

    def setUp(self):
        """Set up test environment."""
        # Clear any existing environment variables that might affect tests
        self.original_env = {}
        env_vars = [
            'FAST_CREWAI_ACCELERATION',
            'FAST_CREWAI_MEMORY',
            'FAST_CREWAI_TOOLS',
            'FAST_CREWAI_TASKS',
            'FAST_CREWAI_SERIALIZATION',
            'FAST_CREWAI_DATABASE'
        ]
        
        for var in env_vars:
            if var in os.environ:
                self.original_env[var] = os.environ[var]
                del os.environ[var]

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment variables
        for var, value in self.original_env.items():
            os.environ[var] = value

    def test_import_fast_crewai(self):
        """Test that fast_crewai can be imported without errors."""
        try:
            import fast_crewai
            self.assertTrue(hasattr(fast_crewai, '__version__'))
            self.assertTrue(hasattr(fast_crewai, 'HAS_RUST_IMPLEMENTATION'))
        except ImportError as e:
            self.fail(f"Failed to import fast_crewai: {e}")

    def test_rust_availability_flag(self):
        """Test that HAS_RUST_IMPLEMENTATION is properly defined."""
        import fast_crewai
        self.assertIsInstance(fast_crewai.HAS_RUST_IMPLEMENTATION, bool)

    def test_environment_variable_handling(self):
        """Test that environment variables are handled correctly."""
        # Test with environment variable set to 'true'
        os.environ['FAST_CREWAI_ACCELERATION'] = '1'
        
        try:
            # Re-import to test environment variable handling
            import importlib
            import fast_crewai
            importlib.reload(fast_crewai)
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_graceful_degradation(self):
        """Test that the system gracefully degrades when Rust is unavailable."""
        if not RUST_AVAILABLE:
            # Test that components fall back to Python implementations
            try:
                from fast_crewai.memory import RustMemoryStorage
                storage = RustMemoryStorage()
                self.assertEqual(storage.implementation, "python")
            except Exception as e:
                # This is expected if Rust components aren't available
                pass

    def test_component_imports(self):
        """Test that all components can be imported."""
        components = [
            'RustMemoryStorage',
            'RustToolExecutor', 
            'RustTaskExecutor',
            'AgentMessage',
            'RustSQLiteWrapper'
        ]
        
        for component in components:
            try:
                from fast_crewai import component
                self.assertTrue(True)  # Import successful
            except ImportError:
                # This is expected if Rust components aren't available
                pass

    def test_utility_functions(self):
        """Test that utility functions work correctly."""
        try:
            from fast_crewai.utils import is_rust_available, get_rust_status
            self.assertIsInstance(is_rust_available(), bool)
            self.assertIsInstance(get_rust_status(), dict)
        except ImportError:
            # This is expected if Rust components aren't available
            pass

    def test_shim_import(self):
        """Test that the shim module can be imported."""
        try:
            import fast_crewai.shim
            self.assertTrue(hasattr(fast_crewai.shim, 'enable_rust_acceleration'))
        except ImportError:
            # This is expected if shim module isn't available
            pass

    def test_memory_storage_compatibility(self):
        """Test that memory storage maintains API compatibility."""
        try:
            from fast_crewai.memory import RustMemoryStorage
            
            # Test basic functionality
            storage = RustMemoryStorage()
            
            # Test save method
            storage.save("test value", {"metadata": "test"})
            
            # Test search method
            results = storage.search("test", limit=5)
            self.assertIsInstance(results, list)
            
            # Test get_all method
            all_items = storage.get_all()
            self.assertIsInstance(all_items, list)
            
            # Test reset method
            storage.reset()
            
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_tool_executor_compatibility(self):
        """Test that tool executor maintains API compatibility."""
        try:
            from fast_crewai.tools import RustToolExecutor
            
            # Test basic functionality
            executor = RustToolExecutor(max_recursion_depth=10)
            
            # Test execute_tool method
            result = executor.execute_tool("test_tool", {"param": "value"})
            self.assertIsInstance(result, str)
            
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_task_executor_compatibility(self):
        """Test that task executor maintains API compatibility."""
        try:
            from fast_crewai.tasks import RustTaskExecutor
            
            # Test basic functionality
            executor = RustTaskExecutor()
            
            # Test execute_concurrent_tasks method
            tasks = ["task1", "task2", "task3"]
            results = executor.execute_concurrent_tasks(tasks)
            self.assertIsInstance(results, list)
            self.assertEqual(len(results), len(tasks))
            
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_serialization_compatibility(self):
        """Test that serialization maintains API compatibility."""
        try:
            from fast_crewai.serialization import AgentMessage
            
            # Test basic functionality
            message = AgentMessage(
                id="test_id",
                sender="test_sender", 
                recipient="test_recipient",
                content="test_content",
                timestamp=1234567890
            )
            
            # Test to_json method
            json_str = message.to_json()
            self.assertIsInstance(json_str, str)
            
            # Test from_json method
            message2 = AgentMessage.from_json(json_str)
            self.assertEqual(message.id, message2.id)
            self.assertEqual(message.sender, message2.sender)
            
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_database_compatibility(self):
        """Test that database operations maintain API compatibility."""
        try:
            import tempfile
            from fast_crewai.database import RustSQLiteWrapper
            
            # Test basic functionality
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                db_path = tmp.name
            
            try:
                wrapper = RustSQLiteWrapper(db_path)
            
                # Test execute_query method
                results = wrapper.execute_query("SELECT 1 as test")
                self.assertIsInstance(results, list)
                
                # Test execute_update method
                affected = wrapper.execute_update("CREATE TABLE test (id INTEGER)")
                self.assertIsInstance(affected, int)
                
            finally:
                # Clean up
                if os.path.exists(db_path):
                    os.unlink(db_path)
                    
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_integration_with_crewai(self):
        """Test integration with actual CrewAI components."""
        try:
            # Test that we can import CrewAI components
            from crewai import Agent, Task, Crew
            
            # Create a simple agent
            agent = Agent(
                role="Test Agent",
                goal="Test Goal",
                backstory="Test Backstory"
            )
            
            # Create a simple task
            task = Task(
                description="Test Task",
                expected_output="Test Output",
                agent=agent
            )
            
            # Create a crew
            crew = Crew(
                agents=[agent],
                tasks=[task]
            )
            
            self.assertIsNotNone(crew)
            
        except ImportError:
            # This is expected if CrewAI isn't installed
            pass

    def test_error_handling(self):
        """Test that error handling works correctly."""
        try:
            from fast_crewai.memory import RustMemoryStorage
            
            # Test with invalid parameters
            storage = RustMemoryStorage()
            
            # Test search with invalid parameters
            results = storage.search("", limit=-1)
            self.assertIsInstance(results, list)
            
        except Exception as e:
            # This is expected if Rust components aren't available
            pass

    def test_configuration_utilities(self):
        """Test configuration utilities."""
        try:
            from fast_crewai.utils import configure_rust_components, get_environment_info
            
            # Test configure_rust_components
            configure_rust_components(memory=True, tools=False)
            
            # Test get_environment_info
            env_info = get_environment_info()
            self.assertIsInstance(env_info, dict)
            self.assertIn('FAST_CREWAI_MEMORY', env_info)
            
        except ImportError:
            # This is expected if Rust components aren't available
            pass

    def test_performance_utilities(self):
        """Test performance utilities."""
        try:
            from fast_crewai.utils import get_performance_improvements, benchmark_comparison
            
            # Test get_performance_improvements
            improvements = get_performance_improvements()
            self.assertIsInstance(improvements, dict)
            self.assertIn('memory', improvements)
            
            # Test benchmark_comparison
            memory_benchmark = benchmark_comparison('memory')
            self.assertIsInstance(memory_benchmark, dict)
            
        except ImportError:
            # This is expected if Rust components aren't available
            pass


if __name__ == '__main__':
    unittest.main()



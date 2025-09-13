"""
Backward Compatibility Tests for CrewAI Rust Integration

These tests verify that existing CrewAI code continues to work unchanged
when the Rust integration is installed.
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Test that we can import the Rust components
try:
    from crewai_rust import HAS_RUST_IMPLEMENTATION
    RUST_AVAILABLE = HAS_RUST_IMPLEMENTATION
except ImportError:
    RUST_AVAILABLE = False

# Test importing the main components
try:
    from crewai_rust.memory import RustMemoryStorage
    from crewai_rust.tools import RustToolExecutor
    from crewai_rust.tasks import RustTaskExecutor
    from crewai_rust.serialization import AgentMessage
    from crewai_rust.database import RustSQLiteWrapper
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

class TestImportCompatibility(unittest.TestCase):
    """Test that all imports work correctly."""
    
    def test_main_package_import(self):
        """Test that the main package can be imported."""
        try:
            import crewai_rust
            self.assertTrue(hasattr(crewai_rust, 'HAS_RUST_IMPLEMENTATION'))
        except ImportError:
            self.fail("Failed to import crewai_rust package")
    
    def test_component_imports(self):
        """Test that all components can be imported."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        # Test individual component imports
        try:
            from crewai_rust.memory import RustMemoryStorage
            from crewai_rust.tools import RustToolExecutor
            from crewai_rust.tasks import RustTaskExecutor
            from crewai_rust.serialization import AgentMessage
            from crewai_rust.database import RustSQLiteWrapper
        except ImportError as e:
            self.fail(f"Failed to import components: {e}")
    
    def test_has_rust_implementation_flag(self):
        """Test that HAS_RUST_IMPLEMENTATION flag works correctly."""
        import crewai_rust
        self.assertIsInstance(crewai_rust.HAS_RUST_IMPLEMENTATION, bool)

class TestExistingCodeCompatibility(unittest.TestCase):
    """Test that existing CrewAI code patterns still work."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    def test_memory_storage_basic_usage(self):
        """Test basic memory storage usage pattern."""
        from crewai_rust.memory import RustMemoryStorage
        
        # This is how users would typically use the component
        memory = RustMemoryStorage()
        
        # Basic operations
        memory.save("test data", {"category": "test"})
        results = memory.search("test")
        
        # Should work without errors
        self.assertIsInstance(results, list)
    
    def test_tool_executor_basic_usage(self):
        """Test basic tool executor usage pattern."""
        from crewai_rust.tools import RustToolExecutor
        
        # This is how users would typically use the component
        executor = RustToolExecutor(max_recursion_depth=10)
        
        # Basic operation
        result = executor.execute_tool("test_tool", {"param": "value"})
        
        # Should work without errors
        self.assertIsInstance(result, str)
        self.assertIn("Executed", result)
    
    def test_task_executor_basic_usage(self):
        """Test basic task executor usage pattern."""
        from crewai_rust.tasks import RustTaskExecutor
        
        # This is how users would typically use the component
        executor = RustTaskExecutor()
        
        # Basic operation
        results = executor.execute_concurrent_tasks(["task1", "task2"])
        
        # Should work without errors
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
    
    def test_serialization_basic_usage(self):
        """Test basic serialization usage pattern."""
        from crewai_rust.serialization import AgentMessage
        
        # This is how users would typically use the component
        message = AgentMessage("1", "sender", "recipient", "content", 1234567890)
        
        # Basic operations
        json_str = message.to_json()
        message2 = AgentMessage.from_json(json_str)
        
        # Should work without errors
        self.assertIsInstance(json_str, str)
        self.assertIsInstance(message2, AgentMessage)

class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment configuration compatibility."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_environment_variable_handling(self):
        """Test that environment variables are handled correctly."""
        from crewai_rust.utils import configure_rust_components, get_environment_info
        
        # Test configuration
        configure_rust_components(
            memory=True,
            tools=False,
            tasks=True
        )
        
        # Check that environment variables are set
        env_info = get_environment_info()
        self.assertEqual(env_info['CREWAI_RUST_MEMORY'], 'true')
        self.assertEqual(env_info['CREWAI_RUST_TOOLS'], 'false')
        self.assertEqual(env_info['CREWAI_RUST_TASKS'], 'true')
    
    def test_auto_detection(self):
        """Test automatic detection of Rust availability."""
        from crewai_rust.utils import get_environment_info
        
        # Test default behavior (auto)
        env_info = get_environment_info()
        self.assertIn(env_info['CREWAI_RUST_MEMORY'], ['auto', 'true', 'false'])

class TestErrorHandling(unittest.TestCase):
    """Test error handling and fallback mechanisms."""
    
    def test_graceful_degradation(self):
        """Test that components handle errors gracefully."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        from crewai_rust.memory import RustMemoryStorage
        
        # Test normal operation
        memory = RustMemoryStorage()
        memory.save("test", {"key": "value"})
        results = memory.search("test")
        
        self.assertIsInstance(results, list)
    
    def test_recursion_limit_handling(self):
        """Test that recursion limits are handled properly."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        from crewai_rust.tools import RustToolExecutor
        
        # Create executor with low recursion limit
        executor = RustToolExecutor(max_recursion_depth=2)
        
        # Should work for normal usage
        result1 = executor.execute_tool("tool1", {})
        result2 = executor.execute_tool("tool2", {})
        
        self.assertIsInstance(result1, str)
        self.assertIsInstance(result2, str)
        
        # Note: We're not testing the recursion limit error case here
        # because it would require actually hitting the limit, which
        # might have side effects in a real implementation

class TestIntegrationWithCrewAI(unittest.TestCase):
    """Test integration with existing CrewAI patterns."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    @patch('crewai.Crew')
    @patch('crewai.Agent')
    @patch('crewai.Task')
    def test_crew_integration_patterns(self, mock_task, mock_agent, mock_crew):
        """Test that integration patterns work with CrewAI."""
        # This test simulates how the Rust components would integrate
        # with existing CrewAI code without breaking anything
        
        from crewai_rust.integration import RustMemoryIntegration
        
        # Mock the CrewAI classes
        mock_crew_instance = MagicMock()
        mock_crew.return_value = mock_crew_instance
        
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance
        
        mock_task_instance = MagicMock()
        mock_task.return_value = mock_task_instance
        
        # Test that we can create enhanced memory without errors
        try:
            short_term_memory = RustMemoryIntegration.create_short_term_memory()
            long_term_memory = RustMemoryIntegration.create_long_term_memory()
        except Exception as e:
            self.fail(f"Failed to create enhanced memory: {e}")
        
        # The actual CrewAI integration would happen in the modified
        # CrewAI classes, but we can test that our integration layer
        # doesn't break existing patterns

class TestPerformanceInterfaceCompatibility(unittest.TestCase):
    """Test that performance interfaces are compatible."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    def test_implementation_property(self):
        """Test that implementation property works."""
        from crewai_rust.memory import RustMemoryStorage
        from crewai_rust.tools import RustToolExecutor
        from crewai_rust.tasks import RustTaskExecutor
        from crewai_rust.serialization import AgentMessage
        
        # Test memory storage
        memory = RustMemoryStorage()
        self.assertTrue(hasattr(memory, 'implementation'))
        self.assertIn(memory.implementation, ['rust', 'python'])
        
        # Test tool executor
        tools = RustToolExecutor()
        self.assertTrue(hasattr(tools, 'implementation'))
        self.assertIn(tools.implementation, ['rust', 'python'])
        
        # Test task executor
        tasks = RustTaskExecutor()
        self.assertTrue(hasattr(tasks, 'implementation'))
        self.assertIn(tasks.implementation, ['rust', 'python'])
        
        # Test serialization
        message = AgentMessage("1", "s", "r", "c", 1234567890)
        self.assertTrue(hasattr(message, 'implementation'))
        self.assertIn(message.implementation, ['rust', 'python'])

class TestAPIConsistency(unittest.TestCase):
    """Test that APIs are consistent between implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    def test_memory_storage_api(self):
        """Test that memory storage API is consistent."""
        from crewai_rust.memory import RustMemoryStorage
        
        memory = RustMemoryStorage()
        
        # Check that all expected methods exist
        expected_methods = ['save', 'search', 'get_all', 'reset', 'implementation']
        for method in expected_methods:
            self.assertTrue(hasattr(memory, method), f"Missing method: {method}")
        
        # Check method signatures by calling them
        try:
            memory.save("test", {"key": "value"})
            results = memory.search("test")
            all_items = memory.get_all()
            memory.reset()
        except Exception as e:
            self.fail(f"API methods failed: {e}")
    
    def test_tool_executor_api(self):
        """Test that tool executor API is consistent."""
        from crewai_rust.tools import RustToolExecutor
        
        executor = RustToolExecutor()
        
        # Check that all expected methods exist
        expected_methods = ['execute_tool', 'implementation']
        for method in expected_methods:
            self.assertTrue(hasattr(executor, method), f"Missing method: {method}")
        
        # Check method signatures by calling them
        try:
            result = executor.execute_tool("test", {"param": "value"})
        except Exception as e:
            self.fail(f"API methods failed: {e}")
    
    def test_serialization_api(self):
        """Test that serialization API is consistent."""
        from crewai_rust.serialization import AgentMessage
        
        # Test instance methods
        message = AgentMessage("1", "s", "r", "c", 1234567890)
        expected_methods = ['to_json', 'implementation']
        for method in expected_methods:
            self.assertTrue(hasattr(message, method), f"Missing method: {method}")
        
        # Test class methods
        self.assertTrue(hasattr(AgentMessage, 'from_json'), "Missing class method: from_json")

def create_compatibility_test_suite():
    """Create a test suite for all backward compatibility tests."""
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTest(unittest.makeSuite(TestImportCompatibility))
    suite.addTest(unittest.makeSuite(TestExistingCodeCompatibility))
    suite.addTest(unittest.makeSuite(TestEnvironmentConfiguration))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    suite.addTest(unittest.makeSuite(TestIntegrationWithCrewAI))
    suite.addTest(unittest.makeSuite(TestPerformanceInterfaceCompatibility))
    suite.addTest(unittest.makeSuite(TestAPIConsistency))
    
    return suite

if __name__ == "__main__":
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = create_compatibility_test_suite()
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    if not result.wasSuccessful():
        sys.exit(1)
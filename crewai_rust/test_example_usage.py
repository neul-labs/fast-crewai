"""
Example Usage Tests for CrewAI Rust Integration

These tests demonstrate and verify the example usage patterns
to ensure they work correctly with both Rust and Python implementations.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import the example module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import the example module
try:
    import example_usage
    EXAMPLE_MODULE_AVAILABLE = True
except ImportError as e:
    EXAMPLE_MODULE_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import the Rust components
try:
    from crewai_rust import HAS_RUST_IMPLEMENTATION
    RUST_AVAILABLE = HAS_RUST_IMPLEMENTATION
    COMPONENTS_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    COMPONENTS_AVAILABLE = False

class TestExampleUsage(unittest.TestCase):
    """Test that the example usage code works correctly."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not EXAMPLE_MODULE_AVAILABLE:
            self.skipTest(f"Example module not available: {IMPORT_ERROR}")
    
    def test_example_memory_usage(self):
        """Test the memory usage example."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        # This test verifies that the example code runs without errors
        try:
            example_usage.example_memory_usage()
        except Exception as e:
            self.fail(f"Memory usage example failed: {e}")
    
    def test_example_tool_execution(self):
        """Test the tool execution example."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        # This test verifies that the example code runs without errors
        try:
            example_usage.example_tool_execution()
        except Exception as e:
            self.fail(f"Tool execution example failed: {e}")
    
    def test_example_task_execution(self):
        """Test the task execution example."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        # This test verifies that the example code runs without errors
        try:
            example_usage.example_task_execution()
        except Exception as e:
            self.fail(f"Task execution example failed: {e}")
    
    def test_example_serialization(self):
        """Test the serialization example."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        # This test verifies that the example code runs without errors
        try:
            example_usage.example_serialization()
        except Exception as e:
            self.fail(f"Serialization example failed: {e}")
    
    def test_example_database_operations(self):
        """Test the database operations example."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
        
        # This test verifies that the example code runs without errors
        try:
            example_usage.example_database_operations()
        except Exception as e:
            self.fail(f"Database operations example failed: {e}")
    
    def test_example_performance_info(self):
        """Test the performance info example."""
        # This test should always work
        try:
            example_usage.example_performance_info()
        except Exception as e:
            self.fail(f"Performance info example failed: {e}")
    
    def test_example_environment_configuration(self):
        """Test the environment configuration example."""
        # This test should always work
        try:
            example_usage.example_environment_configuration()
        except Exception as e:
            self.fail(f"Environment configuration example failed: {e}")

class TestIntegrationWithExistingCrewAI(unittest.TestCase):
    """Test integration patterns with existing CrewAI code."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    def test_crew_integration_pattern(self):
        """Test the Crew integration pattern."""
        # This test simulates how users would integrate Rust components
        # with existing CrewAI code
        
        # Import the integration utilities
        try:
            from crewai_rust.integration import RustMemoryIntegration
        except ImportError as e:
            self.skipTest(f"Integration module not available: {e}")
        
        # Test that we can create enhanced memory without errors
        try:
            # This is how users would enhance their CrewAI applications
            short_term_memory = RustMemoryIntegration.create_short_term_memory()
            long_term_memory = RustMemoryIntegration.create_long_term_memory()
            
            # Verify that the objects were created
            self.assertIsNotNone(short_term_memory)
            self.assertIsNotNone(long_term_memory)
            
        except Exception as e:
            self.fail(f"Crew integration pattern failed: {e}")
    
    def test_selective_enhancement_pattern(self):
        """Test the selective enhancement pattern."""
        # This test verifies that users can selectively enable components
        
        # Import the configuration utilities
        try:
            from crewai_rust.utils import configure_rust_components
        except ImportError as e:
            self.skipTest(f"Utils module not available: {e}")
        
        # Test that we can configure components without errors
        try:
            # This is how users would selectively enable components
            configure_rust_components(
                memory=True,      # Enable Rust memory
                tools=True,       # Enable Rust tools
                tasks=False,      # Keep tasks on Python
                serialization=True,   # Enable Rust serialization
                database=False    # Keep database on Python
            )
        except Exception as e:
            self.fail(f"Selective enhancement pattern failed: {e}")

class TestMigrationPatterns(unittest.TestCase):
    """Test migration patterns from Python to Rust."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    def test_zero_breaking_changes_migration(self):
        """Test the zero breaking changes migration pattern."""
        # This test verifies that existing code continues to work
        
        # Import the status utilities
        try:
            from crewai_rust.utils import get_rust_status
        except ImportError as e:
            self.skipTest(f"Utils module not available: {e}")
        
        # Test that we can check status without errors
        try:
            status = get_rust_status()
            
            # Verify that we get expected structure
            self.assertIsInstance(status, dict)
            self.assertIn('available', status)
            self.assertIsInstance(status['available'], bool)
            
            if status['available']:
                self.assertIn('components', status)
                self.assertIsInstance(status['components'], dict)
                
        except Exception as e:
            self.fail(f"Zero breaking changes migration pattern failed: {e}")
    
    def test_environment_based_migration(self):
        """Test environment-based migration pattern."""
        import os
        
        # Save original environment
        original_memory = os.environ.get('CREWAI_RUST_MEMORY')
        original_tools = os.environ.get('CREWAI_RUST_TOOLS')
        
        try:
            # Test setting environment variables
            os.environ['CREWAI_RUST_MEMORY'] = 'true'
            os.environ['CREWAI_RUST_TOOLS'] = 'false'
            
            # Import and test that configuration is respected
            from crewai_rust.utils import get_environment_info
            
            env_info = get_environment_info()
            self.assertEqual(env_info['CREWAI_RUST_MEMORY'], 'true')
            self.assertEqual(env_info['CREWAI_RUST_TOOLS'], 'false')
            
        finally:
            # Restore original environment
            if original_memory is not None:
                os.environ['CREWAI_RUST_MEMORY'] = original_memory
            elif 'CREWAI_RUST_MEMORY' in os.environ:
                del os.environ['CREWAI_RUST_MEMORY']
                
            if original_tools is not None:
                os.environ['CREWAI_RUST_TOOLS'] = original_tools
            elif 'CREWAI_RUST_TOOLS' in os.environ:
                del os.environ['CREWAI_RUST_TOOLS']

class TestRealWorldUsageScenarios(unittest.TestCase):
    """Test real-world usage scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Rust components not available")
    
    def test_high_performance_memory_operations(self):
        """Test high-performance memory operations scenario."""
        from crewai_rust.memory import RustMemoryStorage
        
        # Simulate a high-performance scenario
        memory = RustMemoryStorage()
        
        # Save many items quickly
        try:
            for i in range(1000):
                memory.save(f"performance_item_{i}", {
                    "id": i,
                    "batch": "performance_test",
                    "timestamp": i
                })
            
            # Search for items
            results = memory.search("performance_item")
            
            # Should have found many items
            self.assertGreater(len(results), 0)
            self.assertLessEqual(len(results), 1000)
            
        except Exception as e:
            self.fail(f"High-performance memory operations failed: {e}")
    
    def test_concurrent_task_processing(self):
        """Test concurrent task processing scenario."""
        from crewai_rust.tasks import RustTaskExecutor
        
        # Simulate concurrent task processing
        executor = RustTaskExecutor()
        
        # Create many tasks
        tasks = [
            {"id": f"task_{i}", "data": f"processing_data_{i}"}
            for i in range(50)
        ]
        
        try:
            # Execute tasks concurrently
            results = executor.execute_concurrent_tasks(tasks)
            
            # Should have results for all tasks
            self.assertEqual(len(results), len(tasks))
            
            # All results should be strings containing "Completed"
            for result in results:
                self.assertIsInstance(result, str)
                self.assertIn("Completed", result)
                
        except Exception as e:
            self.fail(f"Concurrent task processing failed: {e}")

def create_example_test_suite():
    """Create a test suite for all example usage tests."""
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTest(unittest.makeSuite(TestExampleUsage))
    suite.addTest(unittest.makeSuite(TestIntegrationWithExistingCrewAI))
    suite.addTest(unittest.makeSuite(TestMigrationPatterns))
    suite.addTest(unittest.makeSuite(TestRealWorldUsageScenarios))
    
    return suite

if __name__ == "__main__":
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = create_example_test_suite()
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    if not result.wasSuccessful():
        sys.exit(1)
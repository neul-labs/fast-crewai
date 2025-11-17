"""
Comprehensive tests for the CrewAI Rust integration package.

This module provides thorough testing of all components to ensure
proper functionality and backward compatibility.
"""

import unittest
import tempfile
import os
import json
from fast_crewai import (
    HAS_RUST_IMPLEMENTATION,
    RustMemoryStorage,
    RustToolExecutor,
    RustTaskExecutor,
    AgentMessage,
    RustSQLiteWrapper
)
from fast_crewai.memory import RustMemoryStorage as MemoryStorage
from fast_crewai.tools import RustToolExecutor as ToolExecutor
from fast_crewai.tasks import RustTaskExecutor as TaskExecutor
from fast_crewai.serialization import AgentMessage as SerializableMessage
from fast_crewai.database import RustSQLiteWrapper as DatabaseWrapper
from fast_crewai.utils import (
    is_rust_available,
    get_rust_status,
    configure_rust_components,
    get_environment_info
)


class TestRustAvailability(unittest.TestCase):
    """Test Rust availability detection."""

    def test_has_rust_implementation(self):
        """Test that HAS_RUST_IMPLEMENTATION is properly defined."""
        self.assertIsInstance(HAS_RUST_IMPLEMENTATION, bool)

    def test_is_rust_available(self):
        """Test is_rust_available function."""
        self.assertEqual(is_rust_available(), HAS_RUST_IMPLEMENTATION)

    def test_get_rust_status(self):
        """Test get_rust_status function."""
        status = get_rust_status()
        self.assertIsInstance(status, dict)
        self.assertIn('available', status)
        self.assertIsInstance(status['available'], bool)
        if status['available']:
            self.assertIn('components', status)
            self.assertIsInstance(status['components'], dict)


class TestMemoryStorage(unittest.TestCase):
    """Test memory storage functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_storage = MemoryStorage()

    def test_initialization(self):
        """Test memory storage initialization."""
        self.assertIsInstance(self.memory_storage, MemoryStorage)

    def test_save_and_search(self):
        """Test saving and searching data."""
        # Test saving data
        self.memory_storage.save("test item 1", {"category": "test"})
        self.memory_storage.save("test item 2", {"category": "test"})
        
        # Test searching
        results = self.memory_storage.search("test")
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 2)
        
        # Test searching with limit
        limited_results = self.memory_storage.search("test", limit=1)
        self.assertIsInstance(limited_results, list)
        self.assertEqual(len(limited_results), 1)

    def test_get_all(self):
        """Test getting all items."""
        # Add some items
        self.memory_storage.save("item 1")
        self.memory_storage.save("item 2")
        
        # Get all items
        all_items = self.memory_storage.get_all()
        self.assertIsInstance(all_items, list)
        self.assertGreaterEqual(len(all_items), 2)

    def test_reset(self):
        """Test resetting memory storage."""
        # Add some items
        self.memory_storage.save("item 1")
        self.memory_storage.save("item 2")
        
        # Verify items exist
        self.assertGreater(len(self.memory_storage.get_all()), 0)
        
        # Reset storage
        self.memory_storage.reset()
        
        # Verify storage is empty
        self.assertEqual(len(self.memory_storage.get_all()), 0)

    def test_implementation_property(self):
        """Test implementation property."""
        implementation = self.memory_storage.implementation
        self.assertIn(implementation, ["rust", "python"])


class TestToolExecutor(unittest.TestCase):
    """Test tool executor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool_executor = ToolExecutor(max_recursion_depth=5)

    def test_initialization(self):
        """Test tool executor initialization."""
        self.assertIsInstance(self.tool_executor, ToolExecutor)
        self.assertEqual(self.tool_executor.max_recursion_depth, 5)

    def test_execute_tool(self):
        """Test executing a tool."""
        result = self.tool_executor.execute_tool("test_tool", {"param": "value"})
        self.assertIsInstance(result, str)
        self.assertIn("Executed test_tool with args", result)

    def test_execute_tool_with_string_args(self):
        """Test executing a tool with string arguments."""
        result = self.tool_executor.execute_tool("test_tool", "string_args")
        self.assertIsInstance(result, str)
        self.assertIn("Executed test_tool with args", result)

    def test_implementation_property(self):
        """Test implementation property."""
        implementation = self.tool_executor.implementation
        self.assertIn(implementation, ["rust", "python"])


class TestTaskExecutor(unittest.TestCase):
    """Test task executor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.task_executor = TaskExecutor()

    def test_initialization(self):
        """Test task executor initialization."""
        self.assertIsInstance(self.task_executor, TaskExecutor)

    def test_execute_concurrent_tasks(self):
        """Test executing concurrent tasks."""
        tasks = ["task1", "task2", "task3"]
        results = self.task_executor.execute_concurrent_tasks(tasks)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(tasks))
        for result in results:
            self.assertIsInstance(result, str)
            self.assertIn("Completed", result)

    def test_execute_task_with_timeout(self):
        """Test executing a task with timeout."""
        task = "test_task"
        result = self.task_executor.execute_task_with_timeout(task, timeout_seconds=5)
        self.assertIsInstance(result, str)
        self.assertIn("Completed", result)

    def test_implementation_property(self):
        """Test implementation property."""
        implementation = self.task_executor.implementation
        self.assertIn(implementation, ["rust", "python"])


class TestSerialization(unittest.TestCase):
    """Test serialization functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.message = SerializableMessage(
            id="1",
            sender="agent1",
            recipient="agent2",
            content="Hello, World!",
            timestamp=1234567890
        )

    def test_message_initialization(self):
        """Test message initialization."""
        self.assertIsInstance(self.message, SerializableMessage)
        self.assertEqual(self.message.id, "1")
        self.assertEqual(self.message.sender, "agent1")
        self.assertEqual(self.message.recipient, "agent2")
        self.assertEqual(self.message.content, "Hello, World!")
        self.assertEqual(self.message.timestamp, 1234567890)

    def test_message_serialization(self):
        """Test message serialization to JSON."""
        json_str = self.message.to_json()
        self.assertIsInstance(json_str, str)
        # Verify it's valid JSON
        data = json.loads(json_str)
        self.assertEqual(data['id'], "1")
        self.assertEqual(data['sender'], "agent1")
        self.assertEqual(data['recipient'], "agent2")
        self.assertEqual(data['content'], "Hello, World!")
        self.assertEqual(data['timestamp'], 1234567890)

    def test_message_deserialization(self):
        """Test message deserialization from JSON."""
        json_str = '{"id": "2", "sender": "agent2", "recipient": "agent1", "content": "Reply", "timestamp": 1234567891}'
        message = SerializableMessage.from_json(json_str)
        self.assertIsInstance(message, SerializableMessage)
        self.assertEqual(message.id, "2")
        self.assertEqual(message.sender, "agent2")
        self.assertEqual(message.recipient, "agent1")
        self.assertEqual(message.content, "Reply")
        self.assertEqual(message.timestamp, 1234567891)

    def test_batch_serialization(self):
        """Test batch serialization."""
        from fast_crewai.serialization import RustSerializer
        serializer = RustSerializer()
        
        messages = [
            {"id": "1", "sender": "agent1", "recipient": "agent2", "content": "Hello", "timestamp": 1000000},
            {"id": "2", "sender": "agent2", "recipient": "agent1", "content": "Hi", "timestamp": 1000001}
        ]
        
        serialized = serializer.serialize_batch(messages)
        self.assertIsInstance(serialized, list)
        self.assertEqual(len(serialized), 2)
        
        deserialized = serializer.deserialize_batch(serialized)
        self.assertIsInstance(deserialized, list)
        self.assertEqual(len(deserialized), 2)

    def test_implementation_property(self):
        """Test implementation property."""
        implementation = self.message.implementation
        self.assertIn(implementation, ["rust", "python"])


class TestDatabaseWrapper(unittest.TestCase):
    """Test database wrapper functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_wrapper = DatabaseWrapper(self.temp_db.name, pool_size=2)

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass

    def test_initialization(self):
        """Test database wrapper initialization."""
        self.assertIsInstance(self.db_wrapper, DatabaseWrapper)
        self.assertEqual(self.db_wrapper.db_path, self.temp_db.name)
        self.assertEqual(self.db_wrapper.pool_size, 2)

    def test_save_and_load_memory(self):
        """Test saving and loading memory."""
        # Save a memory entry
        self.db_wrapper.save_memory(
            task_description="Test task",
            metadata={"key": "value"},
            datetime="2023-01-01 12:00:00",
            score=0.95
        )
        
        # Load memories
        results = self.db_wrapper.load_memories("Test task", latest_n=5)
        self.assertIsInstance(results, list)
        # Note: Results may be empty if Rust implementation is not available

    def test_execute_query(self):
        """Test executing a query."""
        query = "SELECT 1 as test"
        params = {}
        results = self.db_wrapper.execute_query(query, params)
        self.assertIsInstance(results, list)
        # Results format depends on implementation

    def test_execute_update(self):
        """Test executing an update."""
        query = "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)"
        params = {}
        affected_rows = self.db_wrapper.execute_update(query, params)
        self.assertIsInstance(affected_rows, int)

    def test_execute_batch(self):
        """Test executing a batch of queries."""
        queries = [
            ("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)", {}),
            ("INSERT INTO test_table (name) VALUES (?)", {"name": "test"})
        ]
        results = self.db_wrapper.execute_batch(queries)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(queries))

    def test_reset(self):
        """Test resetting the database."""
        # Reset should not raise an exception
        self.db_wrapper.reset()

    def test_implementation_property(self):
        """Test implementation property."""
        implementation = self.db_wrapper.implementation
        self.assertIn(implementation, ["rust", "python"])


class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment configuration utilities."""

    def test_get_environment_info(self):
        """Test getting environment information."""
        env_info = get_environment_info()
        self.assertIsInstance(env_info, dict)
        self.assertIn('rust_available', env_info)
        self.assertIsInstance(env_info['rust_available'], bool)

    def test_configure_rust_components(self):
        """Test configuring Rust components."""
        # Save original environment
        original_memory = os.environ.get('FAST_CREWAI_MEMORY')
        original_tools = os.environ.get('FAST_CREWAI_TOOLS')
        
        try:
            # Configure components
            configure_rust_components(memory=True, tools=False)
            
            # Check environment variables
            self.assertEqual(os.environ.get('FAST_CREWAI_MEMORY'), 'true')
            self.assertEqual(os.environ.get('FAST_CREWAI_TOOLS'), 'false')
        finally:
            # Restore original environment
            if original_memory is not None:
                os.environ['FAST_CREWAI_MEMORY'] = original_memory
            elif 'FAST_CREWAI_MEMORY' in os.environ:
                del os.environ['FAST_CREWAI_MEMORY']
                
            if original_tools is not None:
                os.environ['FAST_CREWAI_TOOLS'] = original_tools
            elif 'FAST_CREWAI_TOOLS' in os.environ:
                del os.environ['FAST_CREWAI_TOOLS']


class TestIntegration(unittest.TestCase):
    """Test integration between components."""

    def test_memory_storage_with_rust_backend(self):
        """Test memory storage with Rust backend when available."""
        # This test verifies that the memory storage can be instantiated
        # and works regardless of whether Rust is available
        storage = RustMemoryStorage()
        self.assertIsInstance(storage, RustMemoryStorage)
        
        # Test basic operations
        storage.save("integration test", {"type": "integration"})
        results = storage.search("integration")
        self.assertIsInstance(results, list)

    def test_tool_executor_with_rust_backend(self):
        """Test tool executor with Rust backend when available."""
        executor = RustToolExecutor(max_recursion_depth=10)
        self.assertIsInstance(executor, RustToolExecutor)
        
        # Test basic operation
        result = executor.execute_tool("integration_test", {})
        self.assertIsInstance(result, str)

    def test_task_executor_with_rust_backend(self):
        """Test task executor with Rust backend when available."""
        executor = RustTaskExecutor()
        self.assertIsInstance(executor, RustTaskExecutor)
        
        # Test basic operation
        results = executor.execute_concurrent_tasks(["integration_test"])
        self.assertIsInstance(results, list)

    def test_agent_message_with_rust_backend(self):
        """Test agent message with Rust backend when available."""
        message = AgentMessage("1", "sender", "recipient", "content", 1234567890)
        self.assertIsInstance(message, AgentMessage)
        
        # Test serialization
        json_str = message.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        message2 = AgentMessage.from_json(json_str)
        self.assertIsInstance(message2, AgentMessage)

    def test_database_wrapper_with_rust_backend(self):
        """Test database wrapper with Rust backend when available."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db.close()
            try:
                db = RustSQLiteWrapper(temp_db.name)
                self.assertIsInstance(db, RustSQLiteWrapper)
            finally:
                try:
                    os.unlink(temp_db.name)
                except:
                    pass


def suite():
    """Create a test suite for all tests."""
    test_suite = unittest.TestSuite()
    
    # Add all test classes to the suite
    test_suite.addTest(unittest.makeSuite(TestRustAvailability))
    test_suite.addTest(unittest.makeSuite(TestMemoryStorage))
    test_suite.addTest(unittest.makeSuite(TestToolExecutor))
    test_suite.addTest(unittest.makeSuite(TestTaskExecutor))
    test_suite.addTest(unittest.makeSuite(TestSerialization))
    test_suite.addTest(unittest.makeSuite(TestDatabaseWrapper))
    test_suite.addTest(unittest.makeSuite(TestEnvironmentConfiguration))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    return test_suite


if __name__ == "__main__":
    # Run all tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())



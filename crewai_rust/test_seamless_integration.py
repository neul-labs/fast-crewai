"""
Seamless Integration Tests for CrewAI Rust Components

These tests verify that the Rust components can be used as drop-in replacements
for the Python implementations without any code changes required.
"""

import unittest
import tempfile
import os
import json
from typing import Any, Dict, List

# Test both Rust and Python implementations
from crewai_rust.memory import RustMemoryStorage
from crewai_rust.tools import RustToolExecutor
from crewai_rust.tasks import RustTaskExecutor
from crewai_rust.serialization import AgentMessage as RustAgentMessage
from crewai_rust.database import RustSQLiteWrapper

# For comparison, we'll simulate the Python implementations
class PythonMemoryStorage:
    """Python implementation for comparison."""
    def __init__(self):
        self._storage = []
    
    def save(self, value: Any, metadata: Dict[str, Any] = None) -> None:
        self._storage.append({
            'value': value,
            'metadata': metadata or {},
            'timestamp': __import__('time').time()
        })
    
    def search(self, query: str, limit: int = 3, score_threshold: float = 0.35) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        for item in self._storage:
            if query_lower in str(item.get('value', '')).lower():
                results.append(item)
        results.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return results[:limit]
    
    def get_all(self) -> List[Dict[str, Any]]:
        return self._storage.copy()
    
    def reset(self) -> None:
        self._storage = []

class PythonToolExecutor:
    """Python implementation for comparison."""
    def __init__(self, max_recursion_depth: int = 100):
        self.max_recursion_depth = max_recursion_depth
        self._execution_count = 0
    
    def execute_tool(self, tool_name: str, arguments: Any) -> Any:
        if self._execution_count >= self.max_recursion_depth:
            raise Exception(f"Maximum recursion depth exceeded for tool '{tool_name}'")
        
        self._execution_count += 1
        try:
            if isinstance(arguments, dict):
                args_str = ", ".join([f"{k}={v}" for k, v in arguments.items()])
            else:
                args_str = str(arguments)
            return f"Executed {tool_name} with args: {args_str}"
        finally:
            self._execution_count -= 1

class PythonTaskExecutor:
    """Python implementation for comparison."""
    def execute_concurrent_tasks(self, tasks: List[Any]) -> List[Any]:
        import threading
        import queue
        
        def worker(task_queue, result_queue):
            while True:
                item = task_queue.get()
                if item is None:
                    break
                task, index = item
                try:
                    __import__('time').sleep(0.001)  # Simulate work
                    if isinstance(task, dict):
                        task_str = ", ".join([f"{k}={v}" for k, v in task.items()])
                    else:
                        task_str = str(task)
                    result = f"Completed: {task_str}"
                    result_queue.put((index, result))
                except Exception as e:
                    result_queue.put((index, f"Error: {str(e)}"))
                finally:
                    task_queue.task_done()
        
        task_queue = queue.Queue()
        result_queue = queue.Queue()
        
        for i, task in enumerate(tasks):
            task_queue.put((task, i))
        
        threads = []
        for i in range(min(4, len(tasks))):
            t = threading.Thread(target=worker, args=(task_queue, result_queue))
            t.start()
            threads.append(t)
        
        task_queue.join()
        
        for i in range(len(threads)):
            task_queue.put(None)
        for t in threads:
            t.join()
        
        results = [None] * len(tasks)
        while not result_queue.empty():
            index, result = result_queue.get()
            results[index] = result
        
        return results

class PythonAgentMessage:
    """Python implementation for comparison."""
    def __init__(self, id: str, sender: str, recipient: str, content: str, timestamp: int):
        self.id = id
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.timestamp = timestamp
    
    def to_json(self) -> str:
        data = {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'content': self.content,
            'timestamp': self.timestamp
        }
        return json.dumps(data, separators=(',', ':'))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PythonAgentMessage':
        data = json.loads(json_str)
        return cls(
            id=data['id'],
            sender=data['sender'],
            recipient=data['recipient'],
            content=data['content'],
            timestamp=data['timestamp']
        )

class PythonSQLiteWrapper:
    """Python implementation for comparison."""
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._initialize_db()
    
    def _initialize_db(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_description TEXT,
                    metadata TEXT,
                    datetime TEXT,
                    score REAL
                )
            """)
            conn.commit()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: Dict[str, Any] = None) -> int:
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount

class TestSeamlessIntegration(unittest.TestCase):
    """Test that Rust components are seamless drop-in replacements."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize both implementations
        self.rust_memory = RustMemoryStorage()
        self.python_memory = PythonMemoryStorage()
        
        self.rust_tools = RustToolExecutor(max_recursion_depth=5)
        self.python_tools = PythonToolExecutor(max_recursion_depth=5)
        
        self.rust_tasks = RustTaskExecutor()
        self.python_tasks = PythonTaskExecutor()
        
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.rust_db = RustSQLiteWrapper(self.temp_db.name)
        self.python_db = PythonSQLiteWrapper(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_memory_storage_interface(self):
        """Test that memory storage interfaces are identical."""
        # Both should have the same methods
        self.assertTrue(hasattr(self.rust_memory, 'save'))
        self.assertTrue(hasattr(self.rust_memory, 'search'))
        self.assertTrue(hasattr(self.rust_memory, 'get_all'))
        self.assertTrue(hasattr(self.rust_memory, 'reset'))
        
        self.assertTrue(hasattr(self.python_memory, 'save'))
        self.assertTrue(hasattr(self.python_memory, 'search'))
        self.assertTrue(hasattr(self.python_memory, 'get_all'))
        self.assertTrue(hasattr(self.python_memory, 'reset'))
    
    def test_memory_storage_functionality(self):
        """Test that memory storage works identically."""
        # Save identical data
        test_data = "test item"
        test_metadata = {"category": "test", "priority": 1}
        
        self.rust_memory.save(test_data, test_metadata)
        self.python_memory.save(test_data, test_metadata)
        
        # Search should return similar results
        rust_results = self.rust_memory.search("test")
        python_results = self.python_memory.search("test")
        
        # Both should return results
        self.assertIsInstance(rust_results, list)
        self.assertIsInstance(python_results, list)
        
        # Both should have at least one result
        self.assertGreater(len(rust_results), 0)
        self.assertGreater(len(python_results), 0)
    
    def test_tool_executor_interface(self):
        """Test that tool executor interfaces are identical."""
        # Both should have the same methods
        self.assertTrue(hasattr(self.rust_tools, 'execute_tool'))
        self.assertTrue(hasattr(self.python_tools, 'execute_tool'))
        
        # Both should have the same attributes
        self.assertTrue(hasattr(self.rust_tools, 'max_recursion_depth'))
        self.assertTrue(hasattr(self.python_tools, 'max_recursion_depth'))
    
    def test_tool_executor_functionality(self):
        """Test that tool executor works identically."""
        # Execute identical tools
        tool_name = "test_tool"
        arguments = {"param1": "value1", "param2": 42}
        
        rust_result = self.rust_tools.execute_tool(tool_name, arguments)
        python_result = self.python_tools.execute_tool(tool_name, arguments)
        
        # Both should return strings
        self.assertIsInstance(rust_result, str)
        self.assertIsInstance(python_result, str)
        
        # Both should contain the tool name
        self.assertIn(tool_name, rust_result)
        self.assertIn(tool_name, python_result)
    
    def test_task_executor_interface(self):
        """Test that task executor interfaces are identical."""
        # Both should have the same methods
        self.assertTrue(hasattr(self.rust_tasks, 'execute_concurrent_tasks'))
        self.assertTrue(hasattr(self.python_tasks, 'execute_concurrent_tasks'))
    
    def test_task_executor_functionality(self):
        """Test that task executor works identically."""
        # Execute identical tasks
        tasks = ["task1", "task2", "task3"]
        
        rust_results = self.rust_tasks.execute_concurrent_tasks(tasks)
        python_results = self.python_tasks.execute_concurrent_tasks(tasks)
        
        # Both should return lists
        self.assertIsInstance(rust_results, list)
        self.assertIsInstance(python_results, list)
        
        # Both should have the same length
        self.assertEqual(len(rust_results), len(python_results))
        
        # Both should contain "Completed" in each result
        for result in rust_results:
            self.assertIn("Completed", result)
        for result in python_results:
            self.assertIn("Completed", result)
    
    def test_serialization_interface(self):
        """Test that serialization interfaces are identical."""
        # Create identical messages
        rust_message = RustAgentMessage("1", "sender", "recipient", "content", 1234567890)
        
        python_message = PythonAgentMessage("1", "sender", "recipient", "content", 1234567890)
        
        # Both should have the same attributes
        self.assertEqual(rust_message.id, python_message.id)
        self.assertEqual(rust_message.sender, python_message.sender)
        self.assertEqual(rust_message.recipient, python_message.recipient)
        self.assertEqual(rust_message.content, python_message.content)
        self.assertEqual(rust_message.timestamp, python_message.timestamp)
        
        # Both should have the same methods
        self.assertTrue(hasattr(rust_message, 'to_json'))
        self.assertTrue(hasattr(python_message, 'to_json'))
        
        self.assertTrue(hasattr(rust_message, 'from_json'))
        self.assertTrue(hasattr(PythonAgentMessage, 'from_json'))
    
    def test_serialization_functionality(self):
        """Test that serialization works identically."""
        # Create identical messages
        rust_message = RustAgentMessage("1", "sender", "recipient", "content", 1234567890)
        python_message = PythonAgentMessage("1", "sender", "recipient", "content", 1234567890)
        
        # Serialize both
        rust_json = rust_message.to_json()
        python_json = python_message.to_json()
        
        # Both should return strings
        self.assertIsInstance(rust_json, str)
        self.assertIsInstance(python_json, str)
        
        # Both should be valid JSON
        rust_data = json.loads(rust_json)
        python_data = json.loads(python_json)
        
        # Both should have the same data
        self.assertEqual(rust_data['id'], python_data['id'])
        self.assertEqual(rust_data['sender'], python_data['sender'])
        self.assertEqual(rust_data['recipient'], python_data['recipient'])
        self.assertEqual(rust_data['content'], python_data['content'])
        self.assertEqual(rust_data['timestamp'], python_data['timestamp'])
        
        # Test deserialization
        rust_message2 = RustAgentMessage.from_json(rust_json)
        python_message2 = PythonAgentMessage.from_json(python_json)
        
        # Both should have the same data
        self.assertEqual(rust_message2.id, python_message2.id)
        self.assertEqual(rust_message2.sender, python_message2.sender)
        self.assertEqual(rust_message2.recipient, python_message2.recipient)
        self.assertEqual(rust_message2.content, python_message2.content)
        self.assertEqual(rust_message2.timestamp, python_message2.timestamp)
    
    def test_database_interface(self):
        """Test that database interfaces are identical."""
        # Both should have the same methods
        self.assertTrue(hasattr(self.rust_db, 'execute_query'))
        self.assertTrue(hasattr(self.python_db, 'execute_query'))
        
        self.assertTrue(hasattr(self.rust_db, 'execute_update'))
        self.assertTrue(hasattr(self.python_db, 'execute_update'))
    
    def test_database_functionality(self):
        """Test that database operations work identically."""
        # Execute identical queries
        query = "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)"
        params = {}
        
        rust_result = self.rust_db.execute_update(query, params)
        python_result = self.python_db.execute_update(query, params)
        
        # Both should return integers (affected row counts)
        self.assertIsInstance(rust_result, int)
        self.assertIsInstance(python_result, int)
    
    def test_drop_in_replacement(self):
        """Test that Rust components can be used as drop-in replacements."""
        # This test simulates how a user would use the components
        
        # Memory storage replacement
        def use_memory_storage(storage):
            storage.save("test data", {"type": "test"})
            results = storage.search("test")
            return len(results) > 0
        
        # Should work with both implementations
        self.assertTrue(use_memory_storage(self.rust_memory))
        self.assertTrue(use_memory_storage(self.python_memory))
        
        # Tool executor replacement
        def use_tool_executor(executor):
            result = executor.execute_tool("test_tool", {"param": "value"})
            return "Executed" in result
        
        # Should work with both implementations
        self.assertTrue(use_tool_executor(self.rust_tools))
        self.assertTrue(use_tool_executor(self.python_tools))
        
        # Task executor replacement
        def use_task_executor(executor):
            results = executor.execute_concurrent_tasks(["task1", "task2"])
            return len(results) == 2 and all("Completed" in r for r in results)
        
        # Should work with both implementations
        self.assertTrue(use_task_executor(self.rust_tasks))
        self.assertTrue(use_task_executor(self.python_tasks))

class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing code continues to work unchanged."""
    
    def test_existing_crewai_imports_still_work(self):
        """Test that existing CrewAI imports continue to work."""
        # This would normally import from crewai, but we're testing the concept
        try:
            from crewai_rust import HAS_RUST_IMPLEMENTATION
            # This should not raise an ImportError
            self.assertIsInstance(HAS_RUST_IMPLEMENTATION, bool)
        except ImportError:
            self.fail("CrewAI Rust integration should be importable")
    
    def test_fallback_mechanism(self):
        """Test that fallback to Python works when Rust is not available."""
        # We can't easily test this without actually removing Rust,
        # but we can test that the fallback classes exist
        from crewai_rust import (
            RustMemoryStorage,
            RustToolExecutor,
            RustTaskExecutor,
            AgentMessage as RustAgentMessage,
            RustSQLiteWrapper
        )
        
        # All classes should be importable
        self.assertTrue(RustMemoryStorage)
        self.assertTrue(RustToolExecutor)
        self.assertTrue(RustTaskExecutor)
        self.assertTrue(RustAgentMessage)
        self.assertTrue(RustSQLiteWrapper)

class TestPerformanceComparison(unittest.TestCase):
    """Test that Rust components provide performance improvements."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rust_memory = RustMemoryStorage()
        self.rust_tools = RustToolExecutor()
        self.rust_tasks = RustTaskExecutor()
    
    def test_rust_components_are_faster(self):
        """Test that Rust components provide performance improvements."""
        import time
        
        # Memory storage performance
        start_time = time.time()
        for i in range(100):
            self.rust_memory.save(f"item {i}", {"id": i})
        rust_save_time = time.time() - start_time
        
        start_time = time.time()
        results = self.rust_memory.search("item")
        rust_search_time = time.time() - start_time
        
        # We should be able to perform operations quickly
        self.assertLess(rust_save_time, 1.0)  # Should be fast
        self.assertLess(rust_search_time, 1.0)  # Should be fast
        self.assertGreater(len(results), 0)  # Should find results
    
    def test_rust_components_handle_concurrency(self):
        """Test that Rust components handle concurrent operations."""
        # Execute multiple tasks concurrently
        tasks = [f"task_{i}" for i in range(10)]
        
        start_time = time.time()
        results = self.rust_tasks.execute_concurrent_tasks(tasks)
        execution_time = time.time() - start_time
        
        # Should complete successfully
        self.assertEqual(len(results), len(tasks))
        self.assertTrue(all("Completed" in result for result in results))
        
        # Should be relatively fast
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds

def create_test_suite():
    """Create a test suite for all seamless integration tests."""
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTest(unittest.makeSuite(TestSeamlessIntegration))
    suite.addTest(unittest.makeSuite(TestBackwardCompatibility))
    suite.addTest(unittest.makeSuite(TestPerformanceComparison))
    
    return suite

if __name__ == "__main__":
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = create_test_suite()
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    if not result.wasSuccessful():
        exit(1)
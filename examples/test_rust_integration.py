import unittest
from crewai_rust import RustMemoryStorage, RustToolExecutor, AgentMessage, RustTaskExecutor

class TestRustIntegration(unittest.TestCase):
    
    def test_memory_storage(self):
        """Test the Rust memory storage component"""
        memory = RustMemoryStorage()
        memory.save("test item 1")
        memory.save("test item 2")
        
        all_items = memory.get_all()
        self.assertEqual(len(all_items), 2)
        self.assertIn("test item 1", all_items)
        self.assertIn("test item 2", all_items)
        
        search_results = memory.search("test")
        self.assertEqual(len(search_results), 2)
        
        search_results = memory.search("item 1")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0], "test item 1")
    
    def test_tool_executor(self):
        """Test the Rust tool executor component"""
        executor = RustToolExecutor(5)  # Max recursion depth of 5
        
        # Test normal execution
        result = executor.execute_tool("test_tool", "arg1,arg2")
        self.assertIn("Executed test_tool with args: arg1,arg2", result)
        
        # Test recursion limit
        for i in range(5):
            executor.execute_tool(f"tool_{i}", f"args_{i}")
        
        # This should fail due to recursion limit
        with self.assertRaises(RuntimeError):
            executor.execute_tool("overflow_tool", "overflow_args")
    
    def test_agent_message_serialization(self):
        """Test the Rust serialization component"""
        message = AgentMessage("1", "agent1", "agent2", "Hello!", 1234567890)
        
        # Test serialization
        json_str = message.to_json()
        self.assertIn("agent1", json_str)
        self.assertIn("agent2", json_str)
        self.assertIn("Hello!", json_str)
        
        # Test deserialization
        message2 = AgentMessage.from_json(json_str)
        self.assertEqual(message.id, message2.id)
        self.assertEqual(message.sender, message2.sender)
        self.assertEqual(message.recipient, message2.recipient)
        self.assertEqual(message.content, message2.content)
        self.assertEqual(message.timestamp, message2.timestamp)
    
    def test_task_executor(self):
        """Test the Rust concurrent task executor component"""
        executor = RustTaskExecutor()
        
        tasks = [f"task_{i}" for i in range(10)]
        results = executor.execute_concurrent_tasks(tasks)
        
        self.assertEqual(len(results), 10)
        for i, result in enumerate(results):
            self.assertIn(f"Completed: task_{i}", result)

if __name__ == "__main__":
    unittest.main()
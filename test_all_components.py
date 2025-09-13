"""
Test script to verify all component shimming works correctly.
"""

def test_all_component_imports():
    """Test that we can import all crewai-rust components."""
    try:
        from crewai_rust.memory import RustMemoryStorage
        from crewai_rust.tools import RustToolExecutor
        from crewai_rust.tasks import RustTaskExecutor
        from crewai_rust.database import RustSQLiteWrapper
        from crewai_rust.serialization import AgentMessage
        print("✅ Successfully imported all crewai-rust components")
        return True
    except Exception as e:
        print(f"❌ Failed to import crewai-rust components: {e}")
        return False

def test_shim_enable_verbose():
    """Test that we can enable shimming with verbose output."""
    try:
        from crewai_rust.shim import enable_rust_acceleration
        result = enable_rust_acceleration(verbose=True)
        print(f"✅ enable_rust_acceleration(verbose=True) returned: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed to call enable_rust_acceleration with verbose: {e}")
        return False

def test_component_functionality():
    """Test basic functionality of shimmed components."""
    try:
        # Test memory storage
        from crewai_rust.memory import RustMemoryStorage
        memory = RustMemoryStorage()
        memory.save("test value", {"test": "metadata"})
        results = memory.search("test")
        print(f"✅ Memory storage test: {len(results)} results found")
        
        # Test tool executor
        from crewai_rust.tools import RustToolExecutor
        tool_executor = RustToolExecutor()
        result = tool_executor.execute_tool("test_tool", {"param": "value"})
        print(f"✅ Tool executor test: {result[:50]}...")
        
        # Test task executor
        from crewai_rust.tasks import RustTaskExecutor
        task_executor = RustTaskExecutor()
        results = task_executor.execute_concurrent_tasks(["task1", "task2"])
        print(f"✅ Task executor test: {len(results)} tasks completed")
        
        # Test serialization
        from crewai_rust.serialization import AgentMessage
        message = AgentMessage("1", "sender", "recipient", "content", 1234567890)
        json_str = message.to_json()
        message2 = AgentMessage.from_json(json_str)
        print(f"✅ Serialization test: {message2.id}")
        
        # Test database
        from crewai_rust.database import RustSQLiteWrapper
        import tempfile
        import os
        db_path = tempfile.mktemp(suffix='.db')
        db = RustSQLiteWrapper(db_path, pool_size=2)
        db.save_memory("test task", {"key": "value"}, "2023-01-01", 0.95)
        results = db.load_memories("test task")
        print(f"✅ Database test: {len(results) if results else 0} records found")
        
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)
            
        return True
    except Exception as e:
        print(f"❌ Component functionality test failed: {e}")
        return False

def test_shim_disable():
    """Test that we can disable shimming."""
    try:
        from crewai_rust.shim import disable_rust_acceleration
        result = disable_rust_acceleration()
        print(f"✅ disable_rust_acceleration() returned: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed to call disable_rust_acceleration: {e}")
        return False

if __name__ == "__main__":
    print("Testing crewai-rust all components shimming functionality...")
    print("")
    
    tests = [
        test_all_component_imports,
        test_shim_enable_verbose,
        test_component_functionality,
        test_shim_disable
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print("")
    
    print(f"Tests passed: {passed}/{len(tests)}")
    if passed == len(tests):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed.")
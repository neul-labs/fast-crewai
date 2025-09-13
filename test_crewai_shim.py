"""
Test script to verify the shim functionality works with correct CrewAI class names.
"""

def test_crewai_import():
    """Test that we can import CrewAI modules."""
    try:
        import crewai
        print("✅ Successfully imported crewai")
        return True
    except Exception as e:
        print(f"❌ Failed to import crewai: {e}")
        return False

def test_memory_module_import():
    """Test that we can import CrewAI memory modules."""
    try:
        import crewai.memory.storage.rag_storage
        import crewai.memory.short_term.short_term_memory
        import crewai.memory.memory
        print("✅ Successfully imported CrewAI memory modules")
        return True
    except Exception as e:
        print(f"❌ Failed to import CrewAI memory modules: {e}")
        return False

def test_shim_with_crewai():
    """Test that we can shim with actual CrewAI classes."""
    try:
        # First import CrewAI
        import crewai
        
        # Then import and enable shimming
        from crewai_rust.shim import enable_rust_acceleration
        result = enable_rust_acceleration()
        print(f"✅ enable_rust_acceleration() returned: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed to test shimming with CrewAI: {e}")
        return False

if __name__ == "__main__":
    print("Testing crewai-rust shim functionality with actual CrewAI class names...")
    print("")
    
    tests = [
        test_crewai_import,
        test_memory_module_import,
        test_shim_with_crewai
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
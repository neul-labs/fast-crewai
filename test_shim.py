"""
Test script to verify the shim functionality works correctly.
"""

def test_shim_import():
    """Test that we can import the shim module."""
    try:
        import crewai_rust.shim
        print("✅ Successfully imported crewai_rust.shim")
        return True
    except Exception as e:
        print(f"❌ Failed to import crewai_rust.shim: {e}")
        return False

def test_shim_enable():
    """Test that we can enable the shim."""
    try:
        from crewai_rust.shim import enable_rust_acceleration
        result = enable_rust_acceleration()
        print(f"✅ enable_rust_acceleration() returned: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed to call enable_rust_acceleration(): {e}")
        return False

def test_environment_variable():
    """Test environment variable functionality."""
    import os
    original = os.environ.get('CREWAI_RUST_ACCELERATION')
    
    try:
        # Temporarily set the environment variable
        os.environ['CREWAI_RUST_ACCELERATION'] = '1'
        
        # Reload the module to test auto-enable
        import sys
        if 'crewai_rust' in sys.modules:
            del sys.modules['crewai_rust']
            
        import crewai_rust
        print("✅ Environment variable auto-enable test completed")
        return True
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False
    finally:
        # Restore original environment
        if original is None:
            os.environ.pop('CREWAI_RUST_ACCELERATION', None)
        else:
            os.environ['CREWAI_RUST_ACCELERATION'] = original

if __name__ == "__main__":
    print("Testing crewai-rust shim functionality...")
    print("")
    
    tests = [
        test_shim_import,
        test_shim_enable,
        test_environment_variable
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
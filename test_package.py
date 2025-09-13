"""
Test to verify that the crewai-rust package can be imported and basic functionality works.
"""

def test_import():
    """Test that we can import the package."""
    try:
        import crewai_rust
        print("Successfully imported crewai_rust")
        print(f"Version: {crewai_rust.__version__}")
        print(f"Has Rust implementation: {crewai_rust.HAS_RUST_IMPLEMENTATION}")
        return True
    except Exception as e:
        print(f"Failed to import crewai_rust: {e}")
        return False

if __name__ == "__main__":
    success = test_import()
    if success:
        print("Package test PASSED")
    else:
        print("Package test FAILED")
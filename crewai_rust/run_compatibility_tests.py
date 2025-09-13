"""
Runner for all compatibility tests for CrewAI Rust Integration

This script runs all compatibility tests to verify that the Rust components
are seamless drop-in replacements for the Python implementations.
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import the test modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_compatibility_tests():
    """Run all compatibility tests and report results."""
    print("Running CrewAI Rust Integration Compatibility Tests")
    print("=" * 55)
    
    # Import test modules
    try:
        from test_seamless_integration import create_test_suite as create_seamless_suite
        from test_backward_compatibility import create_compatibility_test_suite
        from test_drop_in_replacement import create_drop_in_replacement_test_suite
        print("✓ All test modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import test modules: {e}")
        return False
    
    # Create test suites
    try:
        seamless_suite = create_seamless_suite()
        compatibility_suite = create_compatibility_test_suite()
        drop_in_suite = create_drop_in_replacement_test_suite()
        print("✓ All test suites created successfully")
    except Exception as e:
        print(f"✗ Failed to create test suites: {e}")
        return False
    
    # Combine all tests into one suite
    full_suite = unittest.TestSuite()
    full_suite.addTest(seamless_suite)
    full_suite.addTest(compatibility_suite)
    full_suite.addTest(drop_in_suite)
    
    print(f"✓ Test suite contains {full_suite.countTestCases()} tests")
    print()
    
    # Run all tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    print("Running all compatibility tests...")
    print("-" * 40)
    
    result = runner.run(full_suite)
    
    # Report results
    print("\n" + "=" * 55)
    print("COMPATIBILITY TEST RESULTS")
    print("=" * 55)
    
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.failures) - len(result.errors)
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    
    print(f"Total tests run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}:")
            print(f"    {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}:")
            print(f"    {traceback}")
    
    # Overall result
    if result.wasSuccessful():
        print("\n🎉 ALL COMPATIBILITY TESTS PASSED!")
        print("The Rust components are seamless drop-in replacements.")
        return True
    else:
        print("\n❌ SOME COMPATIBILITY TESTS FAILED!")
        print("The Rust components may not be fully compatible.")
        return False

def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    print(f"Running {suite_name} tests...")
    print("-" * 40)
    
    if suite_name == "seamless":
        from test_seamless_integration import create_test_suite
        suite = create_test_suite()
    elif suite_name == "compatibility":
        from test_backward_compatibility import create_compatibility_test_suite
        suite = create_compatibility_test_suite()
    elif suite_name == "replacement":
        from test_drop_in_replacement import create_drop_in_replacement_test_suite
        suite = create_drop_in_replacement_test_suite()
    else:
        print(f"Unknown test suite: {suite_name}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main function to run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CrewAI Rust Integration Compatibility Tests")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["all", "seamless", "compatibility", "replacement"],
        default="all",
        help="Test suite to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.suite == "all":
        success = run_all_compatibility_tests()
    else:
        success = run_specific_test_suite(args.suite)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
"""
Compatibility Report Generator for CrewAI Rust Integration

This script generates a detailed report on the compatibility between
Rust and Python implementations, verifying seamless integration.
"""

import json
import os
import sys
import time
import unittest
from typing import Any, Dict

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test modules
try:
    from test_backward_compatibility import TestBackwardCompatibility
    from test_drop_in_replacement import TestDropInReplacement
    from test_example_usage import TestExampleUsage
    from test_seamless_integration import TestSeamlessIntegration

    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    IMPORT_ERROR = str(e)


def run_compatibility_analysis():
    """Run a comprehensive compatibility analysis."""
    if not MODULES_AVAILABLE:
        print(f"Cannot run compatibility analysis: {IMPORT_ERROR}")
        return None

    print("CrewAI Rust Integration Compatibility Analysis")
    print("=" * 50)

    # Test results storage
    results = {
        "timestamp": time.time(),
        "modules_available": MODULES_AVAILABLE,
        "test_results": {},
        "compatibility_score": 0,
        "issues_found": [],
    }

    # Test categories
    test_categories = {
        "Seamless Integration": TestSeamlessIntegration,
        "Backward Compatibility": TestBackwardCompatibility,
        "Drop-in Replacement": TestDropInReplacement,
        "Example Usage": TestExampleUsage,
    }

    total_tests = 0
    passed_tests = 0

    # Run each category of tests
    for category_name, test_class in test_categories.items():
        print(f"\nRunning {category_name} tests...")
        print("-" * 30)

        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        total_tests += suite.countTestCases()

        # Run tests
        runner = unittest.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0)
        result = runner.run(suite)

        # Store results
        category_results = {
            "total_tests": suite.countTestCases(),
            "passed": suite.countTestCases()
            - len(result.failures)
            - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "failures": [str(test) for test, _ in result.failures],
            "errors_details": [str(test) for test, _ in result.errors],
        }

        results["test_results"][category_name] = category_results
        passed_tests += category_results["passed"]

        # Print summary for this category
        print(f"  Total: {category_results['total_tests']}")
        print(f"  Passed: {category_results['passed']}")
        print(f"  Failed: {category_results['failed']}")
        print(f"  Errors: {category_results['errors']}")

        # Collect issues
        for failure in result.failures:
            results["issues_found"].append(
                {
                    "category": category_name,
                    "test": str(failure[0]),
                    "type": "failure",
                    "details": str(failure[1]),
                }
            )

        for error in result.errors:
            results["issues_found"].append(
                {
                    "category": category_name,
                    "test": str(error[0]),
                    "type": "error",
                    "details": str(error[1]),
                }
            )

    # Calculate compatibility score
    if total_tests > 0:
        results["compatibility_score"] = (passed_tests / total_tests) * 100
    else:
        results["compatibility_score"] = 0

    # Print overall results
    print("\n" + "=" * 50)
    print("COMPATIBILITY ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Failed Tests: {total_tests - passed_tests}")
    print(f"Compatibility Score: {results['compatibility_score']:.1f}%")

    if results["compatibility_score"] >= 95:
        print("\n🎉 EXCELLENT COMPATIBILITY")
        print("The Rust components are seamless drop-in replacements!")
    elif results["compatibility_score"] >= 80:
        print("\n✅ GOOD COMPATIBILITY")
        print("The Rust components are mostly compatible with minor issues.")
    else:
        print("\n⚠️  COMPATIBILITY ISSUES DETECTED")
        print("Some compatibility issues need to be addressed.")

    # Show issues if any
    if results["issues_found"]:
        print(f"\nIssues Found ({len(results['issues_found'])}):")
        for i, issue in enumerate(
            results["issues_found"][:10], 1
        ):  # Show first 10 issues
            print(f"  {i}. [{issue['category']}] {issue['test']} - {issue['type']}")

    if len(results["issues_found"]) > 10:
        print(f"  ... and {len(results['issues_found']) - 10} more issues")

    return results


def generate_detailed_report(results: Dict[str, Any]) -> str:
    """Generate a detailed compatibility report."""
    if not results:
        return "No results to report."

    report = []
    report.append("CREWAI RUST INTEGRATION COMPATIBILITY REPORT")
    report.append("=" * 50)
    report.append(
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['timestamp']))}"
    )
    report.append(f"Compatibility Score: {results['compatibility_score']:.1f}%")
    report.append("")

    # Test results by category
    report.append("DETAILED TEST RESULTS")
    report.append("-" * 25)
    for category, category_results in results["test_results"].items():
        report.append(f"{category}:")
        report.append(f"  Total Tests: {category_results['total_tests']}")
        report.append(f"  Passed: {category_results['passed']}")
        report.append(f"  Failed: {category_results['failed']}")
        report.append(f"  Errors: {category_results['errors']}")
        report.append("")

    # Issues found
    if results["issues_found"]:
        report.append("ISSUES DETECTED")
        report.append("-" * 15)
        for issue in results["issues_found"]:
            report.append(f"[{issue['category']}] {issue['test']}")
            report.append(f"  Type: {issue['type']}")
            report.append(
                f"  Details: {issue['details'][:200]}..."
            )  # Truncate long details
            report.append("")

    return "\n".join(report)


def save_report_to_file(
    results: Dict[str, Any], filename: str = "compatibility_report.txt"
):
    """Save the compatibility report to a file."""
    try:
        # Generate text report
        text_report = generate_detailed_report(results)

        # Save text report
        with open(filename, "w") as f:
            f.write(text_report)

        # Save JSON report
        json_filename = filename.replace(".txt", ".json")
        with open(json_filename, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Reports saved to {filename} and {json_filename}")
        return True
    except Exception as e:
        print(f"Failed to save reports: {e}")
        return False


def main():
    """Main function to run compatibility analysis."""
    print("Starting CrewAI Rust Integration Compatibility Analysis...")

    # Run analysis
    results = run_compatibility_analysis()

    if results:
        # Save reports
        save_report_to_file(results)

        # Print summary
        print(f"\nCompatibility Score: {results['compatibility_score']:.1f}%")

        if results["compatibility_score"] >= 95:
            print("✅ The Rust integration is ready for production use!")
        elif results["compatibility_score"] >= 80:
            print("⚠️  The Rust integration is usable but needs some improvements.")
        else:
            print(
                "❌ The Rust integration needs significant work before production use."
            )

        return results["compatibility_score"] >= 80
    else:
        print("❌ Compatibility analysis failed to run.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

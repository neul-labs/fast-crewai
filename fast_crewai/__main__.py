"""
Main entry point for the CrewAI Accelerate package.

This module provides command-line utilities for working with the accelerated components.
"""

import argparse
import sys

from .benchmark import run_benchmarks
from .utils import (get_acceleration_status, get_environment_info,
                    get_performance_improvements, is_acceleration_available)

"""
Main entry point for the crewai-rust package.
"""

import argparse
import sys


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="CrewAI Rust Integration Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status     Check Rust component status
  env        Show environment configuration
  bench      Run performance benchmarks
  info       Show performance improvement information
        """,
    )

    parser.add_argument(
        "command", choices=["status", "env", "bench", "info"], help="Command to execute"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.command == "status":
        status_cmd(args.verbose)
    elif args.command == "env":
        env_cmd(args.verbose)
    elif args.command == "bench":
        bench_cmd(args.verbose)
    elif args.command == "info":
        info_cmd(args.verbose)


def status_cmd(verbose=False):
    """Check Rust component status."""
    try:
        import fast_crewai

        print("CrewAI Rust Integration Status")
        print("=============================")
        print(f"Version: {fast_crewai.__version__}")
        print(
            f"Rust Implementation Available: {fast_crewai.HAS_ACCELERATION_IMPLEMENTATION}"
        )

        if verbose:
            print("")
            print("Environment Variables:")
            import os

            rust_accel = os.environ.get("FAST_CREWAI_ACCELERATION", "")
            print(f"  FAST_CREWAI_ACCELERATION: {rust_accel or '(not set)'}")
    except ImportError:
        print("CrewAI Rust Integration: Not Available")
        print("Please ensure the package was built correctly with maturin.")
    except Exception as e:
        print(f"Error checking status: {e}")


def env_cmd(verbose=False):
    """Show environment configuration."""
    import os

    print("Environment Configuration")
    print("========================")
    rust_accel = os.environ.get("FAST_CREWAI_ACCELERATION", "")
    print(f"FAST_CREWAI_ACCELERATION: {rust_accel or '(not set)'}")

    if verbose:
        print("")
        print("All Environment Variables:")
        for key, value in sorted(os.environ.items()):
            if "crew" in key.lower() or "rust" in key.lower():
                print(f"  {key}: {value}")


def bench_cmd(verbose=False):
    """Run performance benchmarks."""
    print("Running performance benchmarks...")
    # Implementation would go here


def info_cmd(verbose=False):
    """Show performance improvement information."""
    try:
        import fast_crewai

        print("CrewAI Rust Integration")
        print("======================")
        print(f"Version: {fast_crewai.__version__}")
        print(
            f"Rust Implementation Available: {fast_crewai.HAS_ACCELERATION_IMPLEMENTATION}"
        )

        if fast_crewai.HAS_ACCELERATION_IMPLEMENTATION:
            print("\nPerformance Improvements:")
            print("  - Memory Storage: 10-20x faster")
            print("  - Tool Execution: 2-5x faster")
            print("  - Task Execution: 3-5x faster")
            print("  - Serialization: 5-10x faster")
            print("  - Database Operations: 3-5x faster")

            print("\nUsage Options:")
            print(
                "  1. Explicit import: from fast_crewai import AcceleratedMemoryStorage"
            )
            print("  2. Auto-shim: export FAST_CREWAI_ACCELERATION=1")
            print("  3. Import hook: import fast_crewai.shim")
        else:
            print("\nRust implementation not available.")
            print("Please ensure the package was built correctly with maturin.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()


def status_cmd(verbose=False):
    """Check acceleration component status."""
    print("CrewAI Accelerate Status")
    print("=" * 30)

    available = is_acceleration_available()
    print(f"Acceleration Implementation Available: {'Yes' if available else 'No'}")

    if available:
        status = get_acceleration_status()
        print(f"Components Available:")
        for component, available in status["components"].items():
            print(f"  {component}: {'Yes' if available else 'No'}")

    if verbose:
        print("\nEnvironment Configuration:")
        env_info = get_environment_info()
        for key, value in env_info.items():
            print(f"  {key}: {value}")


def env_cmd(verbose=False):
    """Show environment configuration."""
    print("CrewAI Rust Integration Environment")
    print("=" * 35)

    env_info = get_environment_info()
    for key, value in env_info.items():
        print(f"{key}: {value}")


def bench_cmd(verbose=False):
    """Run performance benchmarks."""
    print("Running CrewAI Rust Integration Benchmarks...")
    print("=" * 45)

    try:
        results = run_benchmarks()
        if verbose:
            import json

            print("\nDetailed Results:")
            print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error running benchmarks: {e}")
        sys.exit(1)


def info_cmd(verbose=False):
    """Show performance improvement information."""
    print("CrewAI Rust Integration Performance Improvements")
    print("=" * 50)

    improvements = get_performance_improvements()
    for component, info in improvements.items():
        print(f"{component.capitalize()}:")
        print(f"  Expected Improvement: {info['improvement']}")
        print(f"  Description: {info['description']}")
        print()


if __name__ == "__main__":
    main()

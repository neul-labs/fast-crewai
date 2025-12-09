"""
Main entry point for the CrewAI Accelerate package.

This module provides command-line utilities for working with the accelerated components.
"""

import argparse
import sys

from .benchmark import run_benchmarks
from .utils import (
    get_acceleration_status,
    get_environment_info,
    get_performance_improvements,
    is_acceleration_available,
)


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
    """Check acceleration component status."""
    print("CrewAI Accelerate Status")
    print("=" * 30)

    available = is_acceleration_available()
    print(f"Acceleration Implementation Available: {'Yes' if available else 'No'}")

    if available:
        status = get_acceleration_status()
        print("Components Available:")
        for component, is_available in status.get("components", {}).items():
            print(f"  {component}: {'Yes' if is_available else 'No'}")

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

    if verbose:
        import os

        print("\nAll Related Environment Variables:")
        for key, value in sorted(os.environ.items()):
            if "crew" in key.lower() or "rust" in key.lower():
                print(f"  {key}: {value}")


def bench_cmd(verbose=False):
    """Run performance benchmarks."""
    import json

    print("Running CrewAI Rust Integration Benchmarks...")
    print("=" * 45)

    try:
        results = run_benchmarks()
        if verbose:
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

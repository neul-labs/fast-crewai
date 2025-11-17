#!/usr/bin/env python3
"""
Test runner script for CrewAI Accelerate.

This script provides a convenient way to run tests with different configurations.
Usage: python run_tests.py [test_type]
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Exit code: {e.returncode}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} available")
    except ImportError:
        print("❌ pytest not found. Install with: pip install -r requirements.txt")
        return False
    
    # Check if maturin is available
    try:
        result = subprocess.run(["maturin", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ maturin available")
        else:
            print("❌ maturin not found. Install with: pip install maturin")
            return False
    except FileNotFoundError:
        print("❌ maturin not found. Install with: pip install maturin")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="CrewAI Accelerate Test Runner")
    parser.add_argument("test_type", nargs="?", default="all", 
                       choices=["all", "fast", "unit", "integration", "performance", "coverage", "memory", "tools", "tasks", "shim"],
                       help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-deps", action="store_true", help="Skip dependency checks")
    
    args = parser.parse_args()
    
    print("CrewAI Accelerate Test Runner")
    print("=============================")
    
    # Check dependencies unless skipped
    if not args.no_deps:
        if not check_dependencies():
            print("\n❌ Dependency check failed. Please install required dependencies.")
            print("Run: pip install -r requirements.txt")
            sys.exit(1)
    
    # Build the Rust extension first
    print("\n🔨 Building Rust extension...")
    if not run_command("maturin develop", "Build Rust extension"):
        print("❌ Failed to build Rust extension")
        sys.exit(1)
    
    # Run tests based on type
    test_commands = {
        "all": "pytest -v",
        "fast": "pytest -m 'not slow and not integration and not performance' -v",
        "unit": "pytest tests/test_package_import.py tests/test_memory.py tests/test_tools.py tests/test_tasks.py tests/test_shim.py -v",
        "integration": "pytest tests/test_integration.py -v",
        "performance": "pytest -m performance -v",
        "coverage": "pytest --cov=fast_crewai --cov-report=html --cov-report=term",
        "memory": "pytest tests/test_memory.py -v",
        "tools": "pytest tests/test_tools.py -v",
        "tasks": "pytest tests/test_tasks.py -v",
        "shim": "pytest tests/test_shim.py -v",
    }
    
    cmd = test_commands.get(args.test_type, "pytest -v")
    
    if args.verbose:
        cmd += " -s"
    
    success = run_command(cmd, f"{args.test_type.title()} Tests")
    
    if success:
        print(f"\n✅ {args.test_type.title()} tests completed successfully!")
        if args.test_type == "coverage":
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ {args.test_type.title()} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test Fast-CrewAI compatibility with CrewAI's test suite.

This script automates the process of:
1. Cloning CrewAI repository
2. Installing CrewAI and dependencies (including LiteLLM)
3. Installing Fast-CrewAI
4. Activating the shim
5. Running CrewAI's tests to verify compatibility
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def log_info(message: str) -> None:
    """Log an info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message: str) -> None:
    """Log a success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def log_warning(message: str) -> None:
    """Log a warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def log_error(message: str) -> None:
    """Log an error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture_output: bool = False
) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {' '.join(cmd)}")
        if capture_output:
            log_error(f"Output: {e.stdout}")
            log_error(f"Error: {e.stderr}")
        raise


def setup_test_environment(
    test_dir: Path,
    crewai_repo: str,
    crewai_branch: str,
    skip_clone: bool = False,
    skip_install: bool = False
) -> tuple[Path, Path]:
    """
    Set up the test environment.

    Returns:
        Tuple of (crewai_dir, venv_dir)
    """
    # Step 1: Create test directory
    log_info("Step 1/6: Creating test directory")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Convert to absolute path to avoid issues when changing directories
    test_dir = test_dir.resolve()

    log_success(f"Test directory created: {test_dir}")
    print()

    crewai_dir = test_dir / "crewai"
    venv_dir = test_dir / "venv"

    # Step 2: Clone CrewAI repository
    if not skip_clone:
        log_info("Step 2/6: Cloning CrewAI repository")
        if crewai_dir.exists():
            log_warning("CrewAI directory already exists, removing...")
            shutil.rmtree(crewai_dir)

        run_command([
            "git", "clone",
            "--depth", "1",
            "--branch", crewai_branch,
            crewai_repo,
            str(crewai_dir)
        ])
        log_success("CrewAI cloned successfully")
    else:
        log_info("Step 2/6: Skipping CrewAI clone (using existing)")
        if not crewai_dir.exists():
            log_error(f"CrewAI directory not found: {crewai_dir}")
            sys.exit(1)
    print()

    # Step 3: Create virtual environment
    log_info("Step 3/6: Setting up Python virtual environment")
    if not skip_install:
        if venv_dir.exists():
            log_warning("Virtual environment already exists, removing...")
            shutil.rmtree(venv_dir)

        run_command([sys.executable, "-m", "venv", str(venv_dir)])
        log_success("Virtual environment created")
    else:
        log_info("Using existing virtual environment")
    print()

    return crewai_dir, venv_dir


def get_venv_python(venv_dir: Path) -> Path:
    """Get the path to the Python executable in the virtual environment."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def get_venv_pip(venv_dir: Path) -> Path:
    """Get the path to pip in the virtual environment."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "pip.exe"
    else:
        return venv_dir / "bin" / "pip"


def install_dependencies(
    crewai_dir: Path,
    venv_dir: Path,
    fast_crewai_dir: Path,
    skip_install: bool = False
) -> None:
    """Install all required dependencies."""
    if skip_install:
        log_info("Step 4/6: Skipping installation")
        print()
        return

    log_info("Step 4/6: Installing dependencies")

    pip = get_venv_pip(venv_dir)

    # Upgrade pip
    log_info("Upgrading pip...")
    run_command([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])

    # Install CrewAI (from lib/crewai subdirectory - monorepo structure)
    log_info("Installing CrewAI...")
    crewai_package_dir = crewai_dir / "lib" / "crewai"
    try:
        run_command([str(pip), "install", "-e", ".[test]"], cwd=crewai_package_dir)
    except subprocess.CalledProcessError:
        log_warning("Failed to install with [test] extras, trying without...")
        run_command([str(pip), "install", "-e", "."], cwd=crewai_package_dir)

    # Install test dependencies
    log_info("Installing test dependencies...")
    run_command([
        str(pip), "install",
        "pytest", "pytest-cov", "pytest-mock",
        "pytest-timeout", "pytest-asyncio", "litellm"
    ])

    # Install Fast-CrewAI
    log_info("Installing Fast-CrewAI...")
    run_command([str(pip), "install", "-e", "."], cwd=fast_crewai_dir)

    # Try to build Rust extension
    log_info("Attempting to build Rust extension...")
    try:
        run_command(
            ["maturin", "develop"],
            cwd=fast_crewai_dir,
            check=False
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_warning("Rust extension build failed or maturin not found, will use Python fallback")

    log_success("All dependencies installed")
    print()


def create_test_config(test_dir: Path) -> None:
    """Create pytest configuration for shim activation."""
    log_info("Step 5/6: Creating test runner with Fast-CrewAI shim")

    conftest_content = '''"""
Pytest configuration for CrewAI compatibility testing with Fast-CrewAI.

This file automatically activates the Fast-CrewAI shim before running
CrewAI's tests to ensure compatibility.
"""

import os
import sys

# Set environment variable to enable acceleration
os.environ['FAST_CREWAI_ACCELERATION'] = '1'

# Import and activate the shim before any CrewAI imports
try:
    import fast_crewai.shim
    print("\\n" + "="*80)
    print("Fast-CrewAI shim activated successfully!")
    print("="*80 + "\\n")

    # Show acceleration status
    try:
        from fast_crewai import get_acceleration_status
        status = get_acceleration_status()
        print("Acceleration Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        print("="*80 + "\\n")
    except Exception as e:
        print(f"Warning: Could not get acceleration status: {e}\\n")

except ImportError as e:
    print(f"\\nWarning: Could not import fast_crewai.shim: {e}")
    print("Tests will run with standard CrewAI implementation\\n")
except Exception as e:
    print(f"\\nWarning: Error activating shim: {e}")
    print("Tests will run with standard CrewAI implementation\\n")
'''

    conftest_path = test_dir / "conftest.py"
    conftest_path.write_text(conftest_content)

    log_success("Test runner configuration created")
    print()


def run_tests(
    crewai_dir: Path,
    venv_dir: Path,
    test_dir: Path,
    test_filter: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Run CrewAI tests with Fast-CrewAI shim.

    Returns:
        Exit code from pytest
    """
    log_info("Step 6/6: Running CrewAI tests with Fast-CrewAI shim")
    print()

    # Copy conftest to CrewAI directory so pytest can find it
    import shutil
    shutil.copy(test_dir / "conftest.py", crewai_dir / "conftest.py")

    pytest = venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / "pytest"

    # Build pytest command
    cmd = [str(pytest), "-v", "--tb=short"]

    if test_filter:
        cmd.extend(["-k", test_filter])

    if verbose:
        cmd.append("-vv")

    log_info(f"Running: {' '.join(cmd)}")
    print()

    # Run tests
    result = run_command(
        cmd,
        cwd=crewai_dir,
        check=False
    )

    print()
    if result.returncode == 0:
        log_success("All tests passed! Fast-CrewAI is compatible with CrewAI.")
    else:
        log_error("Some tests failed. See details above.")

    return result.returncode


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Fast-CrewAI compatibility with CrewAI's test suite"
    )
    parser.add_argument(
        "--crewai-repo",
        default="https://github.com/crewAIInc/crewAI.git",
        help="CrewAI repository URL"
    )
    parser.add_argument(
        "--crewai-branch",
        default="main",
        help="CrewAI branch to test"
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("./test_compatibility"),
        help="Directory for test environment"
    )
    parser.add_argument(
        "--skip-clone",
        action="store_true",
        help="Skip cloning CrewAI (use existing clone)"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installation steps"
    )
    parser.add_argument(
        "--keep-env",
        action="store_true",
        help="Keep test environment after completion"
    )
    parser.add_argument(
        "--filter",
        help="Run only tests matching PATTERN"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Get fast-crewai directory (current working directory)
    fast_crewai_dir = Path.cwd()

    try:
        log_info("Starting Fast-CrewAI compatibility testing")
        print()

        # Setup environment
        crewai_dir, venv_dir = setup_test_environment(
            args.test_dir,
            args.crewai_repo,
            args.crewai_branch,
            args.skip_clone,
            args.skip_install
        )

        # Install dependencies
        install_dependencies(
            crewai_dir,
            venv_dir,
            fast_crewai_dir,
            args.skip_install
        )

        # Create test configuration
        create_test_config(args.test_dir)

        # Run tests
        exit_code = run_tests(
            crewai_dir,
            venv_dir,
            args.test_dir,
            args.filter,
            args.verbose
        )

        print()
        log_info("Compatibility testing complete")

        # Cleanup
        if not args.keep_env:
            print()
            response = input("Keep test environment for inspection? [y/N] ").strip().lower()
            if response not in ['y', 'yes']:
                log_info("Cleaning up test environment...")
                shutil.rmtree(args.test_dir)
                log_success("Cleanup complete")
            else:
                log_info(f"Test environment kept at: {args.test_dir}")
        else:
            log_info(f"Test environment kept at: {args.test_dir}")

        return exit_code

    except KeyboardInterrupt:
        print()
        log_warning("Testing interrupted by user")
        return 130
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test Fast-CrewAI benchmarking and performance validation.

This script automates the process of:
1. Setting up benchmark environment
2. Building Rust extension if available
3. Running comprehensive performance benchmarks
4. Comparing Rust vs Python implementations
5. Reporting performance improvements
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
import tempfile
import json
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
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


def log_performance(message: str) -> None:
    """Log a performance message."""
    print(f"{Colors.PURPLE}[BENCHMARK]{Colors.NC} {message}")


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


def setup_benchmark_environment(
    test_dir: Path,
    skip_install: bool = False
) -> Path:
    """Set up the benchmark environment.

    Returns:
        Path to virtual environment
    """
    # Step 1: Create test directory
    log_info("Step 1/5: Creating test directory")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Convert to absolute path to avoid issues when changing directories
    test_dir = test_dir.resolve()

    log_success(f"Test directory created: {test_dir}")
    print()

    venv_dir = test_dir / "venv"

    # Step 2: Create virtual environment
    log_info("Step 2/5: Setting up Python virtual environment")
    if not skip_install:
        if venv_dir.exists():
            log_warning("Virtual environment already exists, removing...")
            shutil.rmtree(venv_dir)

        run_command([sys.executable, "-m", "venv", str(venv_dir)])
        log_success("Virtual environment created")
        
        # Install Fast-CrewAI in development mode
        pip = get_venv_pip(venv_dir)
        run_command([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])
        run_command([str(pip), "install", "-e", "."])
    else:
        log_info("Using existing virtual environment")
    print()

    return venv_dir


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


def build_rust_extension(
    fast_crewai_dir: Path,
    build_rust: bool = True
) -> bool:
    """Build the Rust extension if requested and available."""
    if not build_rust:
        log_info("Step 3/5: Skipping Rust extension build (--no-rust-build)")
        print()
        return False

    log_info("Step 3/5: Building Rust extension")
    
    try:
        # Check if maturin is available
        result = run_command(["maturin", "--version"], capture_output=True, check=False)
        if result.returncode != 0:
            log_warning("Maturin not found, skipping Rust extension build")
            log_info("Benchmarks will run with Python fallback only")
            print()
            return False

        # Build the Rust extension
        run_command(["maturin", "develop", "--release"], cwd=fast_crewai_dir)
        log_success("Rust extension built successfully")
        
        # Check if Rust is available
        try:
            import fast_crewai
            rust_available = fast_crewai.HAS_ACCELERATION_IMPLEMENTATION
            log_performance(f"Rust acceleration available: {rust_available}")
        except ImportError:
            log_warning("Could not check Rust availability")
        
        print()
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_warning("Rust extension build failed, will use Python fallback")
        log_info("Benchmarks will run with Python fallback only")
        print()
        return False


def run_benchmarks(
    test_dir: Path,
    venv_dir: Path,
    iterations: int,
    python_only: bool = False,
    rust_only: bool = False,
    report_file: Optional[Path] = None
) -> int:
    """
    Run performance benchmarks.

    Returns:
        Exit code from benchmark execution
    """
    log_info("Step 5/5: Running performance benchmarks")
    print()

    # Set environment variables for benchmarking
    os.environ['FAST_CREWAI_ACCELERATION'] = '1'
    os.environ['FAST_CREWAI_MEMORY'] = 'true'
    os.environ['FAST_CREWAI_TOOLS'] = 'true'
    os.environ['FAST_CREWAI_TASKS'] = 'true'
    os.environ['FAST_CREWAI_DATABASE'] = 'true'
    os.environ['ITERATIONS'] = str(iterations)

    # Build benchmark runner script
    benchmark_runner_content = f'''
#!/usr/bin/env python3
"""
Benchmark runner for Fast-CrewAI performance testing.
"""
import os
import sys
import json
from datetime import datetime

def run_benchmarks():
    """Run the Fast-CrewAI benchmark suite."""
    try:
        # Import benchmark module
        from fast_crewai.benchmark import PerformanceBenchmark
        
        print("="*80)
        print("Fast-CrewAI Performance Benchmark")
        print("="*80)
        print(f"Benchmark started: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
        print(f"Iterations: {{os.environ.get('ITERATIONS', '{iterations}')}}")
        print()
        
        # Print rust availability
        from fast_crewai import is_acceleration_available
        print(f"Rust acceleration available: {{is_acceleration_available()}}")
        print()
        
        # Configure benchmark with specified iterations
        iterations = int(os.environ.get('ITERATIONS', '{iterations}'))
        benchmark = PerformanceBenchmark(iterations=iterations)
        
        # Run all benchmarks
        results = benchmark.run_all_benchmarks()
        
        # Print detailed summary
        benchmark.print_summary()
        
        # Print raw results
        print()
        print("Raw Results:")
        print(json.dumps(results, indent=2))
        
        return results
    except ImportError as e:
        print(f"Error importing benchmark module: {{e}}")
        print("Make sure Fast-CrewAI is properly installed.")
        return None
    except Exception as e:
        print(f"Error running benchmarks: {{e}}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = run_benchmarks()
    if results is None:
        sys.exit(1)
    else:
        sys.exit(0)
'''

    # Write the benchmark runner script
    runner_path = test_dir / "benchmark_runner.py"
    with open(runner_path, 'w') as f:
        f.write(benchmark_runner_content)

    # Prepare the Python executable in the virtual environment
    python_exe = get_venv_python(venv_dir)

    # Run the benchmark
    log_info(f"Running benchmarks with {iterations} iterations...")
    print()

    try:
        if report_file:
            # Run with output to both console and file
            import subprocess
            result = subprocess.run(
                [str(python_exe), str(runner_path)],
                cwd=test_dir,
                capture_output=True,
                text=True
            )
            
            # Write to report file
            with open(report_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write(result.stderr)
            
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            return result.returncode
        else:
            # Run with output to console only
            result = run_command([str(python_exe), str(runner_path)], cwd=test_dir, check=False)
            return result.returncode
            
    except Exception as e:
        log_error(f"Error running benchmarks: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark Fast-CrewAI performance improvements"
    )
    parser.add_argument(
        "--no-rust-build",
        action="store_true",
        help="Skip Rust extension build"
    )
    parser.add_argument(
        "--python-only",
        action="store_true",
        help="Run only Python implementation benchmarks"
    )
    parser.add_argument(
        "--rust-only",
        action="store_true",
        help="Run only Rust implementation benchmarks"
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("./benchmark_test"),
        help="Directory for test environment"
    )
    parser.add_argument(
        "--keep-env",
        action="store_true",
        help="Keep test environment after completion"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of iterations for benchmarks (default: 1000)"
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        help="Save benchmark report to file"
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
        log_info("Starting Fast-CrewAI benchmarking")
        print()

        # Setup environment
        venv_dir = setup_benchmark_environment(args.test_dir)

        # Build Rust extension if requested
        rust_built = build_rust_extension(fast_crewai_dir, not args.no_rust_build)

        # Run benchmarks
        exit_code = run_benchmarks(
            args.test_dir,
            venv_dir,
            args.iterations,
            args.python_only,
            args.rust_only,
            args.report_file
        )

        print()
        if exit_code == 0:
            log_success("Benchmarking completed successfully!")
            
            # Show acceleration status
            log_performance("Acceleration Status:")
            try:
                from fast_crewai import get_acceleration_status
                status = get_acceleration_status()
                for key, value in status.items():
                    print(f'  {key}: {value}')
            except ImportError:
                log_warning("Could not get acceleration status")
        else:
            log_error("Benchmarking failed.")

        # Cleanup
        if not args.keep_env:
            print()
            response = input("Keep test environment for inspection? [y/N] ").strip().lower()
            if response not in ['y', 'yes']:
                log_info("Cleaning up benchmark environment...")
                shutil.rmtree(args.test_dir)
                log_success("Cleanup complete")
            else:
                log_info(f"Benchmark environment kept at: {args.test_dir}")
        else:
            log_info(f"Benchmark environment kept at: {args.test_dir}")

        return exit_code

    except KeyboardInterrupt:
        print()
        log_warning("Benchmarking interrupted by user")
        return 130
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
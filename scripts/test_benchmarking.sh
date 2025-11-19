#!/bin/bash
# Benchmark Fast-CrewAI performance improvements
#
# This script:
# 1. Sets up the environment for benchmarking
# 2. Builds Rust extension if available
# 3. Runs comprehensive performance benchmarks
# 4. Compares Rust vs Python implementations
# 5. Reports performance improvements

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
TEST_DIR="${TEST_DIR:-./benchmark_test}"
VENV_DIR="${TEST_DIR}/venv"
ITERATIONS="${ITERATIONS:-1000}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_performance() {
    echo -e "${PURPLE}[BENCHMARK]${NC} $1"
}

cleanup() {
    if [ "$KEEP_TEST_ENV" != "1" ]; then
        log_info "Cleaning up benchmark environment..."
        rm -rf "$TEST_DIR"
        log_success "Cleanup complete"
    else
        log_info "Keeping test environment at: $TEST_DIR"
    fi
}

# Parse arguments
BUILD_RUST=1
RUN_PYTHON_ONLY=0
RUN_RUST_ONLY=0
KEEP_TEST_ENV=0
VERBOSE=0
REPORT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-rust-build)
            BUILD_RUST=0
            shift
            ;;
        --python-only)
            RUN_PYTHON_ONLY=1
            shift
            ;;
        --rust-only)
            RUN_RUST_ONLY=1
            shift
            ;;
        --keep-env)
            KEEP_TEST_ENV=1
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --report-file)
            REPORT_FILE="$2"
            shift 2
            ;;
        --iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Benchmark Fast-CrewAI performance improvements"
            echo ""
            echo "Options:"
            echo "  --no-rust-build     Skip Rust extension build"
            echo "  --python-only       Run only Python implementation benchmarks"
            echo "  --rust-only         Run only Rust implementation benchmarks"
            echo "  --keep-env          Keep test environment after completion"
            echo "  --verbose, -v       Enable verbose output"
            echo "  --report-file FILE  Save benchmark report to file"
            echo "  --iterations N      Number of iterations for benchmarks (default: 1000)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  TEST_DIR            Directory for test environment (default: ./benchmark_test)"
            echo "  ITERATIONS          Number of iterations for benchmarks (default: 1000)"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set verbose mode
if [ "$VERBOSE" = "1" ]; then
    set -x
fi

# Main execution
log_info "Starting Fast-CrewAI benchmarking"
echo ""

# Step 1: Create test directory
log_info "Step 1/5: Creating test directory"
mkdir -p "$TEST_DIR"

# Convert to absolute path to avoid issues when changing directories
TEST_DIR="$(cd "$TEST_DIR" && pwd)"
VENV_DIR="${TEST_DIR}/venv"

log_success "Test directory created: $TEST_DIR"
echo ""

# Step 2: Create and activate virtual environment
log_info "Step 2/5: Setting up Python virtual environment"
if [ -d "$VENV_DIR" ]; then
    log_warning "Virtual environment already exists, removing..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Fast-CrewAI in development mode
log_info "Installing Fast-CrewAI..."
pip install -e .

log_success "Virtual environment created and Fast-CrewAI installed"
echo ""

# Step 3: Build Rust extension (if requested)
if [ "$BUILD_RUST" = "1" ]; then
    log_info "Step 3/5: Building Rust extension"
    
    if command -v maturin &> /dev/null; then
        maturin develop --release
        log_success "Rust extension built successfully"
        
        # Check if Rust is available
        python -c "from fast_crewai import is_acceleration_available; print('Rust available:', is_acceleration_available())"
    else
        log_warning "Maturin not found, skipping Rust extension build"
        log_info "Benchmarks will run with Python fallback only"
    fi
else
    log_info "Step 3/5: Skipping Rust extension build (--no-rust-build)"
fi
echo ""

# Step 4: Configure benchmark environment
log_info "Step 4/5: Configuring benchmark environment"

# Set environment variables for benchmarking
export FAST_CREWAI_ACCELERATION=1
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_TOOLS=true
export FAST_CREWAI_TASKS=true
export FAST_CREWAI_DATABASE=true

log_success "Environment configured for benchmarking"
echo ""

# Step 5: Run benchmarks
log_info "Step 5/5: Running performance benchmarks"
echo ""

cd "$TEST_DIR"

# Create a Python script to run benchmarks
cat > benchmark_runner.py << EOF
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
        print(f"Benchmark started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Iterations: {os.environ.get('ITERATIONS', '1000')}")
        print()
        
        # Print rust availability
        from fast_crewai import is_acceleration_available
        print(f"Rust acceleration available: {is_acceleration_available()}")
        print()
        
        # Configure benchmark with specified iterations
        iterations = int(os.environ.get('ITERATIONS', '1000'))
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
        print(f"Error importing benchmark module: {e}")
        print("Make sure Fast-CrewAI is properly installed.")
        return None
    except Exception as e:
        print(f"Error running benchmarks: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = run_benchmarks()
    if results is None:
        sys.exit(1)
    else:
        sys.exit(0)
EOF

# Set the iterations in environment
export ITERATIONS="$ITERATIONS"

# Run the benchmark
log_info "Running benchmarks with $ITERATIONS iterations..."
echo ""

if [ -n "$REPORT_FILE" ]; then
    # Run with output to both console and file
    python benchmark_runner.py 2>&1 | tee "$REPORT_FILE"
    exit_code=${PIPESTATUS[0]}
else
    # Run with output to console only
    python benchmark_runner.py
    exit_code=$?
fi

echo ""
if [ $exit_code -eq 0 ]; then
    log_success "Benchmarking completed successfully!"
    
    # Show acceleration status
    log_performance "Acceleration Status:"
    python -c "
from fast_crewai import get_acceleration_status
status = get_acceleration_status()
for key, value in status.items():
    print(f'  {key}: {value}')
"
else
    log_error "Benchmarking failed with exit code $exit_code"
fi

# Return to original directory
cd - > /dev/null

echo ""
log_info "Performance benchmarking complete"

# Cleanup
if [ "$KEEP_TEST_ENV" != "1" ]; then
    echo ""
    read -p "Keep test environment for inspection? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    else
        log_info "Test environment kept at: $TEST_DIR"
    fi
else
    log_info "Test environment kept at: $TEST_DIR"
fi

exit $exit_code
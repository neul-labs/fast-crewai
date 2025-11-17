#!/bin/bash
# Test Fast-CrewAI compatibility by running CrewAI's test suite with our shim
#
# This script:
# 1. Clones CrewAI repository
# 2. Installs CrewAI and dependencies (including LiteLLM)
# 3. Installs Fast-CrewAI
# 4. Activates the shim
# 5. Runs CrewAI's tests to verify compatibility

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CREWAI_REPO="${CREWAI_REPO:-https://github.com/crewAIInc/crewAI.git}"
CREWAI_BRANCH="${CREWAI_BRANCH:-main}"
TEST_DIR="${TEST_DIR:-./test_compatibility}"
CREWAI_DIR="${TEST_DIR}/crewai"
VENV_DIR="${TEST_DIR}/venv"

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

cleanup() {
    if [ "$KEEP_TEST_ENV" != "1" ]; then
        log_info "Cleaning up test environment..."
        rm -rf "$TEST_DIR"
        log_success "Cleanup complete"
    else
        log_info "Keeping test environment at: $TEST_DIR"
    fi
}

# Parse arguments
SKIP_CLONE=0
SKIP_INSTALL=0
KEEP_TEST_ENV=0
TEST_FILTER=""
VERBOSE=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-clone)
            SKIP_CLONE=1
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=1
            shift
            ;;
        --keep-env)
            KEEP_TEST_ENV=1
            shift
            ;;
        --filter)
            TEST_FILTER="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Test Fast-CrewAI compatibility with CrewAI's test suite"
            echo ""
            echo "Options:"
            echo "  --skip-clone      Skip cloning CrewAI (use existing clone)"
            echo "  --skip-install    Skip installation steps"
            echo "  --keep-env        Keep test environment after completion"
            echo "  --filter PATTERN  Run only tests matching PATTERN"
            echo "  --verbose, -v     Enable verbose output"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  CREWAI_REPO       CrewAI repository URL (default: https://github.com/crewAIInc/crewAI.git)"
            echo "  CREWAI_BRANCH     CrewAI branch to test (default: main)"
            echo "  TEST_DIR          Directory for test environment (default: ./test_compatibility)"
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
log_info "Starting Fast-CrewAI compatibility testing"
echo ""

# Step 1: Create test directory
log_info "Step 1/6: Creating test directory"
mkdir -p "$TEST_DIR"

# Convert to absolute path to avoid issues when changing directories
TEST_DIR="$(cd "$TEST_DIR" && pwd)"
CREWAI_DIR="${TEST_DIR}/crewai"
VENV_DIR="${TEST_DIR}/venv"

log_success "Test directory created: $TEST_DIR"
echo ""

# Step 2: Clone CrewAI repository
if [ "$SKIP_CLONE" = "0" ]; then
    log_info "Step 2/6: Cloning CrewAI repository"
    if [ -d "$CREWAI_DIR" ]; then
        log_warning "CrewAI directory already exists, removing..."
        rm -rf "$CREWAI_DIR"
    fi
    git clone --depth 1 --branch "$CREWAI_BRANCH" "$CREWAI_REPO" "$CREWAI_DIR"
    log_success "CrewAI cloned successfully"
else
    log_info "Step 2/6: Skipping CrewAI clone (using existing)"
    if [ ! -d "$CREWAI_DIR" ]; then
        log_error "CrewAI directory not found: $CREWAI_DIR"
        exit 1
    fi
fi
echo ""

# Step 3: Create and activate virtual environment
log_info "Step 3/6: Setting up Python virtual environment"
if [ "$SKIP_INSTALL" = "0" ]; then
    if [ -d "$VENV_DIR" ]; then
        log_warning "Virtual environment already exists, removing..."
        rm -rf "$VENV_DIR"
    fi
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel
    log_success "Virtual environment created and activated"
else
    source "$VENV_DIR/bin/activate"
    log_info "Using existing virtual environment"
fi
echo ""

# Step 4: Install dependencies
if [ "$SKIP_INSTALL" = "0" ]; then
    log_info "Step 4/6: Installing dependencies"

    # Install CrewAI and its dependencies
    log_info "Installing CrewAI..."
    cd "$CREWAI_DIR/lib/crewai"
    pip install -e ".[test]" || pip install -e .

    # Install test dependencies if not already installed
    log_info "Installing test dependencies..."
    pip install pytest pytest-cov pytest-mock pytest-timeout pytest-asyncio litellm

    # Go back to fast-crewai directory
    cd - > /dev/null

    # Install Fast-CrewAI
    log_info "Installing Fast-CrewAI..."
    pip install -e .

    # Try to build Rust extension (optional, will use Python fallback if it fails)
    log_info "Attempting to build Rust extension..."
    if command -v maturin &> /dev/null; then
        maturin develop || log_warning "Rust extension build failed, will use Python fallback"
    else
        log_warning "Maturin not found, skipping Rust extension build"
    fi

    log_success "All dependencies installed"
else
    log_info "Step 4/6: Skipping installation"
fi
echo ""

# Step 5: Activate Fast-CrewAI shim
log_info "Step 5/6: Creating test runner with Fast-CrewAI shim"

# Create a pytest configuration that imports the shim
cat > "$TEST_DIR/conftest.py" << 'EOF'
"""
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
    print("\n" + "="*80)
    print("Fast-CrewAI shim activated successfully!")
    print("="*80 + "\n")

    # Show acceleration status
    try:
        from fast_crewai import get_acceleration_status
        status = get_acceleration_status()
        print("Acceleration Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        print("="*80 + "\n")
    except Exception as e:
        print(f"Warning: Could not get acceleration status: {e}\n")

except ImportError as e:
    print(f"\nWarning: Could not import fast_crewai.shim: {e}")
    print("Tests will run with standard CrewAI implementation\n")
except Exception as e:
    print(f"\nWarning: Error activating shim: {e}")
    print("Tests will run with standard CrewAI implementation\n")
EOF

log_success "Test runner configuration created"
echo ""

# Step 6: Run tests
log_info "Step 6/6: Running CrewAI tests with Fast-CrewAI shim"
echo ""

cd "$CREWAI_DIR"

# Copy conftest to CrewAI directory so pytest can find it
cp "$TEST_DIR/conftest.py" "$CREWAI_DIR/conftest.py"

# Build pytest command
PYTEST_CMD="pytest"
PYTEST_ARGS="-v --tb=short"

if [ -n "$TEST_FILTER" ]; then
    PYTEST_ARGS="$PYTEST_ARGS -k $TEST_FILTER"
fi

log_info "Running: $PYTEST_CMD $PYTEST_ARGS"
echo ""

# Ensure log directory exists
mkdir -p "$(dirname "$TEST_DIR/test_results.log")"

# Run the tests
set +e  # Don't exit on test failure
$PYTEST_CMD $PYTEST_ARGS 2>&1 | tee "$TEST_DIR/test_results.log"
TEST_EXIT_CODE=$?
set -e

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "All tests passed! Fast-CrewAI is compatible with CrewAI."
else
    log_error "Some tests failed. See details above."
    log_info "Test results saved to: $TEST_DIR/test_results.log"
fi

# Return to original directory
cd - > /dev/null

echo ""
log_info "Compatibility testing complete"

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

exit $TEST_EXIT_CODE

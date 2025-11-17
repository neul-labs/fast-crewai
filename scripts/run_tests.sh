#!/bin/bash
# Convenient test runner script for CrewAI Accelerate

set -e

echo "CrewAI Accelerate Test Runner"
echo "========================="

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing test dependencies..."
    pip install -r tests/requirements.txt
fi

# Function to run tests with error handling
run_tests() {
    local test_cmd="$1"
    local description="$2"

    echo ""
    echo "$description"
    echo "Command: $test_cmd"
    echo "---"

    if eval "$test_cmd"; then
        echo "$description - PASSED"
    else
        echo "$description - FAILED"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "fast")
        echo "Running fast tests only (excluding slow, integration, performance tests)"
        run_tests "pytest -m 'not slow and not integration and not performance' -v" "Fast Tests"
        ;;
    "unit")
        echo "Running unit tests only"
        run_tests "pytest tests/test_package_import.py tests/test_memory.py tests/test_tools.py tests/test_tasks.py tests/test_shim.py -v" "Unit Tests"
        ;;
    "integration")
        echo "Running integration tests"
        run_tests "pytest tests/test_integration.py -v" "Integration Tests"
        ;;
    "performance")
        echo "Running performance tests"
        run_tests "pytest -m performance -v" "Performance Tests"
        ;;
    "coverage")
        echo "Running tests with coverage report"
        run_tests "pytest --cov=fast_crewai --cov-report=html --cov-report=term" "Coverage Tests"
        ;;
    "memory")
        echo "Running memory component tests"
        run_tests "pytest tests/test_memory.py -v" "Memory Tests"
        ;;
    "tools")
        echo "Running tool component tests"
        run_tests "pytest tests/test_tools.py -v" "Tool Tests"
        ;;
    "tasks")
        echo "Running task component tests"
        run_tests "pytest tests/test_tasks.py -v" "Task Tests"
        ;;
    "shim")
        echo "Running shim system tests"
        run_tests "pytest tests/test_shim.py -v" "Shim Tests"
        ;;
    "all")
        echo "Running all tests"
        run_tests "pytest -v" "All Tests"
        ;;
    "help"|"-h"|"--help")
        echo ""
        echo "Usage: $0 [test_type]"
        echo ""
        echo "Available test types:"
        echo "  all          - Run all tests (default)"
        echo "  fast         - Run fast tests only (exclude slow/integration/performance)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests"
        echo "  performance  - Run performance tests"
        echo "  coverage     - Run tests with coverage report"
        echo "  memory       - Run memory component tests"
        echo "  tools        - Run tool component tests"
        echo "  tasks        - Run task component tests"
        echo "  shim         - Run shim system tests"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 fast              # Quick test run"
        echo "  $0 unit              # Unit tests only"
        echo "  $0 integration       # Integration tests"
        echo "  $0 coverage          # With coverage report"
        echo ""
        exit 0
        ;;
    *)
        echo "Unknown test type: $1"
        echo "Run '$0 help' for available options"
        exit 1
        ;;
esac

echo ""
echo "Test execution completed!"
echo ""
echo "Useful commands:"
echo "  $0 fast       - Quick test run"
echo "  $0 coverage   - Generate coverage report"
echo "  $0 help       - Show all options"
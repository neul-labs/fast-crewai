#!/bin/bash
# Compare CrewAI performance with and without Fast-CrewAI acceleration
#
# This script runs the same CrewAI workflows with and without Fast-CrewAI
# shimming to measure the actual real-world performance improvements.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
TEST_DIR="${TEST_DIR:-./crewai_comparison_test}"
VENV_DIR="${TEST_DIR}/venv"
ITERATIONS="${ITERATIONS:-3}"
WORKFLOW_TYPE="${WORKFLOW_TYPE:-basic}"

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
    echo -e "${PURPLE}[PERFORMANCE]${NC} $1"
}

cleanup() {
    if [ "$KEEP_TEST_ENV" != "1" ]; then
        log_info "Cleaning up comparison environment..."
        rm -rf "$TEST_DIR"
        log_success "Cleanup complete"
    else
        log_info "Keeping test environment at: $TEST_DIR"
    fi
}

# Parse arguments
SKIP_INSTALL=0
KEEP_TEST_ENV=0
VERBOSE=0
WORKFLOW_TYPE="basic"

while [[ $# -gt 0 ]]; do
    case $1 in
        --workflow-type)
            WORKFLOW_TYPE="$2"
            shift 2
            ;;
        --iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        --skip-install)
            SKIP_INSTALL=1
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
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Compare CrewAI performance with and without Fast-CrewAI acceleration"
            echo ""
            echo "Options:"
            echo "  --workflow-type TYPE  Type of workflow: basic, memory, tools (default: basic)"
            echo "  --iterations N        Number of iterations for each test (default: 3)"
            echo "  --skip-install        Skip installation steps"
            echo "  --keep-env            Keep test environment after completion"
            echo "  --verbose, -v         Enable verbose output"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  TEST_DIR              Directory for test environment (default: ./crewai_comparison_test)"
            echo "  ITERATIONS            Number of iterations for each test (default: 3)"
            echo "  WORKFLOW_TYPE         Type of workflow to test (default: basic)"
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
log_info "Starting CrewAI vs Fast-CrewAI performance comparison"
echo ""

# Step 1: Create test directory
log_info "Step 1/4: Creating test directory"
mkdir -p "$TEST_DIR"

# Convert to absolute path to avoid issues when changing directories
TEST_DIR="$(cd "$TEST_DIR" && pwd)"
VENV_DIR="${TEST_DIR}/venv"

log_success "Test directory created: $TEST_DIR"
echo ""

# Step 2: Create and activate virtual environment
log_info "Step 2/4: Setting up Python virtual environment"
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

# Step 3: Install dependencies
if [ "$SKIP_INSTALL" = "0" ]; then
    log_info "Step 3/4: Installing dependencies"
    
    # Install CrewAI
    log_info "Installing CrewAI..."
    pip install "crewai>=0.28.0" || pip install crewai
    
    # Install Fast-CrewAI
    log_info "Installing Fast-CrewAI..."
    pip install -e .
    
    log_success "Dependencies installed"
else
    log_info "Step 3/4: Skipping installation"
fi
echo ""

# Step 4: Create test workflow script
log_info "Step 4/4: Creating test workflow script"

# Create the test workflow script
cat > "$TEST_DIR/crewai_test_workflow.py" << 'EOF'
import os
import sys
import time
from datetime import datetime

def run_crewai_workflow():
    """Run a typical CrewAI workflow for benchmarking."""
    print(f"Starting CrewAI workflow at {datetime.now()}")

    try:
        from crewai import Agent, Task, Crew
    except ImportError:
        print("ERROR: CrewAI not available - please install CrewAI first")
        return None

    # Only set fake API key if no real API key is present
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"
        print("No API key found, using fake key for testing")
    else:
        print(f"Using existing API key from environment")

    # Create agents
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Uncover cutting-edge developments in AI and data science",
        backstory="""You are a Senior Research Analyst at a leading tech think tank.
        Known for your ability to make complex topics easy to understand.""",
        verbose=True
    )

    writer = Agent(
        role="Tech Writer",
        goal="Create engaging content about AI advancements",
        backstory="""You are a renowned Tech Writer, known for your insightful and engaging articles
        on technology and its future implications.""",
        verbose=True
    )

    # Create tasks
    research_task = Task(
        description="Investigate the latest AI trends in 2024",
        expected_output="A list of 5 major AI trends with brief explanations",
        agent=researcher
    )

    writing_task = Task(
        description="Write an engaging blog post about the AI trends",
        expected_output="A 400-word blog post formatted as markdown about AI trends",
        agent=writer
    )

    # Create crew
    start_time = time.time()
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True
    )

    # Run the crew
    result = crew.kickoff()
    end_time = time.time()

    execution_time = end_time - start_time

    print(f"CrewAI workflow completed in {execution_time:.2f} seconds")
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(str(result)) if result else 0}")

    return {
        'execution_time': execution_time,
        'result_length': len(str(result)) if result else 0,
        'success': True
    }


def run_memory_intensive_workflow():
    """Run a memory-intensive CrewAI workflow."""
    print(f"Starting memory-intensive workflow at {datetime.now()}")

    try:
        from crewai import Agent, Task, Crew
    except ImportError:
        print("ERROR: CrewAI not available - please install CrewAI first")
        return None

    # Only set fake API key if no real API key is present
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"
        print("No API key found, using fake key for testing")
    else:
        print(f"Using existing API key from environment")

    # Create agents with memory enabled
    researcher = Agent(
        role="Data Analyst",
        goal="Analyze large datasets and provide insights",
        backstory="You are an expert data analyst with memory capabilities.",
        verbose=True
    )

    # Create multiple tasks to test memory usage
    tasks = []
    for i in range(3):
        task = Task(
            description=f"Analyze dataset {i+1} and summarize findings",
            expected_output=f"Summary of dataset {i+1}",
            agent=researcher
        )
        tasks.append(task)

    # Create crew with memory
    start_time = time.time()
    crew = Crew(
        agents=[researcher],
        tasks=tasks,
        verbose=True,
        memory=True  # Enable memory for this test
    )

    result = crew.kickoff()
    end_time = time.time()

    execution_time = end_time - start_time

    print(f"Memory-intensive workflow completed in {execution_time:.2f} seconds")

    return {
        'execution_time': execution_time,
        'result_length': len(str(result)) if result else 0,
        'success': True
    }


def run_tool_execution_workflow():
    """Run a tool-intensive CrewAI workflow."""
    print(f"Starting tool-intensive workflow at {datetime.now()}")

    try:
        from crewai import Agent, Task, Crew
        from crewai_tools import tool
    except ImportError:
        print("ERROR: CrewAI or crewai-tools not available")
        return None

    # Only set fake API key if no real API key is present
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"
        print("No API key found, using fake key for testing")
    else:
        print(f"Using existing API key from environment")

    # Define a simple tool
    @tool("Calculator Tool")
    def calculator_tool(operation: str) -> str:
        """Perform a calculation based on the operation string."""
        try:
            # For benchmarking, just return a simple calculation
            if "+" in operation:
                parts = operation.replace(" ", "").split("+")
                result = int(parts[0]) + int(parts[1])
                return f"Result: {result}"
            elif "-" in operation:
                parts = operation.replace(" ", "").split("-")
                result = int(parts[0]) - int(parts[1])
                return f"Result: {result}"
            else:
                return f"Result: {operation}"
        except:
            return f"Error in operation: {operation}"

    # Create agents with tools
    calculator_agent = Agent(
        role="Calculator",
        goal="Perform calculations quickly",
        backstory="You are an expert calculator.",
        tools=[calculator_tool],
        verbose=True
    )

    # Create tasks that use tools
    tasks = []
    for i in range(5):
        task = Task(
            description=f"Calculate 10{i} + 5{i}",
            expected_output=f"Calculation result",
            agent=calculator_agent
        )
        tasks.append(task)

    # Create crew
    start_time = time.time()
    crew = Crew(
        agents=[calculator_agent],
        tasks=tasks,
        verbose=True
    )

    result = crew.kickoff()
    end_time = time.time()

    execution_time = end_time - start_time

    print(f"Tool-intensive workflow completed in {execution_time:.2f} seconds")

    return {
        'execution_time': execution_time,
        'result_length': len(str(result)) if result else 0,
        'success': True
    }


if __name__ == "__main__":
    import os
    workflow_type = os.environ.get('WORKFLOW_TYPE', 'basic')
    
    if workflow_type == 'memory':
        result = run_memory_intensive_workflow()
    elif workflow_type == 'tools':
        result = run_tool_execution_workflow()
    elif workflow_type == 'basic':
        result = run_crewai_workflow()
    else:
        result = run_crewai_workflow()
    
    if result:
        import json
        print("\n" + "="*50)
        print("WORKFLOW RESULTS:")
        print(json.dumps(result, indent=2))
        print("="*50)
    else:
        print("Workflow failed to run")
        sys.exit(1)
EOF

log_success "Test workflow script created"
echo ""

# Run tests and collect results
log_info "Running performance comparison tests..."

# Function to run a single test
run_single_test() {
    local use_acceleration=$1
    local test_name=$2
    shift 2
    local extra_args=("$@")
    
    echo "Running $test_name test..."
    
    # Set environment variable for acceleration
    if [ "$use_acceleration" = "1" ]; then
        export FAST_CREWAI_ACCELERATION=1
        echo "Acceleration enabled"
    else
        unset FAST_CREWAI_ACCELERATION
        echo "Acceleration disabled"
    fi
    
    # Run the test multiple times and collect results
    local total_time=0
    local count=0
    local results_file="$TEST_DIR/${test_name}_results.json"
    
    for i in $(seq 1 $ITERATIONS); do
        echo "Iteration $i/$ITERATIONS..."
        
        start_time=$(date +%s.%N)
        
        # Run with or without importing fast_crewai.shim
        if [ "$use_acceleration" = "1" ]; then
            python -c "import fast_crewai.shim; import os; os.environ['WORKFLOW_TYPE']='$WORKFLOW_TYPE'; exec(open('$TEST_DIR/crewai_test_workflow.py').read())"
        else
            WORKFLOW_TYPE="$WORKFLOW_TYPE" python "$TEST_DIR/crewai_test_workflow.py"
        fi
        
        end_time=$(date +%s.%N)
        iteration_time=$(echo "$end_time - $start_time" | bc -l)
        
        total_time=$(echo "$total_time + $iteration_time" | bc -l)
        count=$((count + 1))
        
        echo "  Iteration $i completed in ${iteration_time}s"
    done
    
    local avg_time=$(echo "$total_time / $count" | bc -l)
    echo "$avg_time" > "$TEST_DIR/${test_name}_avg_time.txt"
    
    echo "$test_name test completed. Average time: $avg_time seconds"
    echo ""
}

# Run baseline test (without acceleration)
run_single_test 0 "baseline"

# Run accelerated test (with acceleration)
run_single_test 1 "accelerated"

# Compare results
baseline_time=$(cat "$TEST_DIR/baseline_avg_time.txt")
accelerated_time=$(cat "$TEST_DIR/accelerated_avg_time.txt")

# Calculate improvement
if [ "$(echo "$accelerated_time > 0" | bc -l)" = "1" ]; then
    improvement=$(echo "scale=2; $baseline_time / $accelerated_time" | bc -l)
    time_saved=$(echo "scale=4; $baseline_time - $accelerated_time" | bc -l)
    percent_improvement=$(echo "scale=2; (1 - $accelerated_time / $baseline_time) * 100" | bc -l)
else
    improvement="inf"
    time_saved=$baseline_time
    percent_improvement="inf"
fi

echo ""
log_performance "PERFORMANCE COMPARISON RESULTS"
echo "=================================================="
echo "Workflow Type: $WORKFLOW_TYPE"
echo "Iterations: $ITERATIONS"
echo "Baseline (without Fast-CrewAI): ${baseline_time}s"
echo "Accelerated (with Fast-CrewAI): ${accelerated_time}s" 
echo "Time Saved: ${time_saved}s"
echo "Performance Improvement: ${improvement}x faster"
echo "Percent Improvement: ${percent_improvement}%"
echo "=================================================="

# Create summary results file
cat > "$TEST_DIR/comparison_results.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "workflow_type": "$WORKFLOW_TYPE",
  "iterations": $ITERATIONS,
  "baseline_average_time": $baseline_time,
  "accelerated_average_time": $accelerated_time,
  "improvement_factor": $improvement,
  "time_saved": $time_saved,
  "percent_improvement": $percent_improvement
}
EOF

log_success "Comparison completed! Results saved to $TEST_DIR/comparison_results.json"

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

exit 0
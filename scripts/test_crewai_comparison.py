#!/usr/bin/env python3
"""
Compare CrewAI performance with and without Fast-CrewAI acceleration.

This script runs the same CrewAI workflows with and without Fast-CrewAI
shimming to measure the actual real-world performance improvements.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
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
    print(f"{Colors.PURPLE}[PERFORMANCE]{Colors.NC} {message}")


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
    skip_install: bool = False
) -> Path:
    """Set up the test environment with CrewAI installed."""
    # Create virtual environment
    venv_dir = test_dir / "venv"
    
    if not skip_install:
        log_info("Creating virtual environment for CrewAI")
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
        
        pip = get_venv_pip(venv_dir)
        run_command([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])
    
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


def install_crewai(venv_dir: Path) -> None:
    """Install CrewAI in the virtual environment."""
    pip = get_venv_pip(venv_dir)
    
    # Install a minimal version of CrewAI (avoiding complex dependencies if possible for benchmarking)
    # Try to install with minimal dependencies first
    try:
        run_command([str(pip), "install", "crewai[tools]"], check=False)
        # If that fails, try a simpler install
        if run_command([str(pip), "list"], capture_output=True).stdout.find("crewai") == -1:
            run_command([str(pip), "install", "crewai"], check=True)
    except:
        # If all else fails, install directly
        run_command([str(pip), "install", "crewai>=0.28.0"], check=True)


def install_fast_crewai(venv_dir: Path, fast_crewai_dir: Path) -> None:
    """Install both CrewAI and Fast-CrewAI in the virtual environment."""
    pip = get_venv_pip(venv_dir)
    
    # Install CrewAI first
    install_crewai(venv_dir)
    
    # Install Fast-CrewAI
    run_command([str(pip), "install", "-e", "."], cwd=fast_crewai_dir)


def create_test_workflow_script(venv_dir: Path, test_dir: Path) -> Path:
    """Create a test script that runs a CrewAI workflow."""
    
    workflow_script_content = '''
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
        \"\"\"Perform a calculation based on the operation string.\"\"\"
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
        print("\\n" + "="*50)
        print("WORKFLOW RESULTS:")
        print(json.dumps(result, indent=2))
        print("="*50)
    else:
        print("Workflow failed to run")
        sys.exit(1)
'''

    workflow_script_path = test_dir / "crewai_test_workflow.py"
    with open(workflow_script_path, 'w') as f:
        f.write(workflow_script_content)
    
    return workflow_script_path


def run_benchmark(
    venv_dir: Path,
    workflow_script: Path,
    use_acceleration: bool,
    workflow_type: str = "basic",
    iterations: int = 3
) -> Dict[str, Any]:
    """Run the benchmark with or without acceleration."""
    python_exe = get_venv_python(venv_dir)
    
    results = []
    
    for i in range(iterations):
        log_info(f"Running iteration {i+1}/{iterations} ({'with' if use_acceleration else 'without'} acceleration)")
        
        # Set environment variables
        env = os.environ.copy()
        env['WORKFLOW_TYPE'] = workflow_type
        
        if use_acceleration:
            env['FAST_CREWAI_ACCELERATION'] = '1'
        else:
            # Ensure acceleration is disabled
            env.pop('FAST_CREWAI_ACCELERATION', None)
        
        # Add fast_crewai.shim import if using acceleration
        cmd = [str(python_exe)]
        if use_acceleration:
            cmd.extend(['-c', f'import fast_crewai.shim; exec(open("{workflow_script}").read())'])
        else:
            cmd.append(str(workflow_script))
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=venv_dir,
                capture_output=True,
                text=True,
                env=env
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode != 0:
                log_error(f"Iteration {i+1} failed with return code {result.returncode}")
                log_error(f"Error output: {result.stderr}")
                continue
            
            # Extract timing from the output
            import re
            time_match = re.search(r'workflow completed in ([\d.]+) seconds', result.stdout.lower())
            actual_time = float(time_match.group(1)) if time_match else execution_time
            
            results.append({
                'total_time': execution_time,
                'actual_workflow_time': actual_time,
                'success': True,
                'output_length': len(result.stdout)
            })
            
        except Exception as e:
            log_error(f"Iteration {i+1} failed with exception: {e}")
            continue
    
    if not results:
        log_error("All iterations failed")
        return None
    
    # Calculate averages
    avg_total_time = sum(r['total_time'] for r in results) / len(results)
    avg_workflow_time = sum(r['actual_workflow_time'] for r in results) / len(results)
    
    return {
        'iterations_run': len(results),
        'average_total_time': avg_total_time,
        'average_workflow_time': avg_workflow_time,
        'results': results
    }


def compare_performance(baseline_results: Dict, accelerated_results: Dict) -> Dict[str, Any]:
    """Compare baseline and accelerated performance."""
    if not baseline_results or not accelerated_results:
        return {"error": "Missing results to compare"}
    
    comparison = {}
    
    baseline_time = baseline_results['average_workflow_time']
    accelerated_time = accelerated_results['average_workflow_time']
    
    # Calculate improvement
    if accelerated_time > 0:
        improvement = baseline_time / accelerated_time
        comparison['improvement_factor'] = improvement
        comparison['time_saved'] = baseline_time - accelerated_time
        comparison['percent_improvement'] = (1 - accelerated_time / baseline_time) * 100
    else:
        comparison['improvement_factor'] = float('inf')
        comparison['time_saved'] = baseline_time
        comparison['percent_improvement'] = float('inf')
    
    comparison['baseline_time'] = baseline_time
    comparison['accelerated_time'] = accelerated_time
    
    return comparison


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare CrewAI performance with and without Fast-CrewAI acceleration"
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("./crewai_comparison_test"),
        help="Directory for test environment"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations for each test (default: 3)"
    )
    parser.add_argument(
        "--workflow-type",
        choices=["basic", "memory", "tools"],
        default="basic",
        help="Type of workflow to test: basic, memory-intensive, or tool-intensive"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installation steps (use existing environment)"
    )
    parser.add_argument(
        "--keep-env",
        action="store_true",
        help="Keep test environment after completion"
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
        log_info("Starting CrewAI vs Fast-CrewAI performance comparison")
        print()

        # Setup environment
        test_dir = args.test_dir
        test_dir.mkdir(parents=True, exist_ok=True)
        
        venv_dir = setup_test_environment(test_dir, args.skip_install)
        
        if not args.skip_install:
            log_info("Installing CrewAI and Fast-CrewAI...")
            install_fast_crewai(venv_dir, fast_crewai_dir)
            log_success("Installation completed")
        else:
            log_info("Using existing environment")
        print()

        # Create test workflow script
        workflow_script = create_test_workflow_script(venv_dir, test_dir)
        log_success("Test workflow script created")
        print()

        # Run without acceleration (baseline)
        log_info(f"Running baseline test ({args.workflow_type} workflow) without Fast-CrewAI acceleration...")
        baseline_results = run_benchmark(
            venv_dir, workflow_script, use_acceleration=False,
            workflow_type=args.workflow_type, iterations=args.iterations
        )
        
        if not baseline_results:
            log_error("Baseline test failed - cannot proceed with comparison")
            return 1

        print()
        log_info(f"Baseline completed - Average time: {baseline_results['average_workflow_time']:.2f}s")

        # Run with acceleration
        log_info(f"Running accelerated test ({args.workflow_type} workflow) with Fast-CrewAI acceleration...")
        accelerated_results = run_benchmark(
            venv_dir, workflow_script, use_acceleration=True,
            workflow_type=args.workflow_type, iterations=args.iterations
        )
        
        if not accelerated_results:
            log_error("Accelerated test failed")
            return 1

        print()
        log_info(f"Accelerated test completed - Average time: {accelerated_results['average_workflow_time']:.2f}s")

        # Compare results
        comparison = compare_performance(baseline_results, accelerated_results)
        
        print()
        log_performance("PERFORMANCE COMPARISON RESULTS")
        print("=" * 60)
        print(f"Workflow Type: {args.workflow_type}")
        print(f"Iterations: {args.iterations}")
        print(f"Baseline (without Fast-CrewAI): {baseline_results['average_workflow_time']:.4f}s")
        print(f"Accelerated (with Fast-CrewAI): {accelerated_results['average_workflow_time']:.4f}s")
        print(f"Time Saved: {comparison['time_saved']:.4f}s")
        print(f"Performance Improvement: {comparison['improvement_factor']:.2f}x faster")
        print(f"Percent Improvement: {comparison['percent_improvement']:.2f}%")
        print("=" * 60)

        # Save results to file
        results_file = test_dir / "comparison_results.json"
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'workflow_type': args.workflow_type,
            'iterations': args.iterations,
            'baseline_results': baseline_results,
            'accelerated_results': accelerated_results,
            'comparison': comparison
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        log_success(f"Comparison completed! Results saved to {results_file}")
        
        # Cleanup
        if not args.keep_env:
            print()
            response = input("Keep test environment for inspection? [y/N] ").strip().lower()
            if response not in ['y', 'yes']:
                log_info("Cleaning up test environment...")
                shutil.rmtree(test_dir)
                log_success("Cleanup complete")
            else:
                log_info(f"Test environment kept at: {test_dir}")
        else:
            log_info(f"Test environment kept at: {test_dir}")

        return 0

    except KeyboardInterrupt:
        print()
        log_warning("Comparison interrupted by user")
        return 130
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
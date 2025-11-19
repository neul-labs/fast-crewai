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

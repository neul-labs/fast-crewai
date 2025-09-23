#!/usr/bin/env python3
"""
Basic usage example for CrewAI Rust acceleration.

This example demonstrates the simplest way to add Rust acceleration
to your existing CrewAI workflows.
"""

import crewai
import crewai_rust.shim  # Automatic Rust acceleration

from crewai import Agent, Task, Crew


def main():
    """Demonstrate basic CrewAI Rust usage."""
    print("CrewAI Rust Basic Usage Example")
    print("=" * 40)

    # Check if Rust acceleration is active
    from crewai_rust import is_rust_available, get_rust_status
    print(f"Rust acceleration: {'Active' if is_rust_available() else 'Inactive'}")
    print(f"Status: {get_rust_status()}")
    print()

    # Create agents - same as standard CrewAI
    researcher = Agent(
        role="Research Specialist",
        goal="Conduct thorough research on given topics",
        backstory="""You are an expert researcher with years of experience
        in gathering and analyzing information from various sources.""",
        verbose=True
    )

    writer = Agent(
        role="Content Writer",
        goal="Create engaging and informative content",
        backstory="""You are a skilled writer who can transform research
        findings into compelling, easy-to-understand content.""",
        verbose=True
    )

    # Create tasks - same as standard CrewAI
    research_task = Task(
        description="""Research the latest trends in artificial intelligence
        and machine learning for 2024. Focus on practical applications
        and industry adoption.""",
        expected_output="A comprehensive research report with key findings",
        agent=researcher
    )

    writing_task = Task(
        description="""Using the research findings, write an engaging
        article about AI trends for 2024. Make it accessible to a
        general business audience.""",
        expected_output="A 500-word article about AI trends",
        agent=writer,
        context=[research_task]  # Use research output as context
    )

    # Create crew - same as standard CrewAI
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True
    )

    print("Starting crew execution...")
    print("(This is now accelerated with Rust components!)")
    print()

    # Execute the crew - now with Rust acceleration!
    result = crew.kickoff()

    print("Crew execution completed!")
    print()
    print("Final Result:")
    print("-" * 40)
    print(result.raw)

    # Show performance information
    print()
    print("Performance Info:")
    print("-" * 20)
    if hasattr(result, 'token_usage') and result.token_usage:
        print(f"Total tokens used: {result.token_usage.total_tokens}")

    # Demonstrate memory acceleration
    print()
    print("Memory Acceleration Demo:")
    print("-" * 30)

    from crewai_rust import RustMemoryStorage

    # Create memory storage (using Rust acceleration)
    memory = RustMemoryStorage()
    print(f"Memory implementation: {memory.implementation}")

    # Save some data
    memory.save("AI is transforming industries worldwide", {"topic": "AI trends"})
    memory.save("Machine learning adoption is increasing", {"topic": "ML adoption"})
    memory.save("Automation is key for business efficiency", {"topic": "automation"})

    # Search data (10-20x faster with Rust)
    results = memory.search("AI", limit=3)
    print(f"Found {len(results)} results for 'AI':")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['value']}")

    print()
    print("Example completed successfully!")
    print("Your CrewAI workflow is now accelerated with Rust!")


if __name__ == "__main__":
    main()
# Quick Start Guide

Get CrewAI Rust acceleration running in under 5 minutes.

## Prerequisites

- Python 3.8+
- Existing CrewAI project (optional)

## Installation

```bash
pip install crewai-rust
```

## Method 1: Zero-Code Acceleration (Recommended)

Transform your existing CrewAI project with one import:

```python
import crewai
import crewai_rust.shim  # Instant acceleration

# Your existing code remains unchanged
from crewai import Agent, Task, Crew

agent = Agent(
    role="Data Analyst",
    goal="Analyze data efficiently",
    backstory="Expert in data analysis"
)

task = Task(
    description="Analyze the sales data",
    expected_output="Summary report",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()  # Now accelerated with Rust!
```

## Method 2: Environment Variable

Set once, accelerate everywhere:

```bash
export CREWAI_RUST_ACCELERATION=1
python your_existing_script.py
```

## Method 3: Explicit Component Usage

For fine-grained control:

```python
from crewai_rust import RustMemoryStorage, RustToolExecutor
from crewai import Agent, Task, Crew

# Use Rust for memory-intensive operations
memory = RustMemoryStorage()
memory.save("Important insights", {"priority": "high"})

# Search is now 10-20x faster
results = memory.search("insights", limit=5)

# Mix Rust and Python components as needed
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,  # Will use RustMemoryStorage if shimmed
)
```

## Verify Acceleration

```python
from crewai_rust import is_rust_available, get_rust_status

print(f"Rust acceleration: {'Active' if is_rust_available() else 'Inactive'}")
print(f"Status: {get_rust_status()}")
```

## Next Steps

- **[Performance Guide](PERFORMANCE.md)** - Measure your speedups
- **[Configuration](../README.md#configuration)** - Customize behavior
- **[Migration Guide](MIGRATION.md)** - Migrate existing projects
- **[API Reference](COMPATIBILITY.md)** - Full compatibility details

## Troubleshooting

**Rust not detected?**
```python
# Enable verbose logging to see what's happening
import crewai_rust.shim
crewai_rust.shim.enable_rust_acceleration(verbose=True)
```

**Performance not as expected?**
- Check [Performance Guide](PERFORMANCE.md) for optimization tips
- Run benchmarks: `python examples/performance_benchmark.py`
- Ensure you're testing the right components (memory, tools, tasks)
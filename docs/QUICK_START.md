# Quick Start Guide

Get Fast-CrewAI up and running with your existing CrewAI projects in minutes.

## Prerequisites

- Python 3.9+
- CrewAI installed in your project
- Optional: Rust toolchain (for maximum performance)

## Installation

### Standard Installation

Install Fast-CrewAI using pip:

```bash
pip install fast-crewai
```

### For Development

```bash
git clone https://github.com/neul-labs/fast-crewai.git
cd fast-crewai
pip install -e .

# Optional: Build Rust extension for maximum performance
pip install maturin
maturin develop --release
```

## Basic Usage

### Option 1: Import Shim (Recommended)

Add one line to your existing CrewAI code:

```python
# Add this at the top of your main file
import fast_crewai.shim  # Activates acceleration

# Your existing CrewAI code remains unchanged!
from crewai import Agent, Task, Crew

# Create and run your agents as usual
researcher = Agent(
    role="Researcher",
    goal="Discover new insights",
    backstory="An experienced researcher"
)

task = Task(
    description="Analyze market trends",
    agent=researcher
)

crew = Crew(
    agents=[researcher],
    tasks=[task]
)

result = crew.kickoff()
```

### Option 2: Environment Variable

Set an environment variable before running your script:

```bash
export FAST_CREWAI_ACCELERATION=1
python your_crewai_script.py
```

## Configuration

### Environment Variables

Control Fast-CrewAI behavior with these environment variables:

```bash
# Enable/disable all acceleration
export FAST_CREWAI_ACCELERATION=1    # Enable (default)
export FAST_CREWAI_ACCELERATION=0    # Disable

# Component-specific control
export FAST_CREWAI_MEMORY=true       # Memory acceleration
export FAST_CREWAI_DATABASE=true     # Database acceleration  
export FAST_CREWAI_TOOLS=false       # Tool acceleration
export FAST_CREWAI_TASKS=auto        # Task acceleration
```

## Verification

Check that Fast-CrewAI is working:

```python
import fast_crewai.shim

# Check acceleration status
from fast_crewai import get_acceleration_status
status = get_acceleration_status()
print(f"Acceleration available: {status['available']}")
```

## API Key Configuration

Fast-CrewAI tests work with both real and fake API keys:

### Using Real API Keys
```bash
export OPENAI_API_KEY="your-actual-api-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Using Fake API Keys (Default for Tests)
The test scripts automatically use fake keys when no real keys are present, avoiding costs while testing functionality.

### Testing with Keys
```bash
# Will use real keys if present, fake keys otherwise
make test-comparison
```

## Running Benchmarks

Compare performance with and without acceleration:

```bash
# Quick comparison
make test-comparison

# Extensive comparison (1000 iterations)
make test-comparison-extensive
```

## Troubleshooting

### Issues with Monkey Patching

If you encounter issues, try disabling acceleration temporarily:

```bash
export FAST_CREWAI_ACCELERATION=0
python your_script.py
```

### Performance Not Improving

- Ensure your Rust extensions are built: `maturin develop`
- Check that your workflows are suitable for acceleration (memory/database heavy tasks benefit most)
- Run with `FAST_CREWAI_MEMORY=true` and `FAST_CREWAI_DATABASE=true` explicitly

## Next Steps

- Learn about [Architecture](./ARCHITECTURE.md) to understand how it works
- Check [Performance](./PERFORMANCE.md) for detailed benchmarking
- Review [Troubleshooting](./TROUBLESHOOTING.md) for common issues
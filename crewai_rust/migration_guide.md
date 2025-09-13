# Migration Guide: Integrating CrewAI Rust Components

This guide explains how to integrate the new Rust components into existing CrewAI applications with zero breaking changes.

## Overview

The CrewAI Rust integration is designed as a drop-in enhancement that provides significant performance improvements while maintaining full backward compatibility. Existing code continues to work without modification, while new capabilities are available for those who want to leverage them.

## Installation

### For Existing Users

If you're already using CrewAI, you can enhance it with Rust components:

```bash
pip install --upgrade crewai[all]
```

Or install just the Rust components:

```bash
pip install crewai-rust
```

### For New Users

```bash
pip install crewai[all]
```

## Zero-Breaking Changes Approach

The Rust integration follows these principles:

1. **Automatic Detection**: Components automatically detect and use Rust when available
2. **Graceful Fallback**: If Rust is not available, Python implementations are used
3. **Identical APIs**: All public APIs remain exactly the same
4. **No Code Changes Required**: Existing code works without modification

## Integration Strategies

### Strategy 1: Automatic Enhancement (Recommended)

Simply install the package and enjoy performance improvements automatically:

```python
from crewai import Crew, Agent, Task

# Your existing code works exactly the same
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True  # Now uses Rust-enhanced memory when available
)

result = crew.kickoff()
```

The existing CrewAI memory system will automatically use the Rust backend when available, providing transparent performance improvements.

### Strategy 2: Explicit Usage

For more control, you can explicitly use Rust components:

```python
from crewai import Crew, Agent, Task
from crewai_rust.integration import RustMemoryIntegration

# Create a crew with explicitly Rust-enhanced memory
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,
    short_term_memory=RustMemoryIntegration.create_short_term_memory(),
    long_term_memory=RustMemoryIntegration.create_long_term_memory()
)
```

### Strategy 3: Selective Enhancement

Enable specific Rust components while keeping others on Python:

```python
import os

# Enable only specific components
os.environ['CREWAI_RUST_MEMORY'] = 'true'
os.environ['CREWAI_RUST_TOOLS'] = 'true'
os.environ['CREWAI_RUST_TASKS'] = 'false'  # Keep tasks on Python
os.environ['CREWAI_RUST_SERIALIZATION'] = 'true'
os.environ['CREWAI_RUST_DATABASE'] = 'true'

# Now import and use CrewAI as usual
from crewai import Crew
# Memory, tools, serialization, and database operations will use Rust
# Task execution will use Python
```

### Strategy 4: Programmatic Configuration

Configure components programmatically at runtime:

```python
from crewai_rust.utils import configure_rust_components

# Configure which components to use
configure_rust_components(
    memory=True,      # Use Rust for memory operations
    tools=True,       # Use Rust for tool execution
    tasks=False,      # Keep tasks on Python
    serialization=True,  # Use Rust for serialization
    database=True     # Use Rust for database operations
)

# Now use CrewAI normally
from crewai import Crew
```

## Component-Specific Migration

### Memory System

**Before** (no changes needed):
```python
from crewai import Crew

crew = Crew(
    # ... other parameters
    memory=True
)
```

**After** (automatic enhancement):
```python
# Same code, now with Rust performance when available
from crewai import Crew

crew = Crew(
    # ... other parameters
    memory=True  # Automatically uses Rust when available
)
```

### Tool Execution

**Before** (no changes needed):
```python
from crewai.tools import tool

@tool
def calculator_tool(operation: str, operands: list) -> str:
    # Tool implementation
    pass

# Use tool in agent
agent = Agent(
    tools=[calculator_tool]
)
```

**After** (automatic enhancement):
```python
# Same code, now with stack-safe Rust execution when available
from crewai.tools import tool

@tool
def calculator_tool(operation: str, operands: list) -> str:
    # Tool implementation (unchanged)
    pass

# Use tool in agent (unchanged)
agent = Agent(
    tools=[calculator_tool]  # Automatically uses Rust when available
)
```

### Task Execution

**Before** (no changes needed):
```python
from crewai import Task

task = Task(
    description="Process data",
    expected_output="Processed results"
)
```

**After** (automatic enhancement):
```python
# Same code, now with concurrent Rust execution when available
from crewai import Task

task = Task(
    description="Process data",
    expected_output="Processed results"  # Automatically uses Rust when available
)
```

## Environment Configuration

### Environment Variables

Control which components use Rust implementations:

```bash
# Enable all Rust components
export CREWAI_RUST_MEMORY=true
export CREWAI_RUST_TOOLS=true
export CREWAI_RUST_TASKS=true
export CREWAI_RUST_SERIALIZATION=true
export CREWAI_RUST_DATABASE=true

# Disable specific components
export CREWAI_RUST_MEMORY=false  # Use Python for memory

# Auto-detect (default behavior)
export CREWAI_RUST_MEMORY=auto
```

### Runtime Configuration

```python
from crewai_rust.utils import configure_rust_components

# Configure at application startup
configure_rust_components(
    memory=True,      # Enable Rust memory
    tools=False,      # Keep tools on Python
    tasks=True,       # Enable Rust tasks
    serialization=True,   # Enable Rust serialization
    database=False    # Keep database on Python
)
```

## Testing Your Migration

### Verify Rust Availability

```python
from crewai_rust.utils import get_rust_status

status = get_rust_status()
print(f"Rust available: {status['available']}")
if status['available']:
    print("Components available:")
    for component, available in status['components'].items():
        print(f"  {component}: {'✓' if available else '✗'}")
```

### Performance Testing

```python
from crewai_rust.benchmark import PerformanceBenchmark

# Run benchmarks to verify improvements
benchmark = PerformanceBenchmark(iterations=1000)
results = benchmark.run_all_benchmarks()
benchmark.print_summary()
```

### Backward Compatibility Testing

Ensure your existing tests still pass:

```bash
# Run your existing test suite
pytest tests/

# Run the Rust integration tests
python -m pytest crewai_rust/test_comprehensive.py
```

## Troubleshooting

### Rust Components Not Loading

1. **Verify installation**:
   ```bash
   python -c "from crewai_rust import HAS_RUST_IMPLEMENTATION; print(HAS_RUST_IMPLEMENTATION)"
   ```

2. **Check environment variables**:
   ```bash
   python -m crewai_rust env
   ```

3. **Run status check**:
   ```bash
   python -m crewai_rust status
   ```

### Performance Issues

1. **Verify Rust is being used**:
   ```python
   from crewai_rust.memory import RustMemoryStorage
   memory = RustMemoryStorage()
   print(f"Implementation: {memory.implementation}")
   ```

2. **Run benchmarks**:
   ```bash
   python -m crewai_rust bench
   ```

### Fallback to Python

If you need to force Python implementations for debugging:

```python
import os
os.environ['CREWAI_RUST_MEMORY'] = 'false'
os.environ['CREWAI_RUST_TOOLS'] = 'false'
os.environ['CREWAI_RUST_TASKS'] = 'false'
os.environ['CREWAI_RUST_SERIALIZATION'] = 'false'
os.environ['CREWAI_RUST_DATABASE'] = 'false'
```

## Best Practices

### 1. Start with Memory Components

Memory operations typically show the biggest performance gains:

```python
# This provides immediate benefits with zero code changes
crew = Crew(
    memory=True  # Now uses Rust when available
)
```

### 2. Monitor Performance

Use the benchmarking tools to verify improvements:

```python
from crewai_rust.benchmark import run_benchmarks
results = run_benchmarks()
```

### 3. Gradual Rollout

Enable components gradually in production:

```python
# Start with memory and serialization
os.environ['CREWAI_RUST_MEMORY'] = 'true'
os.environ['CREWAI_RUST_SERIALIZATION'] = 'true'

# Later enable tools and tasks
# os.environ['CREWAI_RUST_TOOLS'] = 'true'
# os.environ['CREWAI_RUST_TASKS'] = 'true'
```

### 4. Maintain Fallback Capability

Ensure your application works even when Rust components aren't available:

```python
from crewai_rust.utils import is_rust_available

if is_rust_available():
    print("Rust components available - optimized performance")
else:
    print("Using Python implementations - full functionality maintained")
```

## Conclusion

The CrewAI Rust integration provides significant performance improvements with zero breaking changes to existing code. By following this migration guide, you can enhance your applications while maintaining full backward compatibility.

The key benefits:
- **No code changes required** for existing applications
- **Automatic performance improvements** when Rust is available
- **Graceful fallback** to Python when Rust isn't available
- **Full API compatibility** with existing CrewAI code
- **Selective enhancement** capabilities for fine-grained control

Start enjoying the performance benefits today by simply upgrading to the latest version of CrewAI!
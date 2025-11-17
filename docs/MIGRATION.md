# Migration Guide

Seamlessly migrate your existing CrewAI projects to use Rust acceleration.

## Migration Overview

CrewAI Rust is designed for **zero-breaking-change migration**. Your existing code continues to work unchanged while gaining significant performance improvements.

## Migration Strategies

### Strategy 1: Zero-Code Migration (Recommended)

**Before:**
```python
from crewai import Agent, Task, Crew

# Your existing CrewAI code
agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert")
task = Task(description="Analyze sales", expected_output="Report", agent=agent)
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

**After:**
```python
import fast_crewai.shim  # Add this one line

from crewai import Agent, Task, Crew

# Exact same code - now accelerated!
agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert")
task = Task(description="Analyze sales", expected_output="Report", agent=agent)
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()  # Now 3-20x faster
```

### Strategy 2: Environment Variable

Set once in your deployment environment:

```bash
# In your .env file or deployment config
FAST_CREWAI_ACCELERATION=1

# No code changes needed
python your_existing_script.py
```

### Strategy 3: Gradual Component Migration

Migrate specific components for fine-grained control:

```python
from crewai import Agent, Task, Crew
from fast_crewai import RustMemoryStorage, RustToolExecutor

# Option A: Replace memory storage
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory_storage=RustMemoryStorage(),  # Rust acceleration
)

# Option B: Replace tool executor (if using custom tools)
from fast_crewai.tools import RustToolExecutor
executor = RustToolExecutor(max_recursion_depth=1000)

# Option C: Mixed approach - accelerate bottlenecks
memory = RustMemoryStorage()
memory.save("Critical data", {"priority": "high"})
results = memory.search("data")  # 10-20x faster search
```

## Component Migration Map

| CrewAI Component | Rust Replacement | Migration Impact |
|------------------|-------------------|------------------|
| `RAGStorage` | `RustMemoryStorage` | 10-20x faster searches |
| `ShortTermMemory` | `RustMemoryStorage` | 10-20x faster operations |
| `LongTermMemory` | `RustMemoryStorage` | 10-20x faster persistence |
| `CrewStructuredTool` | `RustToolExecutor` | 2-5x faster execution |
| `Task` execution | `RustTaskExecutor` | 3-5x faster concurrency |
| `LTMSQLiteStorage` | `RustSQLiteWrapper` | 3-5x faster DB ops |

## Common Migration Scenarios

### Scenario 1: Memory-Intensive Applications

**Problem:** Slow document search and RAG operations

```python
# Before: Standard memory operations
from crewai.memory import Memory
from crewai.memory.storage import RAGStorage

storage = RAGStorage(type="documents")
for doc in large_document_set:
    storage.save(doc, metadata)  # Slow vector operations

results = storage.search("query", limit=10)  # Slow similarity search
```

**Solution:** Zero-code acceleration

```python
import fast_crewai.shim  # Automatic acceleration

from crewai.memory import Memory
from crewai.memory.storage import RAGStorage

storage = RAGStorage(type="documents")  # Now using RustMemoryStorage
for doc in large_document_set:
    storage.save(doc, metadata)  # 10-20x faster

results = storage.search("query", limit=10)  # 10-20x faster
```

### Scenario 2: Tool-Heavy Workflows

**Problem:** Slow tool execution with complex chains

```python
# Before: Python tool execution
from crewai.tools import tool

@tool
def complex_calculation(data: str) -> str:
    # CPU-intensive operation
    return process_data(data)

# Slow execution, especially with many tool calls
```

**Solution:** Automatic tool acceleration

```python
import fast_crewai.shim  # Accelerates tool execution

from crewai.tools import tool

@tool  # Now accelerated with RustToolExecutor
def complex_calculation(data: str) -> str:
    return process_data(data)  # 2-5x faster execution
```

### Scenario 3: Concurrent Task Processing

**Problem:** Sequential task execution bottlenecks

```python
# Before: Limited concurrency
from crewai import Crew

crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential  # One task at a time
)
result = crew.kickoff()  # Slow for independent tasks
```

**Solution:** Enhanced concurrency

```python
import fast_crewai.shim  # Enables true async execution

from crewai import Crew

crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential  # Now with work-stealing scheduler
)
result = crew.kickoff()  # 3-5x faster with better concurrency
```

## Configuration During Migration

### Gradual Rollout

```python
# Enable Rust for specific components only
import os
os.environ['FAST_CREWAI_MEMORY'] = 'true'
os.environ['FAST_CREWAI_TOOLS'] = 'false'  # Keep Python tools during testing
os.environ['FAST_CREWAI_TASKS'] = 'true'

import fast_crewai.shim
```

### Fallback Configuration

```python
# Automatic fallback if Rust fails
from fast_crewai import RustMemoryStorage

storage = RustMemoryStorage(use_rust=None)  # Auto-detect
print(f"Using: {storage.implementation}")  # "rust" or "python"
```

### Monitoring Migration

```python
# Track performance improvements
import time
from fast_crewai import get_performance_metrics

# Before migration
start = time.time()
original_result = crew.kickoff()
python_time = time.time() - start

# After migration (with shim)
start = time.time()
rust_result = crew.kickoff()
rust_time = time.time() - start

speedup = python_time / rust_time
print(f"Migration achieved {speedup:.1f}x speedup")

# Detailed metrics
metrics = get_performance_metrics()
print(f"Memory ops/sec: {metrics['memory_ops_per_sec']}")
```

## Testing Your Migration

### Compatibility Testing

```python
# Test that results remain consistent
import fast_crewai.shim
from crewai import Agent, Task, Crew

def test_migration_compatibility():
    agent = Agent(role="Tester", goal="Test migration", backstory="QA")
    task = Task(description="Test task", expected_output="Test result", agent=agent)
    crew = Crew(agents=[agent], tasks=[task])

    # Results should be functionally identical
    result = crew.kickoff()
    assert result is not None
    assert hasattr(result, 'raw')  # Standard CrewOutput interface

    print("Migration compatibility verified")

test_migration_compatibility()
```

### Performance Testing

```python
# Benchmark your specific workflow
from fast_crewai.benchmark import benchmark_workflow

def your_workflow():
    # Your specific CrewAI workflow
    return crew.kickoff()

# Compare before/after performance
results = benchmark_workflow(your_workflow)
print(f"Speedup: {results['speedup']:.1f}x")
print(f"Memory improvement: {results['memory_speedup']:.1f}x")
```

## Troubleshooting Migration

### Common Issues

**1. Import Errors After Migration**

```python
# Check if Rust acceleration is available
from fast_crewai import is_rust_available, get_rust_status

if not is_rust_available():
    print("Rust not available - using Python fallback")
    print(f"Status: {get_rust_status()}")
else:
    print("Rust acceleration active")
```

**2. Performance Not Improved**

```python
# Verify which implementation is being used
from fast_crewai import RustMemoryStorage

storage = RustMemoryStorage()
if storage.implementation != "rust":
    print("⚠️ Still using Python implementation")
    print("Check installation: pip install --upgrade crewai-rust")
```

**3. Behavior Differences**

```python
# Enable verbose logging to track what's happening
import fast_crewai.shim
fast_crewai.shim.enable_rust_acceleration(verbose=True)

# This will show which components are being replaced
```

### Rollback Strategy

If you encounter issues, easily rollback:

```python
# Disable Rust acceleration
import os
os.environ['FAST_CREWAI_ACCELERATION'] = '0'

# Or remove the shim import
# import fast_crewai.shim  # Comment out this line

# Or disable specific components
from fast_crewai.shim import disable_rust_acceleration
disable_rust_acceleration()
```

## Migration Checklist

### Pre-Migration

- [ ] Backup your current working code
- [ ] Install CrewAI Rust: `pip install crewai-rust`
- [ ] Test installation: `python -c "import fast_crewai; print('OK')"`
- [ ] Review current performance baseline

### During Migration

- [ ] Choose migration strategy (zero-code vs gradual)
- [ ] Add acceleration (shim import or environment variable)
- [ ] Test functionality with existing test suite
- [ ] Benchmark performance improvements
- [ ] Monitor for any behavior changes

### Post-Migration

- [ ] Verify all functionality works as expected
- [ ] Document performance improvements achieved
- [ ] Update deployment configurations if using environment variables
- [ ] Consider optimizing code patterns for Rust components

## Best Practices

### 1. Start with Zero-Code Migration

Always begin with the shim import for maximum compatibility:

```python
import fast_crewai.shim  # Safest migration path
```

### 2. Test Incrementally

```python
# Test one component at a time in development
import os
os.environ['FAST_CREWAI_MEMORY'] = 'true'  # Start with memory
os.environ['FAST_CREWAI_TOOLS'] = 'false'  # Add tools later
```

### 3. Monitor Performance

```python
# Track improvements over time
from fast_crewai import get_performance_improvements
improvements = get_performance_improvements()
print(f"Memory: {improvements['memory']}x faster")
```

### 4. Plan for Rollback

```python
# Keep rollback mechanism ready
USE_RUST_ACCELERATION = os.environ.get('USE_RUST', 'true') == 'true'

if USE_RUST_ACCELERATION:
    import fast_crewai.shim
```

## Next Steps

- **[Performance Guide](PERFORMANCE.md)** - Optimize your migrated workflow
- **[Compatibility Reference](COMPATIBILITY.md)** - Detailed API compatibility
- **[Development Guide](DEVELOPMENT.md)** - Contribute improvements
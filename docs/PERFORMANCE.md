# Performance Guide

Comprehensive benchmarks and optimization strategies for CrewAI Rust.

## Performance Overview

| Component | Speedup | Use Case | Optimization |
|-----------|---------|----------|--------------|
| **Memory Storage** | 10-20x | Large document search, RAG operations | SIMD vectorization |
| **Tool Execution** | 2-5x | Heavy tool usage, recursive calls | Zero-cost abstractions |
| **Task Execution** | 3-5x | Parallel task workflows | Async runtime |
| **Serialization** | 5-10x | Event processing, logging | Zero-copy operations |
| **Database Operations** | 3-5x | Memory persistence | Connection pooling |

## Benchmarking

### Run Built-in Benchmarks

```python
from crewai_rust.benchmark import run_benchmarks

# Run all benchmarks
results = run_benchmarks()
print(f"Memory: {results['memory_speedup']:.1f}x faster")
print(f"Tools: {results['tool_speedup']:.1f}x faster")
print(f"Tasks: {results['task_speedup']:.1f}x faster")

# Run specific benchmarks
from crewai_rust.benchmark import (
    benchmark_memory_storage,
    benchmark_tool_execution,
    benchmark_serialization
)

memory_results = benchmark_memory_storage()
tool_results = benchmark_tool_execution()
serialization_results = benchmark_serialization()
```

### Custom Benchmarks

```python
import time
from crewai_rust import RustMemoryStorage

# Benchmark memory operations
def benchmark_memory():
    storage = RustMemoryStorage()

    # Test data
    documents = [f"Document {i} with substantial content" for i in range(1000)]

    # Benchmark saves
    start = time.time()
    for doc in documents:
        storage.save(doc, {"index": i})
    save_time = time.time() - start

    # Benchmark searches
    start = time.time()
    for i in range(100):
        results = storage.search("Document", limit=5)
    search_time = time.time() - start

    print(f"Save: {len(documents)/save_time:.1f} docs/sec")
    print(f"Search: {100/search_time:.1f} queries/sec")

benchmark_memory()
```

## Memory Storage Optimization

### Optimal Usage Patterns

**Optimal Usage:**
```python
from crewai_rust import RustMemoryStorage

# Large batch operations
storage = RustMemoryStorage()
documents = load_large_dataset()  # 10k+ documents

for doc in documents:
    storage.save(doc, metadata)  # Vectorized internally

# Batch searching
queries = ["query1", "query2", "query3"]
for query in queries:
    results = storage.search(query, limit=10)
```

**Suboptimal Usage:**
```python
# Too many small storage instances
for doc in documents:
    storage = RustMemoryStorage()  # Don't recreate
    storage.save(doc)
```

### Memory Configuration

```python
# Optimize for your use case
storage = RustMemoryStorage(
    use_rust=True,  # Force Rust implementation
    # Additional config via environment
)

# Environment tuning
import os
os.environ['CREWAI_RUST_MEMORY_THREADS'] = '4'  # Parallel processing
os.environ['CREWAI_RUST_MEMORY_BATCH_SIZE'] = '100'  # Batch operations
```

## Tool Execution Optimization

### Recursion Safety

```python
from crewai_rust import RustToolExecutor

# Configure for deep tool chains
executor = RustToolExecutor(max_recursion_depth=10000)

# This is now safe and fast
def recursive_tool(depth):
    if depth <= 0:
        return "base case"
    return executor.execute_tool("recursive_tool", {"depth": depth - 1})

result = recursive_tool(5000)  # No stack overflow
```

### Tool Performance Patterns

**Optimized Tool Usage:**
```python
# Batch tool executions
tools = ["tool1", "tool2", "tool3"]
args_list = [{"param": i} for i in range(100)]

# Execute in parallel
results = []
for tool, args in zip(tools, args_list):
    result = executor.execute_tool(tool, args)
    results.append(result)
```

## Task Execution Optimization

### Concurrent Task Design

```python
from crewai_rust import RustTaskExecutor

executor = RustTaskExecutor()

# Design for parallelism
tasks = [
    "Analyze dataset A",
    "Process files B",
    "Generate report C"
]

# True concurrency with work-stealing
results = executor.execute_concurrent_tasks(tasks)
```

### Task Configuration

```python
# Environment tuning for task execution
import os
os.environ['CREWAI_RUST_TASK_THREADS'] = '8'  # Match CPU cores
os.environ['CREWAI_RUST_TASK_QUEUE_SIZE'] = '1000'
```

## Serialization Optimization

### Efficient Message Handling

```python
from crewai_rust.serialization import AgentMessage, RustSerializer

# Batch serialization for best performance
serializer = RustSerializer()
messages = [
    {"id": str(i), "content": f"Message {i}"}
    for i in range(1000)
]

# Zero-copy batch operation
json_strings = serializer.serialize_batch(messages)
```

## Database Operations

### Connection Pool Optimization

```python
from crewai_rust.database import RustSQLiteWrapper

# Configure connection pool
db = RustSQLiteWrapper(
    "database.db",
    pool_size=20,  # Adjust based on concurrency needs
)

# Batch operations for best performance
memories = [
    ("task1", {"data": "value1"}, "2023-01-01", 0.95),
    ("task2", {"data": "value2"}, "2023-01-02", 0.89),
    # ... more entries
]

for task, metadata, date, score in memories:
    db.save_memory(task, metadata, date, score)
```

## Real-World Performance

### Case Study: Document Processing Pipeline

```python
import time
from crewai import Agent, Task, Crew
from crewai_rust import RustMemoryStorage

# Before: Standard CrewAI
start = time.time()
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
python_time = time.time() - start

# After: CrewAI Rust
import crewai_rust.shim  # Enable acceleration

start = time.time()
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
rust_time = time.time() - start

speedup = python_time / rust_time
print(f"Overall speedup: {speedup:.1f}x")
```

### Performance Monitoring

```python
from crewai_rust import get_performance_metrics

# Get detailed performance stats
metrics = get_performance_metrics()
print(f"Memory operations: {metrics['memory_ops_per_sec']}")
print(f"Tool executions: {metrics['tool_exec_per_sec']}")
print(f"Task throughput: {metrics['task_throughput']}")
```

## Optimization Checklist

### High Impact Optimizations

- [ ] Enable Rust acceleration: `import crewai_rust.shim`
- [ ] Use batch operations for memory storage
- [ ] Configure appropriate recursion limits for tools
- [ ] Design tasks for parallel execution
- [ ] Use connection pooling for database operations

### Environment Tuning

- [ ] Set `CREWAI_RUST_ACCELERATION=1`
- [ ] Configure thread counts for your CPU
- [ ] Adjust batch sizes for your memory constraints
- [ ] Enable appropriate logging levels

### Code Patterns

- [ ] Reuse storage instances
- [ ] Batch API calls where possible
- [ ] Avoid deep object nesting in serialization
- [ ] Use appropriate data types (avoid strings for numbers)

## Troubleshooting Performance

### Performance Not as Expected?

```python
# Check what's actually being used
from crewai_rust import get_environment_info
info = get_environment_info()
print(info)

# Verify Rust components are active
from crewai_rust import RustMemoryStorage
storage = RustMemoryStorage()
assert storage.implementation == "rust", "Using Python fallback!"
```

### Profiling

```python
import cProfile
import crewai_rust.shim

def your_workflow():
    # Your CrewAI code here
    pass

# Profile with Rust acceleration
cProfile.run('your_workflow()', 'rust_profile.prof')
```

## Next Steps

- **[Architecture](ARCHITECTURE.md)** - Understand the technical details
- **[Development](DEVELOPMENT.md)** - Contribute performance improvements
- **[Compatibility](COMPATIBILITY.md)** - Ensure your code is optimized
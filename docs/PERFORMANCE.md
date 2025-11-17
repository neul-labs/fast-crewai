# Performance Guide

Comprehensive benchmarks and optimization strategies for CrewAI Rust.

## Performance Overview

| Component | Speedup | Use Case | Optimization |
|-----------|---------|----------|--------------|
| **Memory Storage** | 2-5x | Document search, RAG operations | TF-IDF similarity |
| **Tool Execution** | 1.5-3x | Heavy tool usage, recursive calls | Stack safety |
| **Task Execution** | 2-4x | Parallel task workflows | Tokio async runtime |
| **Serialization** | 3-8x | Event processing, logging | Zero-copy JSON |
| **Database Operations** | 2-4x | Memory persistence | Connection pooling |

*Note: Performance improvements vary based on workload characteristics and system configuration.*

## Benchmarking

### Run Built-in Benchmarks

```python
# Simple performance test
from fast_crewai import RustMemoryStorage, RustToolExecutor, RustTaskExecutor, AgentMessage
import time

def benchmark_memory():
    storage = RustMemoryStorage()
    
    # Test save performance
    start = time.time()
    for i in range(1000):
        storage.save(f"Document {i} with content")
    save_time = time.time() - start
    
    # Test search performance
    start = time.time()
    for i in range(100):
        results = storage.search("Document", limit=10)
    search_time = time.time() - start
    
    print(f"Save: {1000/save_time:.1f} docs/sec")
    print(f"Search: {100/search_time:.1f} queries/sec")
    return save_time, search_time

def benchmark_tools():
    executor = RustToolExecutor(max_recursion_depth=1000)
    
    start = time.time()
    for i in range(1000):
        result = executor.execute_tool("test", f"args_{i}")
    tool_time = time.time() - start
    
    print(f"Tools: {1000/tool_time:.1f} executions/sec")
    return tool_time

def benchmark_serialization():
    start = time.time()
    for i in range(10000):
        msg = AgentMessage(str(i), "sender", "recipient", f"content_{i}", i)
        json_str = msg.to_json()
    serialization_time = time.time() - start
    
    print(f"Serialization: {10000/serialization_time:.1f} messages/sec")
    return serialization_time

# Run benchmarks
print("Running performance benchmarks...")
benchmark_memory()
benchmark_tools()
benchmark_serialization()
```

### Custom Benchmarks

```python
import time
from fast_crewai import RustMemoryStorage

# Benchmark memory operations
def benchmark_memory():
    storage = RustMemoryStorage()

    # Test data
    documents = [f"Document {i} with substantial content" for i in range(1000)]

    # Benchmark saves
    start = time.time()
    for i, doc in enumerate(documents):
        storage.save(doc, {"index": i})
    save_time = time.time() - start

    # Benchmark searches
    start = time.time()
    for i in range(100):
        results = storage.search("Document", limit=5)
    search_time = time.time() - start

    print(f"Save: {len(documents)/save_time:.1f} docs/sec")
    print(f"Search: {100/search_time:.1f} queries/sec")
    
    return save_time, search_time

# Run benchmark
benchmark_memory()
```

## Memory Storage Optimization

### Optimal Usage Patterns

**Optimal Usage:**
```python
from fast_crewai import RustMemoryStorage

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
os.environ['FAST_CREWAI_MEMORY_THREADS'] = '4'  # Parallel processing
os.environ['FAST_CREWAI_MEMORY_BATCH_SIZE'] = '100'  # Batch operations
```

## Tool Execution Optimization

### Recursion Safety

```python
from fast_crewai import RustToolExecutor

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
from fast_crewai import RustTaskExecutor

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
os.environ['FAST_CREWAI_TASK_THREADS'] = '8'  # Match CPU cores
os.environ['FAST_CREWAI_TASK_QUEUE_SIZE'] = '1000'
```

## Serialization Optimization

### Efficient Message Handling

```python
from fast_crewai.serialization import AgentMessage, RustSerializer

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
from fast_crewai.database import RustSQLiteWrapper

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
from fast_crewai import RustMemoryStorage

# Test with and without Rust acceleration
def test_crewai_performance():
    agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert")
    task = Task(description="Analyze data", expected_output="Report", agent=agent)
    
    # Test without Rust acceleration
    start = time.time()
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    python_time = time.time() - start
    
    # Test with Rust acceleration
    import fast_crewai.shim  # Enable acceleration
    
    start = time.time()
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    rust_time = time.time() - start
    
    speedup = python_time / rust_time if rust_time > 0 else 1.0
    print(f"Overall speedup: {speedup:.1f}x")
    print(f"Python time: {python_time:.3f}s")
    print(f"Rust time: {rust_time:.3f}s")
    
    return speedup

# Run performance test
test_crewai_performance()
```

### Performance Monitoring

```python
from fast_crewai.utils import get_performance_improvements, get_rust_status

# Get expected performance improvements
improvements = get_performance_improvements()
for component, info in improvements.items():
    print(f"{component}: {info['improvement']} improvement")

# Check Rust status
status = get_rust_status()
print(f"Rust available: {status['available']}")
print(f"Components: {status['components']}")
```

## Optimization Checklist

### High Impact Optimizations

- [ ] Enable Rust acceleration: `import fast_crewai.shim`
- [ ] Use batch operations for memory storage
- [ ] Configure appropriate recursion limits for tools
- [ ] Design tasks for parallel execution
- [ ] Use connection pooling for database operations

### Environment Tuning

- [ ] Set `FAST_CREWAI_ACCELERATION=1`
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
from fast_crewai import get_environment_info
info = get_environment_info()
print(info)

# Verify Rust components are active
from fast_crewai import RustMemoryStorage
storage = RustMemoryStorage()
assert storage.implementation == "rust", "Using Python fallback!"
```

### Profiling

```python
import cProfile
import fast_crewai.shim

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
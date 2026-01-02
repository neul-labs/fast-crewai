# Performance Tuning

Comprehensive benchmarks and optimization strategies for Fast-CrewAI.

## Performance Overview

| Component | Speedup | Use Case |
|-----------|---------|----------|
| **Serialization** | 34x | Agent messages, event processing |
| **Tool Execution** | 17x | Heavy tool usage, repeated calls |
| **Database Search (FTS5)** | 11x | Memory search, full-text queries |
| **Database Query** | 1.3x | Memory persistence |
| **Memory Storage** | TF-IDF | Document search, RAG operations |
| **Task Execution** | Parallel | Dependency tracking, concurrent workflows |

## Memory Usage Savings

| Component | Python | Rust | Savings |
|-----------|--------|------|---------|
| Tool Execution | 1.2 MB | 0.0 MB | 99% less |
| Serialization | 8.0 MB | 3.4 MB | 58% less |
| Database | 0.1 MB | 0.1 MB | 31% less |

## Running Benchmarks

### Built-in Benchmark Suite

```bash
# Full benchmark suite
uv run python scripts/test_benchmarking.py --iterations 500 --report-output BENCHMARK.md

# Or using make
make benchmark
```

### Quick Python Benchmark

```python
from fast_crewai import (
    AcceleratedMemoryStorage,
    AcceleratedToolExecutor,
    AgentMessage
)
import time

def benchmark_memory():
    storage = AcceleratedMemoryStorage(use_rust=True)

    start = time.time()
    for i in range(1000):
        storage.save(f"Document {i} about machine learning and AI")
    save_time = time.time() - start

    start = time.time()
    for i in range(100):
        results = storage.search("machine learning", limit=10)
    search_time = time.time() - start

    print(f"Memory Save: {1000/save_time:.0f} docs/sec")
    print(f"Memory Search: {100/search_time:.0f} queries/sec")

def benchmark_tools():
    executor = AcceleratedToolExecutor(cache_ttl_seconds=300, use_rust=True)

    start = time.time()
    for i in range(1000):
        result = executor.execute_tool("test", {"query": f"args_{i}"})
    tool_time = time.time() - start

    stats = executor.get_stats()
    print(f"Tool Execution: {1000/tool_time:.0f} ops/sec")
    print(f"Cache hits: {stats.get('cache_hits', 0)}")

def benchmark_serialization():
    start = time.time()
    for i in range(10000):
        msg = AgentMessage(str(i), "sender", "recipient", f"content_{i}", i, use_rust=True)
        json_str = msg.to_json()
    ser_time = time.time() - start

    print(f"Serialization: {10000/ser_time:.0f} msgs/sec")

# Run all benchmarks
benchmark_memory()
benchmark_tools()
benchmark_serialization()
```

## Optimization Strategies

### Memory Storage

**Batch Operations**
```python
storage = AcceleratedMemoryStorage(use_rust=True)

# Good: Reuse storage instance
for doc in documents:
    storage.save(doc)

# Bad: Creating new instances
for doc in documents:
    storage = AcceleratedMemoryStorage()  # Overhead!
    storage.save(doc)
```

**Optimal Batch Sizes**
```python
batch_size = 1000
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    for doc in batch:
        storage.save(doc)
```

### Tool Execution

**Enable Caching**
```python
executor = AcceleratedToolExecutor(
    cache_ttl_seconds=300,  # 5 minute cache
    use_rust=True
)

# First call: executes
result1 = executor.execute_tool("search", {"query": "AI"})

# Second call: cache hit (17x faster!)
result2 = executor.execute_tool("search", {"query": "AI"})
```

**Monitor Cache Effectiveness**
```python
stats = executor.get_stats()
hit_rate = stats['cache_hits'] / max(stats['total_executions'], 1) * 100
print(f"Cache hit rate: {hit_rate:.1f}%")
```

### Database Operations

**Use FTS5 for Text Search**
```python
# Fast: FTS5 with BM25 ranking
results = db.search_memories_fts("machine learning", limit=10)

# Slow: LIKE queries
# results = db.execute_query("SELECT * FROM memories WHERE text LIKE '%machine learning%'")
```

**Configure Pool Size**
```python
# High-concurrency workloads
db = AcceleratedSQLiteWrapper(db_path="db.db", pool_size=50)
```

### Serialization

**Use Rust for High-Volume**
```python
# Always use Rust for message-heavy workflows
message = AgentMessage(
    id="...",
    sender="...",
    recipient="...",
    content="...",
    timestamp=123,
    use_rust=True  # 34x faster
)
```

### Task Execution

**Design for Parallelism**
```python
# Good: Independent tasks can run in parallel
executor.register_task("fetch_a", [])
executor.register_task("fetch_b", [])
executor.register_task("fetch_c", [])
executor.register_task("merge", ["fetch_a", "fetch_b", "fetch_c"])
```

## Optimization Checklist

### High Impact

- [ ] Enable Rust acceleration: `import fast_crewai.shim`
- [ ] Use batch operations for memory storage
- [ ] Enable tool result caching
- [ ] Use FTS5 for text search
- [ ] Design tasks for parallel execution

### Environment Tuning

- [ ] Set `FAST_CREWAI_ACCELERATION=1`
- [ ] Configure appropriate pool sizes
- [ ] Adjust cache TTL for your workload

### Code Patterns

- [ ] Reuse component instances
- [ ] Batch operations where possible
- [ ] Use appropriate data types
- [ ] Avoid deep object nesting

## Measuring Performance

### Profile Your Code

```python
import cProfile
import fast_crewai.shim

def your_workflow():
    # Your CrewAI code here
    pass

cProfile.run('your_workflow()', 'profile.prof')

# Analyze with snakeviz
# pip install snakeviz
# snakeviz profile.prof
```

### Compare With/Without Acceleration

```python
import time
import os

# Without acceleration
os.environ['FAST_CREWAI_ACCELERATION'] = '0'
start = time.time()
run_workflow()
baseline_time = time.time() - start

# With acceleration
os.environ['FAST_CREWAI_ACCELERATION'] = '1'
start = time.time()
run_workflow()
accelerated_time = time.time() - start

speedup = baseline_time / accelerated_time
print(f"Speedup: {speedup:.2f}x")
```

## Troubleshooting Performance

### Not Seeing Expected Speedups?

1. **Verify Rust is active**
    ```python
    from fast_crewai import is_acceleration_available
    print(f"Rust available: {is_acceleration_available()}")

    storage = AcceleratedMemoryStorage()
    print(f"Implementation: {storage.implementation}")
    ```

2. **Check for Python fallback**
    Look for "Using Python fallback" warnings in output.

3. **Profile to find bottlenecks**
    ```python
    import cProfile
    cProfile.run('your_code()')
    ```

### High Memory Usage

1. **Process in batches**
    ```python
    for batch in chunked(documents, 1000):
        for doc in batch:
            storage.save(doc)
        gc.collect()  # Optional
    ```

2. **Clear caches periodically**
    ```python
    executor.clear_cache()
    ```

### Slow Startup

First-time imports may be slower due to Rust extension loading. This is a one-time cost per Python process.

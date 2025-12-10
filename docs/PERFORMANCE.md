# Performance Guide

Comprehensive benchmarks and optimization strategies for Fast-CrewAI.

## Performance Overview

| Component | Speedup | Use Case | Optimization |
|-----------|---------|----------|--------------|
| **Serialization** | 🚀 **34.5x** | Agent messages, event processing | serde JSON |
| **Tool Execution** | 🚀 **17.3x** | Heavy tool usage, repeated calls | Result caching + serde validation |
| **Database Search (FTS5)** | 🚀 **11.2x** | Memory search, full-text queries | FTS5 + BM25 ranking |
| **Database Query** | 🚀 **1.3x** | Memory persistence | Connection pooling (r2d2) |
| **Memory Storage** | ✅ **TF-IDF** | Document search, RAG operations | Cosine similarity |
| **Task Execution** | ✅ **Dependency tracking** | Parallel workflows | Topological sort + Tokio |

### Memory Usage Savings

| Component | Python | Rust | Savings |
|-----------|--------|------|---------|
| Tool Execution | 1.2 MB | 0.0 MB | **99% less** |
| Serialization | 8.0 MB | 3.4 MB | **58% less** |
| Database | 0.1 MB | 0.1 MB | **31% less** |

*See [BENCHMARK.md](../BENCHMARK.md) for full benchmark data.*

*Note: Performance improvements vary based on workload characteristics and system configuration.*

## Benchmarking

### Run Built-in Benchmarks

```bash
# Run the full benchmark suite
uv run python scripts/test_benchmarking.py --iterations 500 --report-output BENCHMARK.md

# Or using make
make benchmark
```

### Quick Python Benchmark

```python
# Simple performance test
from fast_crewai import AcceleratedMemoryStorage, AcceleratedToolExecutor, AcceleratedTaskExecutor, AgentMessage
import time

def benchmark_memory():
    storage = AcceleratedMemoryStorage(use_rust=True)

    # Test save performance
    start = time.time()
    for i in range(1000):
        storage.save(f"Document {i} with content about machine learning and AI")
    save_time = time.time() - start

    # Test search performance (TF-IDF semantic search)
    start = time.time()
    for i in range(100):
        results = storage.search("machine learning", limit=10)
    search_time = time.time() - start

    print(f"Save: {1000/save_time:.1f} docs/sec")
    print(f"Search: {100/search_time:.1f} queries/sec")
    return save_time, search_time

def benchmark_tools():
    # Tool executor with caching (17x faster for repeated calls)
    executor = AcceleratedToolExecutor(
        max_recursion_depth=1000,
        cache_ttl_seconds=300,
        use_rust=True
    )

    start = time.time()
    for i in range(1000):
        result = executor.execute_tool("test", {"query": f"args_{i}"})
    tool_time = time.time() - start

    # Check cache stats
    stats = executor.get_stats()
    print(f"Tools: {1000/tool_time:.1f} executions/sec")
    print(f"Cache hits: {stats.get('cache_hits', 0)}")
    return tool_time

def benchmark_serialization():
    # serde-based serialization (34x faster)
    start = time.time()
    for i in range(10000):
        msg = AgentMessage(str(i), "sender", "recipient", f"content_{i}", i, use_rust=True)
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
from fast_crewai import AcceleratedMemoryStorage

# Benchmark memory operations
def benchmark_memory():
    storage = AcceleratedMemoryStorage(use_rust=True)

    # Test data
    documents = [f"Document {i} with substantial content about AI and machine learning" for i in range(1000)]

    # Benchmark saves
    start = time.time()
    for i, doc in enumerate(documents):
        storage.save(doc, {"index": i})
    save_time = time.time() - start

    # Benchmark searches (TF-IDF semantic search)
    start = time.time()
    for i in range(100):
        results = storage.search("machine learning AI", limit=5)
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
from fast_crewai import AcceleratedMemoryStorage

# Large batch operations
storage = AcceleratedMemoryStorage(use_rust=True)
documents = load_large_dataset()  # 10k+ documents

for doc in documents:
    storage.save(doc, metadata)  # TF-IDF indexed internally

# Semantic search (TF-IDF with cosine similarity)
queries = ["machine learning analysis", "data processing pipeline", "error handling"]
for query in queries:
    results = storage.search(query, limit=10)
```

**Suboptimal Usage:**
```python
# Too many small storage instances
for doc in documents:
    storage = AcceleratedMemoryStorage()  # Don't recreate
    storage.save(doc)
```

### Memory Configuration

```python
# Optimize for your use case
storage = AcceleratedMemoryStorage(
    use_rust=True,  # Force Rust implementation (TF-IDF search)
)

# Environment tuning
import os
os.environ['FAST_CREWAI_MEMORY'] = 'true'  # Enable memory acceleration
```

## Tool Execution Optimization

### Result Caching (17x faster)

```python
from fast_crewai import AcceleratedToolExecutor

# Configure for result caching (major speedup for repeated calls)
executor = AcceleratedToolExecutor(
    max_recursion_depth=10000,
    cache_ttl_seconds=300,  # Cache results for 5 minutes
    use_rust=True
)

# First call: executes tool
result1 = executor.execute_tool("search", {"query": "AI trends"})

# Second call with same args: instant cache hit (17x faster!)
result2 = executor.execute_tool("search", {"query": "AI trends"})

# Check cache statistics
stats = executor.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
```

### JSON Validation (serde-based)

```python
# Fast JSON argument validation using serde
executor = AcceleratedToolExecutor(use_rust=True)

# Validate before executing (much faster than Python json)
is_valid = executor.validate_args({"query": "test", "options": {"limit": 10}})

# Batch validation for multiple argument sets
args_list = [
    {"query": "test1"},
    {"query": "test2"},
    {"invalid": None}  # Will be caught
]
results = executor.batch_validate(args_list)  # [True, True, False]
```

### Tool Performance Patterns

**Optimized Tool Usage:**
```python
# Batch tool executions with caching
tools = ["search", "analyze", "summarize"]
args_list = [{"param": i} for i in range(100)]

results = []
for tool, args in zip(tools, args_list):
    result = executor.execute_tool(tool, args, use_cache=True)
    results.append(result)

# Clear cache when needed
cleared = executor.clear_cache()
```

## Task Execution Optimization

### Dependency Tracking & Topological Sort

```python
from fast_crewai import AcceleratedTaskExecutor

executor = AcceleratedTaskExecutor(use_rust=True)

# Register tasks with dependencies
executor.register_task("fetch_data", dependencies=[])
executor.register_task("clean_data", dependencies=["fetch_data"])
executor.register_task("analyze", dependencies=["clean_data"])
executor.register_task("visualize", dependencies=["clean_data"])
executor.register_task("report", dependencies=["analyze", "visualize"])

# Get optimal execution order (topological sort)
order = executor.get_execution_order()
print(f"Execution order: {order}")
# ['fetch_data', 'clean_data', 'analyze', 'visualize', 'report']

# Get tasks ready for execution
ready = executor.get_ready_tasks()
print(f"Ready to run: {ready}")  # ['fetch_data']

# Mark task completion
executor.mark_started("fetch_data")
executor.mark_completed("fetch_data", "data loaded")

# Now more tasks are ready
ready = executor.get_ready_tasks()
print(f"Ready to run: {ready}")  # ['clean_data']
```

### Cycle Detection

```python
# Automatically detects circular dependencies
executor = AcceleratedTaskExecutor(use_rust=True)
executor.register_task("A", dependencies=["B"])
executor.register_task("B", dependencies=["A"])

try:
    order = executor.get_execution_order()
except ValueError as e:
    print(f"Error: {e}")  # "Circular dependency detected in tasks"
```

### Concurrent Task Execution

```python
# Execute independent tasks in parallel via Tokio runtime
executor = AcceleratedTaskExecutor(use_rust=True)

# Get ready tasks and execute them concurrently
ready_tasks = executor.get_ready_tasks()
results = executor.execute_concurrent(ready_tasks)

# Get execution statistics
stats = executor.get_stats()
print(f"Tasks scheduled: {stats['tasks_scheduled']}")
print(f"Tasks completed: {stats['tasks_completed']}")
```

## Serialization Optimization

### serde-based Serialization (34x faster)

```python
from fast_crewai import AgentMessage

# Create messages with Rust acceleration
msg = AgentMessage(
    id="msg-001",
    sender="agent_1",
    recipient="agent_2",
    content="This is a test message with lots of content...",
    timestamp=1700000000,
    use_rust=True  # Use serde for 34x faster serialization
)

# Serialize (34x faster than json.dumps)
json_str = msg.to_json()

# Deserialize (14x faster than json.loads)
msg_restored = AgentMessage.from_json(json_str, use_rust=True)
```

### Batch Serialization

```python
from fast_crewai import AgentMessage
import time

# Benchmark: serde vs json
messages_data = [
    {"id": str(i), "sender": "agent", "recipient": "user", "content": f"Message {i}", "timestamp": i}
    for i in range(10000)
]

# With Rust (serde): ~80,000 ops/sec
start = time.time()
for data in messages_data:
    msg = AgentMessage(**data, use_rust=True)
    json_str = msg.to_json()
rust_time = time.time() - start
print(f"Rust: {len(messages_data)/rust_time:.0f} ops/sec")
```

## Database Operations

### FTS5 Full-Text Search (11x faster)

```python
from fast_crewai import AcceleratedSQLiteWrapper

# Configure with connection pooling
db = AcceleratedSQLiteWrapper(
    "database.db",
    pool_size=20,  # r2d2 connection pool
    use_rust=True
)

# Insert memories (triggers auto-update FTS5 index)
db.save_memory(
    task_description="Analyze machine learning model performance metrics",
    metadata={"agent": "analyst", "priority": 1},
    datetime="2024-01-01 10:00:00",
    score=0.95
)

# FTS5 search with BM25 ranking (11x faster than LIKE)
results = db.search_memories_fts("machine learning performance", limit=10)
for result in results:
    print(f"Match: {result['task_description'][:50]}... (rank: {result['rank']:.2f})")

# Get all memories
all_memories = db.get_all_memories(limit=100)
```

### Connection Pool Optimization

```python
from fast_crewai import AcceleratedSQLiteWrapper

# Configure connection pool for high concurrency
db = AcceleratedSQLiteWrapper(
    "database.db",
    pool_size=20,  # Adjust based on concurrency needs
    use_rust=True
)

# Batch operations for best performance
memories = [
    ("Analyze dataset A", {"agent": "analyst"}, "2024-01-01", 0.95),
    ("Process results B", {"agent": "processor"}, "2024-01-02", 0.89),
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
from fast_crewai import get_environment_info, is_acceleration_available
info = get_environment_info()
print(info)
print(f"Rust available: {is_acceleration_available()}")

# Verify Rust components are active
from fast_crewai import AcceleratedMemoryStorage
storage = AcceleratedMemoryStorage(use_rust=True)
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
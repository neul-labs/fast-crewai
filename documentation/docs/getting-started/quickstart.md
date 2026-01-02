# Quick Start

Get your CrewAI code running faster in just a few seconds.

## Basic Usage

Add a single import before your CrewAI imports to enable acceleration:

```python
# Add this line before importing CrewAI
import fast_crewai.shim

# Your existing CrewAI code remains unchanged
from crewai import Agent, Task, Crew

agent = Agent(
    role="Analyst",
    goal="Analyze data and provide insights",
    backstory="Expert data analyst with years of experience"
)

task = Task(
    description="Analyze the provided dataset",
    expected_output="A detailed analysis report",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True  # Memory operations are now accelerated!
)

result = crew.kickoff()
```

That's it! Your CrewAI code now benefits from Rust-powered acceleration.

## What Gets Accelerated

When you import `fast_crewai.shim`, these CrewAI components are automatically replaced with faster Rust implementations:

| Component | Acceleration |
|-----------|--------------|
| Memory storage | TF-IDF semantic search |
| Database operations | FTS5 full-text search, connection pooling |
| Tool execution | Result caching, fast JSON validation |
| Task execution | Dependency tracking, parallel scheduling |
| Serialization | serde-based JSON (34x faster) |

## Checking Acceleration Status

Verify that acceleration is active:

```python
import fast_crewai.shim
from fast_crewai import is_acceleration_available, get_acceleration_status

print(f"Rust available: {is_acceleration_available()}")

status = get_acceleration_status()
print(f"Components: {status}")
```

## Using Components Directly

You can also use accelerated components directly without the shim:

```python
from fast_crewai import (
    AcceleratedMemoryStorage,
    AcceleratedToolExecutor,
    AcceleratedTaskExecutor,
    AgentMessage
)

# High-performance memory with TF-IDF search
storage = AcceleratedMemoryStorage(use_rust=True)
storage.save("Important information about machine learning")
results = storage.search("machine learning", limit=5)

# Tool executor with caching (17x faster for repeated calls)
executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300,
    use_rust=True
)

# Fast serialization (34x faster)
message = AgentMessage(
    id="msg-001",
    sender="agent_1",
    recipient="agent_2",
    content="Hello!",
    timestamp=1700000000,
    use_rust=True
)
json_str = message.to_json()
```

## Running Tests

Verify everything works correctly:

```bash
# Run all tests
uv run pytest

# Run quick tests
./scripts/run_tests.sh fast

# Compare performance with and without acceleration
make test-comparison
```

## Example: Performance Comparison

```python
import time
import fast_crewai.shim
from fast_crewai import AcceleratedMemoryStorage, AgentMessage

# Benchmark memory operations
storage = AcceleratedMemoryStorage(use_rust=True)

start = time.time()
for i in range(1000):
    storage.save(f"Document {i} about machine learning and AI")
save_time = time.time() - start

start = time.time()
for i in range(100):
    results = storage.search("machine learning", limit=10)
search_time = time.time() - start

print(f"Save: {1000/save_time:.0f} docs/sec")
print(f"Search: {100/search_time:.0f} queries/sec")

# Benchmark serialization
start = time.time()
for i in range(10000):
    msg = AgentMessage(str(i), "sender", "recipient", f"content_{i}", i, use_rust=True)
    json_str = msg.to_json()
print(f"Serialization: {10000/(time.time()-start):.0f} msgs/sec")
```

## Next Steps

- [How It Works](how-it-works.md) - Understand the acceleration system
- [Configuration](../user-guide/configuration.md) - Fine-tune acceleration settings
- [Performance Tuning](../user-guide/performance.md) - Optimize for your workload

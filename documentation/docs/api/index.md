# API Reference

Complete API documentation for Fast-CrewAI accelerated components.

## Core Components

| Component | Description | Performance |
|-----------|-------------|-------------|
| [AcceleratedMemoryStorage](memory.md) | High-performance memory with TF-IDF search | Semantic search |
| [AcceleratedToolExecutor](tools.md) | Tool execution with caching | 17x faster |
| [AcceleratedTaskExecutor](tasks.md) | Task scheduling with dependency tracking | Parallel execution |
| [AcceleratedSQLiteWrapper](database.md) | SQLite with FTS5 and pooling | 11x faster search |
| [AgentMessage](serialization.md) | Fast JSON serialization | 34x faster |

## Utility Functions

| Function | Description |
|----------|-------------|
| [`is_acceleration_available()`](utilities.md#is_acceleration_available) | Check if Rust acceleration is available |
| [`get_acceleration_status()`](utilities.md#get_acceleration_status) | Get detailed status of all components |
| [`configure_accelerated_components()`](utilities.md#configure_accelerated_components) | Configure which components use Rust |
| [`get_performance_improvements()`](utilities.md#get_performance_improvements) | Get expected performance improvements |
| [`get_environment_info()`](utilities.md#get_environment_info) | Get current environment configuration |

## Shim Module

The shim module provides automatic CrewAI integration:

```python
import fast_crewai.shim  # Auto-enables acceleration

# Or control manually:
fast_crewai.shim.enable_acceleration(verbose=True)
fast_crewai.shim.disable_acceleration()
```

## Quick Example

```python
from fast_crewai import (
    AcceleratedMemoryStorage,
    AcceleratedToolExecutor,
    AcceleratedTaskExecutor,
    AcceleratedSQLiteWrapper,
    AgentMessage,
    is_acceleration_available
)

# Check availability
print(f"Rust acceleration: {is_acceleration_available()}")

# Memory storage
storage = AcceleratedMemoryStorage(use_rust=True)
storage.save("Important document about AI")
results = storage.search("AI", limit=5)

# Tool execution with caching
executor = AcceleratedToolExecutor(cache_ttl_seconds=300, use_rust=True)
result = executor.execute_tool("search", {"query": "test"})

# Task scheduling
task_executor = AcceleratedTaskExecutor(use_rust=True)
task_executor.register_task("task_a", [])
task_executor.register_task("task_b", ["task_a"])
order = task_executor.get_execution_order()

# Database with FTS5
db = AcceleratedSQLiteWrapper("db.db", pool_size=20, use_rust=True)
db.save_memory("Task description", {}, "2024-01-01", 0.95)
results = db.search_memories_fts("Task", limit=10)

# Fast serialization
msg = AgentMessage("id", "sender", "recipient", "content", 123, use_rust=True)
json_str = msg.to_json()
```

## Environment Variables

Control component behavior through environment variables:

```bash
# Global toggle
FAST_CREWAI_ACCELERATION=1    # Enable all
FAST_CREWAI_ACCELERATION=0    # Disable all

# Per-component control
FAST_CREWAI_MEMORY=true
FAST_CREWAI_TOOLS=true
FAST_CREWAI_TASKS=true
FAST_CREWAI_DATABASE=true
FAST_CREWAI_SERIALIZATION=true
```

## Error Handling

All components provide graceful fallback to Python implementations:

```python
storage = AcceleratedMemoryStorage(use_rust=True)

# Check what's being used
if storage.implementation == "rust":
    print("Using Rust acceleration")
else:
    print("Using Python fallback")
```

## Performance Summary

| Component | Improvement | Details |
|-----------|-------------|---------|
| Serialization | 34x faster | serde vs Python json |
| Tool Execution | 17x faster | Result caching |
| FTS5 Search | 11x faster | vs LIKE queries |
| Database Query | 1.3x faster | Connection pooling |

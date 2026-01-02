# Tool Acceleration

Fast-CrewAI provides **17x faster** tool execution through result caching and serde-based JSON validation.

## Overview

| Feature | Benefit |
|---------|---------|
| **Result Caching** | Skip repeated computations |
| **JSON Validation** | serde-based (much faster than Python json) |
| **Recursion Protection** | Configurable depth limits |
| **Execution Stats** | Track cache hits/misses |

## Basic Usage

```python
from fast_crewai import AcceleratedToolExecutor

executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300,  # Cache for 5 minutes
    use_rust=True
)

# Execute a tool
result = executor.execute_tool("search", {"query": "AI trends"})

# Second call with same args - instant cache hit!
result = executor.execute_tool("search", {"query": "AI trends"})
```

## With CrewAI

When using the shim, CrewAI tools are automatically accelerated:

```python
import fast_crewai.shim
from crewai import Agent, Task, Crew
from crewai.tools import tool

@tool("Search Tool")
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

agent = Agent(
    role="Researcher",
    goal="Find information",
    tools=[search],  # Accelerated automatically
    backstory="Expert researcher"
)
```

## Result Caching

The caching system dramatically speeds up repeated tool calls:

```python
executor = AcceleratedToolExecutor(
    cache_ttl_seconds=300,  # 5 minute cache
    use_rust=True
)

# First call: executes tool
result1 = executor.execute_tool("api_call", {"endpoint": "/users"})

# Second call: instant cache hit (17x faster!)
result2 = executor.execute_tool("api_call", {"endpoint": "/users"})

# Different args: cache miss, executes tool
result3 = executor.execute_tool("api_call", {"endpoint": "/posts"})
```

### Cache Control

```python
# Disable caching for specific calls
result = executor.execute_tool("tool", args, use_cache=False)

# Clear all cached results
cleared_count = executor.clear_cache()
print(f"Cleared {cleared_count} cached entries")
```

### Check Cache Statistics

```python
stats = executor.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Total executions: {stats['total_executions']}")
print(f"Hit rate: {stats['cache_hits'] / stats['total_executions'] * 100:.1f}%")
```

## JSON Validation

Fast validation using serde (much faster than Python's json module):

```python
# Validate single argument set
is_valid = executor.validate_args({
    "query": "test",
    "options": {"limit": 10, "offset": 0}
})

# Batch validation
args_list = [
    {"query": "test1"},
    {"query": "test2"},
    {"invalid": None}
]
results = executor.batch_validate(args_list)
# [True, True, False]
```

## Recursion Protection

Prevent stack overflow with configurable limits:

```python
executor = AcceleratedToolExecutor(
    max_recursion_depth=100,  # Lower for safety
    use_rust=True
)

# If recursion limit exceeded, raises exception
try:
    result = executor.execute_tool("recursive_tool", args)
except RuntimeError as e:
    print(f"Recursion limit hit: {e}")
```

## Performance Comparison

| Scenario | Python | Rust + Caching |
|----------|--------|----------------|
| First call | 1.5ms | 1.5ms |
| Cached call | 1.5ms | 0.09ms (17x faster) |
| JSON validation | 0.5ms | 0.03ms |

## Best Practices

### Optimal Cache TTL

Choose TTL based on data freshness requirements:

```python
# Real-time data: short TTL
executor = AcceleratedToolExecutor(cache_ttl_seconds=30)

# Static data: long TTL
executor = AcceleratedToolExecutor(cache_ttl_seconds=3600)

# No caching
executor = AcceleratedToolExecutor(cache_ttl_seconds=0)
```

### Batch Tool Execution

```python
tools_and_args = [
    ("search", {"query": "AI"}),
    ("analyze", {"data": "..."}),
    ("summarize", {"text": "..."})
]

results = []
for tool, args in tools_and_args:
    result = executor.execute_tool(tool, args)
    results.append(result)
```

### Monitor Cache Effectiveness

```python
import atexit

def print_cache_stats():
    stats = executor.get_stats()
    hit_rate = stats['cache_hits'] / max(stats['total_executions'], 1) * 100
    print(f"\nTool Cache Statistics:")
    print(f"  Hit rate: {hit_rate:.1f}%")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Cache misses: {stats['cache_misses']}")

atexit.register(print_cache_stats)
```

## Troubleshooting

### Low Cache Hit Rate

If cache hit rate is low:

1. Check if arguments are consistent (same structure/values)
2. Consider longer TTL if data doesn't change frequently
3. Ensure you're reusing the same executor instance

### Cache Not Working

Verify caching is enabled:

```python
# Check implementation
print(f"Using: {executor.implementation}")

# Verify cache is being used
stats = executor.get_stats()
print(f"Stats: {stats}")
```

### Memory Usage

Cache grows with unique argument combinations. Clear periodically if needed:

```python
# Clear cache when it grows too large
if executor.get_stats()['cache_misses'] > 10000:
    executor.clear_cache()
```

# AcceleratedToolExecutor

High-performance tool execution with result caching and JSON validation.

**Performance:** 17x faster than Python with caching enabled.

## Class Definition

```python
class AcceleratedToolExecutor:
    def __init__(
        self,
        max_recursion_depth: int = 1000,
        cache_ttl_seconds: int = 300,
        use_rust: Optional[bool] = None
    )
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_recursion_depth` | `int` | `1000` | Maximum recursion depth for stack safety |
| `cache_ttl_seconds` | `int` | `300` | Cache time-to-live in seconds |
| `use_rust` | `Optional[bool]` | `None` | Force Rust or Python implementation |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `implementation` | `str` | Returns `"rust"` or `"python"` |

## Methods

### execute_tool

Execute a tool with given arguments.

```python
def execute_tool(
    self,
    tool_name: str,
    args: Dict[str, Any],
    use_cache: bool = True
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tool_name` | `str` | - | Name of the tool to execute |
| `args` | `Dict[str, Any]` | - | Tool arguments |
| `use_cache` | `bool` | `True` | Whether to use cached results |

**Returns:** `str` - Tool execution result.

**Example:**

```python
executor = AcceleratedToolExecutor(cache_ttl_seconds=300, use_rust=True)

# First call - executes tool
result1 = executor.execute_tool("search", {"query": "AI trends"})

# Second call - cache hit (17x faster!)
result2 = executor.execute_tool("search", {"query": "AI trends"})

# Skip cache
result3 = executor.execute_tool("search", {"query": "AI trends"}, use_cache=False)
```

---

### validate_args

Validate tool arguments using serde-based JSON validation.

```python
def validate_args(self, args: Dict[str, Any]) -> bool
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `args` | `Dict[str, Any]` | Arguments to validate |

**Returns:** `bool` - `True` if valid, `False` otherwise.

**Example:**

```python
is_valid = executor.validate_args({
    "query": "test",
    "options": {"limit": 10}
})
print(f"Valid: {is_valid}")
```

---

### batch_validate

Batch validate multiple argument sets.

```python
def batch_validate(self, args_list: List[Dict[str, Any]]) -> List[bool]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `args_list` | `List[Dict]` | List of argument sets |

**Returns:** `List[bool]` - Validation results for each set.

**Example:**

```python
args_list = [
    {"query": "test1"},
    {"query": "test2"},
    {"invalid": None}
]
results = executor.batch_validate(args_list)
# [True, True, False]
```

---

### clear_cache

Clear all cached tool results.

```python
def clear_cache(self) -> int
```

**Returns:** `int` - Number of entries cleared.

**Example:**

```python
cleared = executor.clear_cache()
print(f"Cleared {cleared} cached entries")
```

---

### get_stats

Get execution statistics.

```python
def get_stats(self) -> Dict[str, Any]
```

**Returns:** `Dict[str, Any]` - Statistics dictionary.

| Key | Type | Description |
|-----|------|-------------|
| `cache_hits` | `int` | Number of cache hits |
| `cache_misses` | `int` | Number of cache misses |
| `total_executions` | `int` | Total tool executions |

**Example:**

```python
stats = executor.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Hit rate: {stats['cache_hits'] / stats['total_executions'] * 100:.1f}%")
```

## Complete Example

```python
from fast_crewai import AcceleratedToolExecutor

# Create executor with caching
executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300,
    use_rust=True
)

print(f"Using: {executor.implementation}")

# Execute tools
tools_and_args = [
    ("search", {"query": "machine learning"}),
    ("analyze", {"data": "sample data"}),
    ("search", {"query": "machine learning"}),  # Cache hit!
]

for tool, args in tools_and_args:
    result = executor.execute_tool(tool, args)
    print(f"{tool}: {result[:50]}...")

# Check statistics
stats = executor.get_stats()
print(f"\nStatistics:")
print(f"  Total executions: {stats['total_executions']}")
print(f"  Cache hits: {stats['cache_hits']}")
print(f"  Cache misses: {stats['cache_misses']}")

# Validate arguments
test_args = [
    {"query": "valid"},
    {"invalid_key": 123}
]
validations = executor.batch_validate(test_args)
print(f"\nValidations: {validations}")

# Clear cache
cleared = executor.clear_cache()
print(f"\nCleared {cleared} cached entries")
```

## Cache Behavior

### TTL Expiration

Cached results expire after `cache_ttl_seconds`:

```python
# Results cached for 5 minutes
executor = AcceleratedToolExecutor(cache_ttl_seconds=300)

# First call: cached
result1 = executor.execute_tool("tool", args)

# Within 5 minutes: cache hit
result2 = executor.execute_tool("tool", args)

# After 5 minutes: cache miss, re-executed
```

### Cache Keys

Cache keys are based on tool name + serialized arguments:

```python
# Different keys:
executor.execute_tool("search", {"query": "a"})  # Key: search|{"query":"a"}
executor.execute_tool("search", {"query": "b"})  # Key: search|{"query":"b"}

# Same key (cache hit):
executor.execute_tool("search", {"query": "a"})  # Cache hit!
```

## Recursion Protection

Prevents stack overflow in recursive tool calls:

```python
executor = AcceleratedToolExecutor(max_recursion_depth=100)

# If recursion exceeds limit:
try:
    result = executor.execute_tool("recursive_tool", args)
except RuntimeError as e:
    print(f"Recursion limit exceeded: {e}")
```

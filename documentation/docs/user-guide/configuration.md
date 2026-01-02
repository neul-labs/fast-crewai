# Configuration

Fast-CrewAI can be configured through environment variables or programmatically. All settings have sensible defaults that work well for most use cases.

## Environment Variables

### Global Control

```bash
# Enable all acceleration (default)
export FAST_CREWAI_ACCELERATION=1

# Disable all acceleration
export FAST_CREWAI_ACCELERATION=0
```

### Per-Component Control

Control individual acceleration components:

```bash
# Memory acceleration
export FAST_CREWAI_MEMORY=auto    # Auto-detect (default)
export FAST_CREWAI_MEMORY=true    # Force enable
export FAST_CREWAI_MEMORY=false   # Force disable

# Database acceleration
export FAST_CREWAI_DATABASE=auto
export FAST_CREWAI_DATABASE=true
export FAST_CREWAI_DATABASE=false

# Tool acceleration
export FAST_CREWAI_TOOLS=auto
export FAST_CREWAI_TOOLS=true
export FAST_CREWAI_TOOLS=false

# Task acceleration
export FAST_CREWAI_TASKS=auto
export FAST_CREWAI_TASKS=true
export FAST_CREWAI_TASKS=false

# Serialization acceleration
export FAST_CREWAI_SERIALIZATION=auto
export FAST_CREWAI_SERIALIZATION=true
export FAST_CREWAI_SERIALIZATION=false
```

Values: `true`, `false`, or `auto` (default - uses Rust if available)

## Programmatic Configuration

Configure Fast-CrewAI in your Python code:

```python
from fast_crewai import configure_accelerated_components

configure_accelerated_components(
    memory=True,
    database=True,
    tools=True,
    tasks=True,
    serialization=True
)
```

### Check Current Configuration

```python
from fast_crewai import get_environment_info

env_info = get_environment_info()
print(f"Memory acceleration: {env_info.get('FAST_CREWAI_MEMORY')}")
print(f"Database acceleration: {env_info.get('FAST_CREWAI_DATABASE')}")
print(f"Tool acceleration: {env_info.get('FAST_CREWAI_TOOLS')}")
```

## Component-Specific Configuration

### Memory Storage

```python
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage(
    use_rust=True  # Force Rust implementation
)
```

### Database

```python
from fast_crewai import AcceleratedSQLiteWrapper

db = AcceleratedSQLiteWrapper(
    db_path="database.db",
    pool_size=20,  # Connection pool size (default: 5)
    use_rust=True
)
```

### Tool Executor

```python
from fast_crewai import AcceleratedToolExecutor

executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,  # Stack safety limit (default: 1000)
    cache_ttl_seconds=300,      # Cache lifetime (default: 300)
    use_rust=True
)
```

## Configuration Strategies

### Development

Enable all acceleration with verbose output:

```python
import fast_crewai.shim

fast_crewai.shim.enable_acceleration(verbose=True)
```

```bash
export FAST_CREWAI_ACCELERATION=1
```

### Production

Use auto-detection for graceful fallback:

```bash
export FAST_CREWAI_ACCELERATION=auto
```

### Debugging

Disable acceleration to isolate issues:

```bash
export FAST_CREWAI_ACCELERATION=0
```

Or disable specific components:

```bash
export FAST_CREWAI_TOOLS=false
export FAST_CREWAI_MEMORY=true
```

## Workload-Based Configuration

### Memory-Heavy Workloads

```bash
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_DATABASE=true
```

### Tool-Intensive Workloads

```bash
export FAST_CREWAI_TOOLS=true
```

```python
# Configure longer cache TTL for repeated tool calls
executor = AcceleratedToolExecutor(cache_ttl_seconds=600)
```

### High-Concurrency Workloads

```python
# Increase connection pool size
db = AcceleratedSQLiteWrapper(db_path="db.db", pool_size=50)
```

## Verifying Configuration

### Check Acceleration Status

```python
from fast_crewai import is_acceleration_available, get_acceleration_status

print(f"Rust available: {is_acceleration_available()}")
print(f"Status: {get_acceleration_status()}")
```

### Check Component Implementation

```python
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage()
print(f"Implementation: {storage.implementation}")  # "rust" or "python"
```

## Troubleshooting Configuration

### Components Not Activating

1. Check environment variables:
    ```python
    from fast_crewai import get_environment_info
    print(get_environment_info())
    ```

2. Verify Rust availability:
    ```python
    from fast_crewai import is_acceleration_available
    print(f"Rust available: {is_acceleration_available()}")
    ```

3. Check for import errors:
    ```python
    try:
        from fast_crewai._core import RustMemoryStorage
        print("Rust core available")
    except ImportError as e:
        print(f"Rust core not available: {e}")
    ```

### Configuration Not Taking Effect

- Environment variables must be set **before** importing `fast_crewai`
- Programmatic configuration should be done **before** creating component instances

```python
import os
os.environ['FAST_CREWAI_MEMORY'] = 'true'  # Set before import

import fast_crewai.shim  # Now import
from crewai import Crew  # Acceleration active
```

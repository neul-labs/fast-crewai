# Configuration Guide

Learn how to configure Fast-CrewAI to optimize performance for your specific use case.

## Environment Variables

Fast-CrewAI uses environment variables for configuration. All variables are optional and have sensible defaults.

### Global Control

```bash
# Enable/disable all acceleration
FAST_CREWAI_ACCELERATION=1    # Enable (default: auto-detect)
FAST_CREWAI_ACCELERATION=0    # Disable completely
```

### Component Control

Control individual acceleration components:

```bash
# Memory acceleration
FAST_CREWAI_MEMORY=auto       # Auto-detect (default)
FAST_CREWAI_MEMORY=true       # Force enable
FAST_CREWAI_MEMORY=false      # Force disable

# Database acceleration  
FAST_CREWAI_DATABASE=auto     # Auto-detect (default)
FAST_CREWAI_DATABASE=true     # Force enable
FAST_CREWAI_DATABASE=false    # Force disable

# Tool acceleration
FAST_CREWAI_TOOLS=auto        # Auto-detect (default)
FAST_CREWAI_TOOLS=true        # Force enable
FAST_CREWAI_TOOLS=false       # Force disable

# Task acceleration
FAST_CREWAI_TASKS=auto        # Auto-detect (default)
FAST_CREWAI_TASKS=true        # Force enable
FAST_CREWAI_TASKS=false       # Force disable

# Serialization acceleration
FAST_CREWAI_SERIALIZATION=auto # Auto-detect (default)
FAST_CREWAI_SERIALIZATION=true # Force enable
FAST_CREWAI_SERIALIZATION=false # Force disable
```

### Performance Tuning

Fine-tune performance for specific workloads:

```bash
# Connection pool size for database operations (default: 5)
FAST_CREWAI_DATABASE_POOL_SIZE=10

# Maximum recursion depth for tools (default: 100)  
FAST_CREWAI_MAX_TOOL_RECURSION=50

# Memory storage optimization level
FAST_CREWAI_MEMORY_OPT_LEVEL=2  # 0=none, 1=basic, 2=aggressive (default)
```

## Programmatic Configuration

Configure Fast-CrewAI in your Python code:

```python
import fast_crewai.shim

# Configure which components use Rust acceleration
from fast_crewai import configure_accelerated_components

configure_accelerated_components(
    memory=True,
    database=True,
    tools=False,  # Disable tool acceleration
    tasks=True,
    serialization=True
)

# Check current configuration
from fast_crewai import get_environment_info
env_info = get_environment_info()
print(f"Memory acceleration: {env_info['FAST_CREWAI_MEMORY']}")
print(f"Database acceleration: {env_info['FAST_CREWAI_DATABASE']}")
```

## Memory Configuration

Memory acceleration can be configured for different use patterns:

```python
from fast_crewai.memory import AcceleratedMemoryStorage

# Custom memory storage with specific settings
memory_storage = AcceleratedMemoryStorage(
    use_rust=True  # Use Rust backend if available (TF-IDF search)
)
```

## Database Configuration

Database acceleration supports connection pooling:

```python
from fast_crewai.database import AcceleratedSQLiteWrapper

# Custom database wrapper with pooling
db_wrapper = AcceleratedSQLiteWrapper(
    db_path="my_database.db",
    pool_size=10,  # Connection pool size
    use_rust=True  # Use Rust backend if available
)
```

## Tool Configuration

Tool acceleration adds execution hooks:

```python
from fast_crewai.tools import AcceleratedToolExecutor

# Custom tool executor with caching (17x faster for repeated calls)
tool_executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300,  # Cache results for 5 minutes
    use_rust=True
)
```

## Testing Considerations

### API Key Handling

Fast-CrewAI test scripts intelligently handle API keys:

- If `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set, the tests use the real keys
- If no API keys are present, tests use fake keys to avoid costs
- Performance comparison tests work with both real and fake keys

## Best Practices

### Development vs Production

For development, consider more verbose configuration:

```bash
# Enable all components during development
FAST_CREWAI_ACCELERATION=1
FAST_CREWAI_MEMORY=true
FAST_CREWAI_DATABASE=true

# Disable in production if issues arise
FAST_CREWAI_ACCELERATION=auto  # Auto-detect and fallback gracefully
```

### Component Selection

Choose components based on your workload:

- **Memory heavy**: Enable `FAST_CREWAI_MEMORY=true`
- **Database heavy**: Enable `FAST_CREWAI_DATABASE=true`
- **Tool intensive**: Enable `FAST_CREWAI_TOOLS=true` (hooks available)
- **Task intensive**: Enable `FAST_CREWAI_TASKS=true` (hooks available)

### Performance Monitoring

Monitor configuration effectiveness:

```python
from fast_crewai import get_acceleration_status, is_acceleration_available

print(f"Rust available: {is_acceleration_available()}")
status = get_acceleration_status()
print("Active components:", [k for k, v in status.get('components', {}).items() if v])
```

## Troubleshooting Configuration

### Components Not Activating

If acceleration isn't working:

1. Check if environment variables are set correctly:
```python
from fast_crewai import get_environment_info
print(get_environment_info())
```

2. Verify Rust availability:
```python
from fast_crewai import is_acceleration_available
print("Rust available:", is_acceleration_available())
```

### Performance Degradation

If performance is worse with acceleration:

- Disable components individually to identify issues
- Use `FAST_CREWAI_ACCELERATION=0` as a baseline
- Consider increasing connection pool sizes for database-heavy workloads

### Compatibility Issues

If experiencing compatibility problems:

- Start with `FAST_CREWAI_ACCELERATION=auto` for safe fallbacks
- Disable specific components that cause issues
- Enable components one by one to identify the problematic component
# Utility Functions

Helper functions for checking status and configuring Fast-CrewAI.

## is_acceleration_available

Check if Rust acceleration is available.

```python
def is_acceleration_available() -> bool
```

**Returns:** `bool` - `True` if Rust implementation is loaded.

**Example:**

```python
from fast_crewai import is_acceleration_available

if is_acceleration_available():
    print("Rust acceleration is available!")
else:
    print("Using Python fallback")
```

---

## get_acceleration_status

Get detailed status of all components.

```python
def get_acceleration_status() -> Dict[str, Any]
```

**Returns:** `Dict[str, Any]` - Status dictionary with component availability.

**Example:**

```python
from fast_crewai import get_acceleration_status

status = get_acceleration_status()
print(f"Rust available: {status.get('rust_available')}")
print(f"Components: {status.get('components', {})}")
```

---

## configure_accelerated_components

Configure which components use Rust acceleration.

```python
def configure_accelerated_components(
    memory: bool = True,
    tools: bool = True,
    tasks: bool = True,
    serialization: bool = True,
    database: bool = True
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `memory` | `bool` | `True` | Enable memory acceleration |
| `tools` | `bool` | `True` | Enable tool acceleration |
| `tasks` | `bool` | `True` | Enable task acceleration |
| `serialization` | `bool` | `True` | Enable serialization acceleration |
| `database` | `bool` | `True` | Enable database acceleration |

**Example:**

```python
from fast_crewai import configure_accelerated_components

# Enable only memory and database
configure_accelerated_components(
    memory=True,
    tools=False,
    tasks=False,
    serialization=True,
    database=True
)
```

---

## get_performance_improvements

Get expected performance improvements by component.

```python
def get_performance_improvements() -> Dict[str, Dict[str, str]]
```

**Returns:** `Dict[str, Dict[str, str]]` - Performance data for each component.

**Example:**

```python
from fast_crewai import get_performance_improvements

improvements = get_performance_improvements()
for component, info in improvements.items():
    print(f"{component}: {info.get('improvement', 'N/A')}")
```

---

## get_environment_info

Get current environment configuration.

```python
def get_environment_info() -> Dict[str, Any]
```

**Returns:** `Dict[str, Any]` - Environment variable settings.

**Example:**

```python
from fast_crewai import get_environment_info

env_info = get_environment_info()
print(f"FAST_CREWAI_ACCELERATION: {env_info.get('FAST_CREWAI_ACCELERATION')}")
print(f"FAST_CREWAI_MEMORY: {env_info.get('FAST_CREWAI_MEMORY')}")
```

---

## Shim Functions

### enable_acceleration

Enable automatic component replacement via monkey patching.

```python
import fast_crewai.shim

result = fast_crewai.shim.enable_acceleration(verbose: bool = False) -> bool
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `verbose` | `bool` | `False` | Print what was patched |

**Returns:** `bool` - `True` if at least one component was patched.

**Example:**

```python
import fast_crewai.shim

# Enable with verbose output
success = fast_crewai.shim.enable_acceleration(verbose=True)
print(f"Acceleration enabled: {success}")
```

---

### disable_acceleration

Restore original CrewAI components.

```python
import fast_crewai.shim

result = fast_crewai.shim.disable_acceleration() -> bool
```

**Returns:** `bool` - `True` if restoration was successful.

**Example:**

```python
import fast_crewai.shim

# Disable acceleration
fast_crewai.shim.disable_acceleration()
```

## Complete Example

```python
from fast_crewai import (
    is_acceleration_available,
    get_acceleration_status,
    configure_accelerated_components,
    get_performance_improvements,
    get_environment_info
)

# Check availability
print("=== Availability ===")
print(f"Rust available: {is_acceleration_available()}")

# Get detailed status
print("\n=== Status ===")
status = get_acceleration_status()
for key, value in status.items():
    print(f"  {key}: {value}")

# Configure components
print("\n=== Configuration ===")
configure_accelerated_components(
    memory=True,
    tools=True,
    tasks=False,  # Disable task acceleration
    database=True
)

# Check environment
print("\n=== Environment ===")
env = get_environment_info()
for key, value in env.items():
    if key.startswith("FAST_CREWAI"):
        print(f"  {key}: {value}")

# Expected improvements
print("\n=== Expected Improvements ===")
improvements = get_performance_improvements()
for component, info in improvements.items():
    print(f"  {component}: {info}")
```

## Environment Variables Reference

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `FAST_CREWAI_ACCELERATION` | `0`, `1` | `1` | Global toggle |
| `FAST_CREWAI_MEMORY` | `true`, `false`, `auto` | `auto` | Memory acceleration |
| `FAST_CREWAI_TOOLS` | `true`, `false`, `auto` | `auto` | Tool acceleration |
| `FAST_CREWAI_TASKS` | `true`, `false`, `auto` | `auto` | Task acceleration |
| `FAST_CREWAI_DATABASE` | `true`, `false`, `auto` | `auto` | Database acceleration |
| `FAST_CREWAI_SERIALIZATION` | `true`, `false`, `auto` | `auto` | Serialization acceleration |

### Setting Environment Variables

**In shell:**
```bash
export FAST_CREWAI_ACCELERATION=1
export FAST_CREWAI_MEMORY=true
```

**In Python (before imports):**
```python
import os
os.environ['FAST_CREWAI_ACCELERATION'] = '1'
os.environ['FAST_CREWAI_MEMORY'] = 'true'

import fast_crewai.shim  # Now with configured settings
```

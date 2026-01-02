# Troubleshooting

Common issues and solutions for Fast-CrewAI.

## Installation Issues

### Rust Components Not Available

**Symptoms:**

- `ImportError: No module named '_core'`
- `RuntimeError: Rust implementation not available`
- Components fall back to Python implementation

**Solutions:**

1. **Rebuild from source:**
    ```bash
    uv sync --dev
    uv run maturin develop
    ```

2. **Check Rust installation:**
    ```bash
    rustc --version
    cargo --version
    ```

3. **Install Rust if missing:**
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source ~/.cargo/env
    ```

### Build Errors

**Windows:**
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Restart terminal and try again
uv sync --dev
uv run maturin develop
```

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install build-essential python3-dev

# Fedora
sudo dnf install gcc python3-devel
```

## Runtime Issues

### Performance Not Improved

**Check implementation:**
```python
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage()
print(f"Implementation: {storage.implementation}")

if storage.implementation != "rust":
    print("Using Python fallback - check Rust installation")
```

**Enable verbose logging:**
```python
import fast_crewai.shim
fast_crewai.shim.enable_acceleration(verbose=True)
```

### Memory Issues

**Large dataset handling:**
```python
storage = AcceleratedMemoryStorage()
batch_size = 1000

for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    for doc in batch:
        storage.save(doc)
```

**Memory usage monitoring:**
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Tool Execution Issues

**Recursion depth exceeded:**
```python
executor = AcceleratedToolExecutor(max_recursion_depth=10000)
```

**Tool execution errors:**
```python
try:
    result = executor.execute_tool("tool_name", args)
except Exception as e:
    print(f"Tool execution failed: {e}")
```

### Task Execution Issues

**Concurrent task failures:**
```python
try:
    executor = AcceleratedTaskExecutor()
    results = executor.execute_concurrent(tasks)
except Exception as e:
    print(f"Task execution failed: {e}")
```

## Configuration Issues

### Environment Variables Not Working

**Check environment:**
```python
from fast_crewai import get_environment_info
print(get_environment_info())
```

**Set variables correctly:**
```bash
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_TOOLS=true
export FAST_CREWAI_ACCELERATION=1
```

**Programmatic configuration:**
```python
from fast_crewai import configure_accelerated_components
configure_accelerated_components(memory=True, tools=True, tasks=False)
```

### Shimming Issues

**Automatic shimming not working:**
```python
import fast_crewai.shim
result = fast_crewai.shim.enable_acceleration(verbose=True)
print(f"Shimming enabled: {result}")
```

**Manual shimming:**
```python
# Import shim before other imports
import fast_crewai.shim
from crewai import Agent, Task, Crew
```

## Debugging

### Enable Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

import fast_crewai.shim
fast_crewai.shim.enable_acceleration(verbose=True)
```

### Check Component Status

```python
from fast_crewai import get_acceleration_status, is_acceleration_available

print(f"Rust available: {is_acceleration_available()}")
print(f"Status: {get_acceleration_status()}")
```

### Performance Debugging

```python
import time
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage()

start = time.time()
for i in range(100):
    storage.save(f"Test {i}")
save_time = time.time() - start
print(f"Save time: {save_time:.3f}s")

start = time.time()
for i in range(10):
    results = storage.search("Test", limit=5)
search_time = time.time() - start
print(f"Search time: {search_time:.3f}s")
```

## Common Error Messages

### "Failed to acquire lock"

- **Cause**: Threading issues or resource contention
- **Solution**: Check for deadlocks or excessive concurrency

### "Maximum recursion depth exceeded"

- **Cause**: Tool execution recursion limit reached
- **Solution**: Increase `max_recursion_depth` or refactor tool logic

### "Task execution failed"

- **Cause**: Async task execution error
- **Solution**: Check task implementation and error handling

### "Failed to serialize to JSON"

- **Cause**: Invalid data types in serialization
- **Solution**: Ensure all data is JSON-serializable

### "Failed to create connection pool"

- **Cause**: Database connection issues
- **Solution**: Check database path and permissions

## Performance Optimization

### Memory Optimization

```python
storage = AcceleratedMemoryStorage()
batch_size = 1000  # Adjust based on available memory

import psutil
def check_memory():
    return psutil.virtual_memory().percent
```

### Tool Optimization

```python
executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300  # Adjust cache lifetime
)
```

### Task Optimization

```python
executor = AcceleratedTaskExecutor()
# Keep reasonable batch sizes
tasks = ["task1", "task2", "task3"]
```

## Getting Help

### Report Issues

When reporting issues, include:

1. **Environment information:**
    ```python
    from fast_crewai import get_environment_info
    print(get_environment_info())
    ```

2. **Rust status:**
    ```python
    from fast_crewai import is_acceleration_available
    print(is_acceleration_available())
    ```

3. **Error traceback:**
    ```python
    import traceback
    try:
        # Your code here
        pass
    except Exception:
        traceback.print_exc()
    ```

4. **System information:**
    ```bash
    python --version
    rustc --version
    uv pip list | grep crew
    ```

### Community Resources

- **GitHub Issues**: [Report bugs](https://github.com/neul-labs/fast-crewai/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/neul-labs/fast-crewai/discussions)

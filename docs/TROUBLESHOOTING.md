# Troubleshooting Guide

Common issues and solutions for CrewAI Rust integration.

## Installation Issues

### Rust Components Not Available

**Symptoms:**
- `ImportError: No module named '_core'`
- `RuntimeError: Rust implementation not available`
- Components fall back to Python implementation

**Solutions:**

1. **Rebuild from source:**
```bash
pip uninstall crewai-rust
pip install maturin
maturin develop
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
pip install --upgrade setuptools wheel
pip install crewai-rust
```

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install
```

**Linux:**
```bash
# Install build dependencies
sudo apt update
sudo apt install build-essential python3-dev
```

## Runtime Issues

### Performance Not Improved

**Check implementation:**
```python
from fast_crewai import RustMemoryStorage
storage = RustMemoryStorage()
print(f"Implementation: {storage.implementation}")

if storage.implementation != "rust":
    print("⚠️ Using Python fallback - check Rust installation")
```

**Enable verbose logging:**
```python
import fast_crewai.shim
fast_crewai.shim.enable_rust_acceleration(verbose=True)
```

### Memory Issues

**Large dataset handling:**
```python
# For very large datasets, consider batching
storage = RustMemoryStorage()
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
# Increase recursion limit
executor = RustToolExecutor(max_recursion_depth=10000)
```

**Tool execution errors:**
```python
try:
    result = executor.execute_tool("tool_name", "args")
except Exception as e:
    print(f"Tool execution failed: {e}")
    # Handle error appropriately
```

### Task Execution Issues

**Concurrent task failures:**
```python
try:
    executor = RustTaskExecutor()
    results = executor.execute_concurrent_tasks(tasks)
except Exception as e:
    print(f"Task execution failed: {e}")
    # Fall back to sequential execution
```

**Thread pool issues:**
```python
# Check system resources
import os
print(f"CPU count: {os.cpu_count()}")
print(f"Thread limit: {threading.active_count()}")
```

## Configuration Issues

### Environment Variables Not Working

**Check environment:**
```python
from fast_crewai.utils import get_environment_info
print(get_environment_info())
```

**Set variables correctly:**
```bash
# Correct format
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_TOOLS=true
export FAST_CREWAI_ACCELERATION=1
```

**Programmatic configuration:**
```python
from fast_crewai.utils import configure_rust_components
configure_rust_components(memory=True, tools=True, tasks=False)
```

### Shimming Issues

**Automatic shimming not working:**
```python
# Check if shimming is enabled
import fast_crewai.shim
result = fast_crewai.shim.enable_rust_acceleration(verbose=True)
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

# Enable verbose Rust acceleration
import fast_crewai.shim
fast_crewai.shim.enable_rust_acceleration(verbose=True)
```

### Check Component Status

```python
from fast_crewai.utils import get_rust_status, is_rust_available

print(f"Rust available: {is_rust_available()}")
print(f"Status: {get_rust_status()}")
```

### Performance Debugging

```python
import time
from fast_crewai import RustMemoryStorage

# Time individual operations
storage = RustMemoryStorage()

# Test save performance
start = time.time()
for i in range(100):
    storage.save(f"Test {i}")
save_time = time.time() - start
print(f"Save time: {save_time:.3f}s")

# Test search performance
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
# Use appropriate batch sizes
storage = RustMemoryStorage()
batch_size = 1000  # Adjust based on available memory

# Monitor memory usage
import psutil
def check_memory():
    return psutil.virtual_memory().percent
```

### Tool Optimization

```python
# Set appropriate recursion limits
executor = RustToolExecutor(max_recursion_depth=1000)  # Adjust as needed

# Batch tool executions when possible
tools = ["tool1", "tool2", "tool3"]
for tool in tools:
    result = executor.execute_tool(tool, args)
```

### Task Optimization

```python
# Use appropriate task sizes
executor = RustTaskExecutor()
tasks = ["task1", "task2", "task3"]  # Keep reasonable batch sizes

# Monitor task execution
start = time.time()
results = executor.execute_concurrent_tasks(tasks)
execution_time = time.time() - start
print(f"Task execution time: {execution_time:.3f}s")
```

## Getting Help

### Check Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
# Check console output for detailed error messages
```

### Report Issues

When reporting issues, include:

1. **Environment information:**
```python
from fast_crewai.utils import get_environment_info
print(get_environment_info())
```

2. **Rust status:**
```python
from fast_crewai.utils import get_rust_status
print(get_rust_status())
```

3. **Error traceback:**
```python
import traceback
try:
    # Your code here
except Exception as e:
    traceback.print_exc()
```

4. **System information:**
```bash
python --version
rustc --version
pip list | grep crew
```

### Community Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/neul-labs/fast-crewai/issues)
- **GitHub Discussions**: [Ask questions and share solutions](https://github.com/neul-labs/fast-crewai/discussions)
- **Discord**: [CrewAI Community](https://discord.gg/crewai)

## Best Practices

### Error Handling

```python
from fast_crewai import RustMemoryStorage

try:
    storage = RustMemoryStorage()
    storage.save("data")
    results = storage.search("data")
except Exception as e:
    print(f"Error: {e}")
    # Implement fallback logic
```

### Resource Management

```python
# Use context managers when available
with RustSQLiteWrapper("db.db", pool_size=10) as db:
    results = db.execute_query("SELECT * FROM table", {})
```

### Performance Monitoring

```python
import time
from fast_crewai import RustMemoryStorage

def benchmark_operation():
    storage = RustMemoryStorage()
    
    # Benchmark save
    start = time.time()
    for i in range(1000):
        storage.save(f"Document {i}")
    save_time = time.time() - start
    
    # Benchmark search
    start = time.time()
    for i in range(100):
        results = storage.search("Document", limit=10)
    search_time = time.time() - start
    
    print(f"Save: {1000/save_time:.1f} ops/sec")
    print(f"Search: {100/search_time:.1f} ops/sec")
```

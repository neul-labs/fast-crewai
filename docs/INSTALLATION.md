# Installation Guide

Comprehensive installation instructions for CrewAI Accelerate.

## Standard Installation

### Via pip (Recommended)

```bash
pip install fast-crewai
```

### Via pip with extras

```bash
# Include development dependencies
pip install fast-crewai[dev]
```

## Development Installation

### Prerequisites

- Python 3.8+
- Rust 1.70+ (for building from source)
- Git

### Install Rust

```bash
# Install Rust via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

### Clone and Build

```bash
# Clone the repository
git clone https://github.com/neul-labs/fast-crewai.git
cd crewai-rust

# Install maturin (Rust-Python bridge)
pip install maturin

# Development build
maturin develop

# Or build release wheels
maturin build --release
```

## Platform-Specific Instructions

### Linux

```bash
# Ubuntu/Debian - install build dependencies
sudo apt update
sudo apt install build-essential python3-dev

# Then proceed with standard installation
pip install crewai-rust
```

### macOS

```bash
# Install Xcode command line tools
xcode-select --install

# Then proceed with standard installation
pip install crewai-rust
```

### Windows

```bash
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then proceed with standard installation
pip install crewai-rust
```

## Verification

### Test Installation

```python
# Test basic import
try:
    import fast_crewai
    print("CrewAI Accelerate installed successfully")
    print(f"Version: {fast_crewai.__version__}")
except ImportError as e:
    print(f"Installation failed: {e}")
```

### Test Rust Components

```python
# Test acceleration
from fast_crewai import is_acceleration_available, get_acceleration_status

if is_acceleration_available():
    print("✅ Acceleration available")
    print(f"Status: {get_acceleration_status()}")

    # Test memory component
    from fast_crewai import AcceleratedMemoryStorage
    memory = AcceleratedMemoryStorage()
    print(f"Memory implementation: {memory.implementation}")
    
    # Test basic functionality
    memory.save("Test data")
    results = memory.search("Test", limit=5)
    print(f"Search results: {results}")
else:
    print("❌ Acceleration not available")
    print("This is normal if accelerated components are not built or installed")
```

### Run Test Suite

```bash
# Run basic tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_memory.py -v
python -m pytest tests/test_tools.py -v

# Run Rust tests (if Rust is installed)
cargo test
```

### Quick Functionality Test

```python
# Test all components quickly
from fast_crewai import (
    AcceleratedMemoryStorage, 
    AcceleratedToolExecutor, 
    AcceleratedTaskExecutor,
    AcceleratedMessage,
    AcceleratedSQLiteWrapper
)

# Test memory
memory = AcceleratedMemoryStorage()
memory.save("Hello World")
results = memory.search("Hello", limit=1)
print(f"Memory test: {len(results)} results")

# Test tool executor
tool_exec = AcceleratedToolExecutor(max_recursion_depth=100)
result = tool_exec.execute_tool("test", "args")
print(f"Tool test: {result}")

# Test task executor
task_exec = AcceleratedTaskExecutor()
tasks = ["task1", "task2"]
results = task_exec.execute_concurrent_tasks(tasks)
print(f"Task test: {len(results)} completed")

# Test serialization
msg = AcceleratedMessage("1", "sender", "recipient", "content", 1234567890)
json_str = msg.to_json()
print(f"Serialization test: {len(json_str)} chars")

print("✅ All components working!")
```

## Environment Configuration

### Environment Variables

```bash
# Enable automatic acceleration
export FAST_CREWAI_ACCELERATION=1

# Force specific component usage
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_TOOLS=true
export FAST_CREWAI_TASKS=true

# Disable specific components
export FAST_CREWAI_MEMORY=false
```

### Configuration File

Create `~/.fast-crewai/config.toml`:

```toml
[acceleration]
auto_enable = true
verbose_logging = false

[memory]
use_rust = true
fallback_on_error = true

[tools]
use_rust = true
max_recursion_depth = 1000

[tasks]
use_rust = true
thread_pool_size = 4
```

## Troubleshooting

### Common Issues

**1. Import Error: "No module named '_core'"**

```bash
# Accelerated extension not built properly
pip uninstall fast-crewai
pip install --no-cache-dir fast-crewai

# If still failing, build from source
pip install maturin
maturin develop
```

**2. Performance Issues**

```python
# Check implementation being used
from fast_crewai import AcceleratedMemoryStorage
storage = AcceleratedMemoryStorage()
print(f"Implementation: {storage.implementation}")

# Should show "accelerated", not "python"
if storage.implementation != "accelerated":
    print("⚠️ Using Python fallback - check acceleration installation")
```

**3. Build Errors on Windows**

```bash
# Install Visual C++ Build Tools
# Restart terminal and try again
pip install --upgrade setuptools wheel
pip install fast-crewai
```

**4. Version Conflicts**

```bash
# Check CrewAI compatibility
pip list | grep crew
# Ensure crewai >= 0.28.0
pip install --upgrade crewai

# Check Python version
python --version
# Ensure Python >= 3.8
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose acceleration
import fast_crewai.shim
fast_crewai.shim.enable_acceleration(verbose=True)

# Check detailed status
from fast_crewai.utils import get_acceleration_status, get_environment_info
print("Acceleration status:", get_acceleration_status())
print("Environment:", get_environment_info())
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/neul-labs/fast-crewai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neul-labs/fast-crewai/discussions)
- **Discord**: [CrewAI Community](https://discord.gg/crewai)

## Next Steps

- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Configuration](../README.md#configuration)** - Customize settings
- **[Performance](PERFORMANCE.md)** - Benchmark your setup
# Installation Guide

Comprehensive installation instructions for CrewAI Rust.

## Standard Installation

### Via pip (Recommended)

```bash
pip install crewai-rust
```

### Via pip with extras

```bash
# Include development dependencies
pip install crewai-rust[dev]
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
git clone https://github.com/crewAI/crewai-rust.git
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
    import crewai_rust
    print("CrewAI Rust installed successfully")
    print(f"Version: {crewai_rust.__version__}")
except ImportError as e:
    print(f"Installation failed: {e}")
```

### Test Rust Components

```python
# Test Rust acceleration
from crewai_rust import is_rust_available, get_rust_status

if is_rust_available():
    print("Rust acceleration available")
    print(f"Status: {get_rust_status()}")

    # Test memory component
    from crewai_rust import RustMemoryStorage
    memory = RustMemoryStorage()
    print(f"Memory implementation: {memory.implementation}")
else:
    print("Rust acceleration not available")
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
```

## Environment Configuration

### Environment Variables

```bash
# Enable automatic acceleration
export CREWAI_RUST_ACCELERATION=1

# Force specific component usage
export CREWAI_RUST_MEMORY=true
export CREWAI_RUST_TOOLS=true
export CREWAI_RUST_TASKS=true

# Disable specific components
export CREWAI_RUST_MEMORY=false
```

### Configuration File

Create `~/.crewai-rust/config.toml`:

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
# Rust extension not built properly
pip uninstall crewai-rust
pip install --no-cache-dir crewai-rust
```

**2. Performance Issues**

```python
# Check implementation being used
from crewai_rust import RustMemoryStorage
storage = RustMemoryStorage()
print(f"Implementation: {storage.implementation}")

# Should show "rust", not "python"
```

**3. Build Errors on Windows**

```bash
# Install Visual C++ Build Tools
# Restart terminal and try again
pip install --upgrade setuptools wheel
pip install crewai-rust
```

**4. Version Conflicts**

```bash
# Check CrewAI compatibility
pip list | grep crew
# Ensure crewai >= 0.28.0
pip install --upgrade crewai
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

import crewai_rust.shim
crewai_rust.shim.enable_rust_acceleration(verbose=True)
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/crewAI/crewai-rust/issues)
- **Discussions**: [GitHub Discussions](https://github.com/crewAI/crewai-rust/discussions)
- **Discord**: [CrewAI Community](https://discord.gg/crewai)

## Next Steps

- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Configuration](../README.md#configuration)** - Customize settings
- **[Performance](PERFORMANCE.md)** - Benchmark your setup
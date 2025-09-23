# CrewAI Rust

High-performance Rust acceleration for CrewAI workflows

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://www.rust-lang.org/)

CrewAI Rust provides drop-in Rust implementations for performance-critical CrewAI components, delivering significant speed improvements while maintaining 100% API compatibility.

## Performance Improvements

| Component | Performance Gain | Key Optimization |
|-----------|------------------|------------------|
| **Memory Storage** | 10-20x faster | SIMD-accelerated vector operations |
| **Tool Execution** | 2-5x faster | Zero-cost error handling & stack safety |
| **Task Execution** | 3-5x faster | True async concurrency with work-stealing |
| **Serialization** | 5-10x faster | Zero-copy operations |
| **Database Operations** | 3-5x faster | Connection pooling & prepared statements |

## Installation

```bash
pip install crewai-rust
```

## Quick Start

### Zero-Code Integration (Recommended)

Accelerate existing CrewAI projects without any code changes:

```python
import crewai
import crewai_rust.shim  # Automatically enables Rust acceleration

from crewai import Agent, Task, Crew
# Your existing CrewAI code works unchanged
```

**Alternative activation methods:**
```bash
# Environment variable
export CREWAI_RUST_ACCELERATION=1
python your_script.py

# Command line
crewai-rust-bootstrap && python your_script.py
```

### Explicit Component Usage

For fine-grained control over which components use Rust:

```python
from crewai_rust import RustMemoryStorage, RustToolExecutor

# Explicit Rust usage
memory = RustMemoryStorage()
memory.save("Important data", {"priority": "high"})
results = memory.search("data")

# Mixed usage - Rust where it matters most
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory_storage=RustMemoryStorage(),  # Rust acceleration
    # Other components use standard Python
)
```

## Configuration

### Memory Storage Configuration

```python
# Environment-based control
import os
os.environ['CREWAI_RUST_MEMORY'] = 'true'  # Force Rust
os.environ['CREWAI_RUST_MEMORY'] = 'false' # Force Python
os.environ['CREWAI_RUST_MEMORY'] = 'auto'  # Auto-detect (default)

# Programmatic control
from crewai_rust import RustMemoryStorage
storage = RustMemoryStorage(use_rust=True)
```

### Tool Execution Limits

```python
from crewai_rust import RustToolExecutor

# Configure recursion safety
executor = RustToolExecutor(max_recursion_depth=1000)
result = executor.execute_tool("my_tool", {"param": "value"})
```

## Architecture

CrewAI Rust works through intelligent monkey patching:

```python
# Before: Standard CrewAI
from crewai.memory import RAGStorage          # Python implementation
from crewai.tools import CrewStructuredTool   # Python implementation

# After: crewai_rust.shim import
from crewai.memory import RAGStorage          # ➜ RustMemoryStorage
from crewai.tools import CrewStructuredTool   # ➜ RustToolExecutor
```

**Replaced Components:**
- `RAGStorage` → `RustMemoryStorage`
- `ShortTermMemory` → `RustMemoryStorage`
- `LongTermMemory` → `RustMemoryStorage`
- `CrewStructuredTool` → `RustToolExecutor`
- `Task` → `RustTaskExecutor`
- `LTMSQLiteStorage` → `RustSQLiteWrapper`

## Benchmarks

Run performance comparisons:

```python
from crewai_rust.benchmark import run_benchmarks

# Compare Python vs Rust implementations
results = run_benchmarks()
print(f"Memory operations: {results['memory_speedup']:.1f}x faster")
print(f"Tool execution: {results['tool_speedup']:.1f}x faster")
```

## Reliability

- **Automatic Fallback**: Falls back to Python implementations if Rust is unavailable
- **Zero Breaking Changes**: 100% API compatibility with existing CrewAI code
- **Production Ready**: Comprehensive error handling and logging
- **Memory Safe**: All Rust code is memory-safe by design

## Debugging

Check acceleration status:

```python
from crewai_rust import get_rust_status, is_rust_available

print(f"Rust available: {is_rust_available()}")
print(f"Status: {get_rust_status()}")

# Enable detailed logging
import crewai_rust.shim
crewai_rust.shim.enable_rust_acceleration(verbose=True)
```

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Performance Guide](docs/PERFORMANCE.md)** - Benchmarks and optimization tips
- **[Migration Guide](docs/MIGRATION.md)** - Migrating from standard CrewAI
- **[API Reference](docs/COMPATIBILITY.md)** - Complete API compatibility reference
- **[Architecture](docs/ARCHITECTURE.md)** - Technical implementation details

## Contributing

We welcome contributions! See our [Development Guide](docs/DEVELOPMENT.md) for:

- Building from source
- Running tests
- Development setup
- Contributing guidelines

## Testing

```bash
# Run all tests
python -m pytest

# Run fast tests only
./scripts/run_tests.sh fast

# Run with coverage
./scripts/run_tests.sh coverage
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/crewAI/crewai-rust/issues)
- **Discussions**: [GitHub Discussions](https://github.com/crewAI/crewai-rust/discussions)
- **Discord**: [CrewAI Community](https://discord.gg/crewai)
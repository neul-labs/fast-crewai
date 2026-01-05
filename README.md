# Fast-CrewAI

**Drop-in performance acceleration for CrewAI** - Get up to **34x faster serialization**, **17x faster tool execution**, and **11x faster database search** with zero code changes to your existing CrewAI projects.

[![CI](https://github.com/neul-labs/fast-crewai/workflows/CI/badge.svg)](https://github.com/neul-labs/fast-crewai/actions)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/rust-stable-orange.svg)](https://www.rust-lang.org/)

Fast-CrewAI is authored by [Dipankar Sarkar](mailto:me@dipankar.name) and maintained by [Neul Labs](https://github.com/neul-labs) to bring production-ready acceleration to CrewAI workloads.

## 🚀 Quick Start

Get your CrewAI code running faster in seconds:

```bash
# Install the acceleration layer (using uv - recommended)
uv add fast-crewai

# Or with pip
pip install fast-crewai

# Add one line to your existing CrewAI code
import fast_crewai.shim  # Add this before importing CrewAI
from crewai import Agent, Task, Crew  # Your existing code remains unchanged!
```

That's it! Your existing CrewAI code now benefits from Rust-powered acceleration.

## 🏎️ What Gets Faster

| Component | Performance Boost | What This Means |
|-----------|-------------------|-----------------|
| **Serialization** | 🚀 **34x faster** | Agent message serialization using serde |
| **Tool Execution** | 🚀 **17x faster** | Result caching and JSON validation |
| **Database Search** | 🚀 **11x faster** | FTS5 full-text search with BM25 ranking |
| **Memory Storage** | ✅ **TF-IDF search** | Semantic search using cosine similarity |
| **Task Execution** | ✅ **Dependency tracking** | Topological sort and parallel scheduling |

See [BENCHMARK.md](BENCHMARK.md) for detailed performance data.

## 🤝 How It Works

Fast-CrewAI uses **smart monkey patching** that seamlessly integrates with your existing CrewAI code:

```python
# Your existing CrewAI code - no changes needed!
from crewai import Agent, Task, Crew  # This automatically gets accelerated!

# Just add this line once at the top of your main file
import fast_crewai.shim  # Activates acceleration for all CrewAI components
```

The acceleration happens automatically through **dynamic inheritance** - your tools, tasks, and other components get wrapped with performance improvements while keeping 100% API compatibility.

## 📦 Installation

### Get Started Quickly
```bash
# Using uv (recommended)
uv add fast-crewai

# Or with pip
pip install fast-crewai
```

### For Development
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/neul-labs/fast-crewai.git
cd fast-crewai
uv sync --dev

# Build Rust extensions for maximum performance
uv run maturin develop --release
```

## 🧪 Testing & Verification

Verify Fast-CrewAI is working with these tests:

```bash
# Run all unit tests
make test

# Compare performance (with/without acceleration) - runs full CrewAI workflows
make test-comparison

# Run extensive performance tests (1000 iterations)
make test-comparison-extensive

# Full compatibility check with CrewAI
make test-compatibility

# Run internal benchmarks
make benchmark
```

The `test-comparison` command runs complete CrewAI workflows that engage all acceleration components:

- **Memory acceleration**: Through CrewAI's memory systems (RAG storage, short/long-term memory)
- **Database acceleration**: Through SQLite operations for memory persistence
- **Tool execution**: Through any tools used in the workflow (hooks enabled)
- **Task execution**: Through CrewAI's task processing system (hooks enabled)

For example, on basic workflows the comparison typically shows around 13% performance improvement:

```
==================================================
Workflow Type: basic
Iterations: 3
Baseline (without Fast-CrewAI): 27.88s
Accelerated (with Fast-CrewAI): 24.50s
Time Saved: 3.38s
Performance Improvement: 1.13x faster
Percent Improvement: 13.00%
==================================================
```

Higher improvements (2-5x) are typically seen with memory-intensive and database-heavy workflows where Fast-CrewAI's Rust acceleration provides greater benefits.

## ⚙️ Configuration

Fine-tune your acceleration with environment variables:

```bash
# Enable all acceleration (default)
export FAST_CREWAI_ACCELERATION=1

# Disable acceleration (for debugging)
export FAST_CREWAI_ACCELERATION=0

# Control specific components
export FAST_CREWAI_MEMORY=true    # Memory acceleration
export FAST_CREWAI_TOOLS=false    # Tool acceleration
export FAST_CREWAI_DATABASE=true  # Database acceleration
```

## 📊 Performance Benchmarks

Latest benchmark results (see [BENCHMARK.md](BENCHMARK.md) for full details):

### Performance Improvements

| Component | Improvement | Details |
|-----------|-------------|---------|
| **Serialization** | 🚀 **34.5x faster** | 80,525 ops/s (Rust) vs 2,333 ops/s (Python) |
| **Tool Execution** | 🚀 **17.3x faster** | Result caching with configurable TTL |
| **FTS Database Search** | 🚀 **11.2x faster** | 10,206 ops/s (FTS5) vs 913 ops/s (LIKE) |
| **Database Query** | 🚀 **1.3x faster** | Connection pooling with r2d2 |
| **Memory Storage** | ✅ **Comparable** | TF-IDF semantic search |

### Memory Usage

| Component | Python | Rust | Savings |
|-----------|--------|------|---------|
| Tool Execution | 1.2 MB | 0.0 MB | **99% less** |
| Serialization | 8.0 MB | 3.4 MB | **58% less** |
| Database | 0.1 MB | 0.1 MB | **31% less** |

### Key Features by Component

**Database (FTS5)**
- Full-text search with BM25 relevance ranking
- Automatic index synchronization via triggers
- Connection pooling for concurrent access

**Tool Executor**
- Result caching with TTL expiration
- Fast JSON validation using serde
- Execution statistics tracking

**Task Executor**
- Dependency tracking with topological sort
- Cycle detection for circular dependencies
- Parallel task scheduling via Tokio

**Serialization**
- serde-based JSON serialization (34x faster)
- Lower memory footprint (58% less)

## 🛠️ Development & Testing

The project includes comprehensive tools for development and performance analysis:

```bash
# Run all tests
make test

# Run performance comparisons
make test-comparison                 # Quick comparison
make test-comparison-extensive      # 1000 iterations for detailed analysis

# Run compatibility tests
make test-compatibility             # Verify with latest CrewAI

# Run internal benchmarks
make benchmark                      # Test components in isolation
```

## 📚 Learn More

- **[Architecture](docs/ARCHITECTURE.md)**: How the acceleration system works under the hood
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Configuration](docs/CONFIGURATION.md)**: Fine-tuning Fast-CrewAI for your needs
- **[Performance](docs/PERFORMANCE.md)**: Detailed benchmarking and optimization
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions

For complete documentation, visit the [docs/](docs/) directory.

## 📋 Requirements & Compatibility

### Python Version Support

| Python Version | Status | Notes |
|----------------|--------|-------|
| Python 3.10 | ✅ Supported | Fully tested |
| Python 3.11 | ✅ Supported | Fully tested |
| Python 3.12 | ✅ Supported | Fully tested |
| Python 3.13 | ✅ Supported | Fully tested |
| Python 3.9 | ⚠️ Limited | May work but not tested in CI |

### Dependencies

- **CrewAI**: Any recent version supported
- **Rust toolchain**: Optional, for native extensions (provides maximum performance)
  - PyO3 0.23+ is used for Python-Rust bindings
  - Falls back to pure Python if Rust extensions aren't available

### Platform Support

| Platform | Status |
|----------|--------|
| Linux (x86_64) | ✅ Fully supported |
| macOS (x86_64) | ✅ Fully supported |
| macOS (ARM64/M1) | ✅ Fully supported |
| Windows (x86_64) | ✅ Supported |

## 🤝 Contributing

Contributions are welcome! Check out our development guide for setup instructions and coding standards.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Maintainers

- **Author**: Dipankar Sarkar (<me@dipankar.name>)
- **Organization**: Neul Labs

## 🔧 Support

- **Issues**: [GitHub Issues](https://github.com/neul-labs/fast-crewai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neul-labs/fast-crewai/discussions)

Fast-CrewAI is in **active development**. Memory and database acceleration are production-ready, with ongoing optimization for tools and tasks.

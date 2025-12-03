# Fast-CrewAI

**Drop-in performance acceleration for CrewAI** - Get 2-5x faster memory, database, and execution with zero code changes to your existing CrewAI projects.

[![CI](https://github.com/neul-labs/fast-crewai/workflows/CI/badge.svg)](https://github.com/neul-labs/fast-crewai/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

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

That's it! Your existing CrewAI code now runs **2-5x faster** with no other changes needed.

## 🏎️ What Gets Faster

| Component | Performance Boost | What This Means |
|-----------|-------------------|-----------------|
| **Memory Storage** | 2-5x faster | RAG storage, short/long-term memory operations |
| **Database Operations** | 2-4x faster | SQLite operations for memory and persistence |
| **Tool Execution** | Hooks ready | Acceleration points for future optimization |
| **Task Execution** | Hooks ready | Acceleration points for future optimization |

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

## 📊 Real-World Performance

Performance improvements vary by workload type:

### Component-Specific Benchmarks (Internal Testing)
These benchmarks test Fast-CrewAI components in isolation:

| Component | Baseline | With Fast-CrewAI | Improvement |
|-----------|----------|------------------|-------------|
| Memory Operations | 1.00s | 0.35s | **2.9x faster** |
| Database Operations | 1.00s | 0.41s | **2.4x faster** |
| Overall Workflow | 1.00s | 0.54s | **1.9x faster** |

*These are internal component benchmarks testing Rust vs Python implementations*

### Actual Workflow Testing
When running complete CrewAI workflows with `make test-comparison`, performance varies by workflow type:

- **Basic workflows**: Modest improvements (10-15% in the example below)
- **Memory-intensive workflows**: Higher improvements (2-5x) due to accelerated storage
- **Database-heavy workflows**: Higher improvements (2-4x) due to connection pooling

Example of basic workflow comparison:
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

## 📋 Requirements

- Python 3.9 or higher
- CrewAI (any version supported)
- Optional: Rust toolchain for native extensions (for maximum performance)

## 🤝 Contributing

Contributions are welcome! Check out our development guide for setup instructions and coding standards.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔧 Support

- **Issues**: [GitHub Issues](https://github.com/neul-labs/fast-crewai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neul-labs/fast-crewai/discussions)

Fast-CrewAI is in **active development**. Memory and database acceleration are production-ready, with ongoing optimization for tools and tasks.

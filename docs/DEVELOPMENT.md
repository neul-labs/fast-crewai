# Development Guide

Contributing to CrewAI Rust - setup, building, testing, and contribution guidelines.

## Development Setup

### Prerequisites

- **Python 3.8+**
- **Rust 1.70+**
- **Git**
- **C++ Build Tools** (platform-specific)

### Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/neul-labs/fast-crewai.git
cd crewai-rust

# 2. Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 3. Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install development dependencies
pip install -r requirements-dev.txt
pip install maturin

# 5. Build the project in development mode
maturin develop

# 6. Verify installation
python -c "import fast_crewai; print('Development setup complete')"
```

### IDE Setup

#### VS Code

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "rust-analyzer.cargo.features": ["extension-module"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm

1. Set Python interpreter to `./venv/bin/python`
2. Install Rust plugin
3. Configure pytest as test runner

## Project Structure

```
fast-crewai/
├── src/                    # Rust source code
│   └── lib.rs             # Main Rust library
├── fast_crewai/           # Python package
│   ├── __init__.py        # Package initialization
│   ├── shim.py            # Monkey patching system
│   ├── memory.py          # Python memory wrapper
│   ├── tools.py           # Python tool wrapper
│   ├── tasks.py           # Python task wrapper
│   ├── serialization.py   # Serialization utilities
│   ├── database.py        # Database wrappers
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
│   ├── test_memory.py     # Memory tests
│   ├── test_tools.py      # Tool tests
│   ├── test_tasks.py      # Task tests
│   └── test_integration.py # Integration tests
├── test_integration.py    # Standalone integration example
├── test_all_patches.py    # Patch validation test
├── docs/                  # Documentation
├── scripts/               # Build and test scripts
├── Cargo.toml            # Rust dependencies
├── pyproject.toml        # Python project config
└── README.md
```

## Building

### Development Builds

```bash
# Fast development build (debug symbols, no optimizations)
maturin develop

# With specific Python version
maturin develop --python python3.10

# Force rebuild
maturin develop --force
```

### Release Builds

```bash
# Optimized release build
maturin build --release

# Cross-platform builds
maturin build --release --target x86_64-pc-windows-msvc
maturin build --release --target x86_64-apple-darwin
maturin build --release --target aarch64-apple-darwin
```

### Build Profiles

**Debug Profile** (`Cargo.toml`):
```toml
[profile.dev]
opt-level = 0
debug = true
debug-assertions = true
```

**Release Profile**:
```toml
[profile.release]
opt-level = 3
lto = true
panic = 'abort'
codegen-units = 1
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_memory.py

# Run with coverage
python -m pytest --cov=fast_crewai

# Run Rust tests
cargo test
```

### Test Categories

#### Unit Tests

**Python Unit Tests** (`tests/test_memory.py`):
```python
import pytest
from fast_crewai import RustMemoryStorage

def test_memory_save_and_search():
    storage = RustMemoryStorage()
    storage.save("test data", {"key": "value"})
    results = storage.search("test")
    assert len(results) > 0
    assert "test data" in [r['value'] for r in results]
```

**Rust Unit Tests** (`src/lib.rs`):
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memory_storage() {
        let storage = RustMemoryStorage::new();
        storage.save("test").unwrap();
        let results = storage.search("test").unwrap();
        assert!(!results.is_empty());
    }
}
```

#### Integration Tests

**CrewAI Integration** (`tests/test_integration.py`):
```python
def test_crewai_integration():
    import fast_crewai.shim
    from crewai import Agent, Task, Crew

    agent = Agent(role="Tester", goal="Test", backstory="Testing")
    task = Task(description="Test task", expected_output="Result", agent=agent)
    crew = Crew(agents=[agent], tasks=[task])

    result = crew.kickoff()
    assert result is not None
```

#### Performance Tests

**Benchmark Tests** (`tests/test_performance.py`):
```python
import time
import pytest
from fast_crewai import RustMemoryStorage

@pytest.mark.performance
def test_memory_performance():
    storage = RustMemoryStorage()

    # Large dataset
    documents = [f"Document {i}" for i in range(1000)]

    # Benchmark save operations
    start = time.time()
    for doc in documents:
        storage.save(doc)
    save_time = time.time() - start

    # Should be significantly faster than Python implementation
    assert save_time < 1.0  # Adjust based on expected performance
```

#### Compatibility Tests

**API Compatibility** (`tests/test_compatibility.py`):
```python
def test_api_compatibility():
    """Ensure Rust components maintain CrewAI API compatibility."""
    from fast_crewai import RustMemoryStorage
    from crewai.memory.storage.rag_storage import RAGStorage

    # Test same interface
    rust_storage = RustMemoryStorage()
    python_storage = RAGStorage(type="test")

    # Both should have same methods
    assert hasattr(rust_storage, 'save')
    assert hasattr(rust_storage, 'search')
    assert hasattr(python_storage, 'save')
    assert hasattr(python_storage, 'search')
```

## Development Workflow

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Edit Rust code in `src/`
   - Edit Python wrappers in `fast_crewai/`
   - Add tests for new functionality

3. **Build and Test**
   ```bash
   maturin develop
   python -m pytest
   cargo test
   ```

4. **Format Code**
   ```bash
   # Format Rust code
   cargo fmt

   # Format Python code
   black fast_crewai/ tests/
   isort fast_crewai/ tests/
   ```

5. **Run Linting**
   ```bash
   # Rust linting
   cargo clippy

   # Python linting
   flake8 fast_crewai/ tests/
   mypy fast_crewai/
   ```

### Debugging

#### Python Debugging

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

import fast_crewai.shim
fast_crewai.shim.enable_rust_acceleration(verbose=True)
```

#### Rust Debugging

```bash
# Build with debug symbols
maturin develop --profile dev

# Enable Rust backtraces
export RUST_BACKTRACE=1

# Use GDB for debugging
gdb python
(gdb) run your_script.py
```

#### Memory Debugging

```bash
# Use Valgrind for memory leak detection
valgrind --tool=memcheck python your_script.py

# Use AddressSanitizer
export RUSTFLAGS="-Z sanitizer=address"
cargo build --target x86_64-unknown-linux-gnu
```

## Contributing Guidelines

### Code Style

#### Rust Code Style

```rust
// Use descriptive names
pub struct RustMemoryStorage {
    data: Arc<Mutex<Vec<String>>>,
}

// Document public APIs
/// High-performance memory storage using Rust backend.
///
/// # Examples
///
/// ```rust
/// let storage = RustMemoryStorage::new();
/// storage.save("data").unwrap();
/// ```
pub fn save(&self, value: &str) -> PyResult<()> {
    // Implementation
}

// Handle errors properly
pub fn search(&self, query: &str) -> PyResult<Vec<String>> {
    let data = self.data.lock().map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to acquire lock: {}", e)
        )
    })?;
    // Continue implementation
}
```

#### Python Code Style

```python
# Follow PEP 8
class RustMemoryStorage:
    """High-performance memory storage using Rust backend."""

    def __init__(self, use_rust: Optional[bool] = None) -> None:
        """Initialize memory storage."""
        pass

    def save(self, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save a value to memory."""
        pass
```

### Documentation

#### Rust Documentation

```rust
/// High-performance memory storage implementation.
///
/// This struct provides a thread-safe memory storage system optimized for
/// high-throughput operations using SIMD instructions where available.
///
/// # Examples
///
/// ```rust
/// let storage = RustMemoryStorage::new();
/// storage.save("Hello, World!").unwrap();
/// let results = storage.search("Hello").unwrap();
/// assert!(!results.is_empty());
/// ```
///
/// # Thread Safety
///
/// This struct is thread-safe and can be shared across multiple threads
/// using Arc<RustMemoryStorage>.
#[pyclass]
pub struct RustMemoryStorage {
    // ...
}
```

#### Python Documentation

```python
def save(self, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Save a value to memory.

    Args:
        value: The value to save
        metadata: Optional metadata associated with the value

    Raises:
        RuntimeError: If storage operation fails

    Example:
        >>> storage = RustMemoryStorage()
        >>> storage.save("Hello", {"priority": "high"})
    """
```

### Pull Request Process

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/crewai-rust.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/add-new-feature
   ```

3. **Implement Changes**
   - Add functionality
   - Write tests
   - Update documentation

4. **Test Thoroughly**
   ```bash
   # All tests must pass
   python -m pytest
   cargo test

   # No linting errors
   cargo clippy
   flake8 fast_crewai/
   ```

5. **Commit with Good Messages**
   ```bash
   git commit -m "feat: add SIMD acceleration for memory search

   - Implement AVX2 instructions for string matching
   - Add fallback for systems without SIMD support
   - Improves search performance by 15-20x

   Fixes #123"
   ```

6. **Create Pull Request**
   - Describe changes clearly
   - Include performance impact
   - Reference relevant issues

### Release Process

1. **Version Bump**
   ```bash
   # Update version in Cargo.toml and __init__.py
   # Follow semantic versioning
   ```

2. **Update Changelog**
   ```markdown
   ## [0.2.0] - 2024-01-15
   ### Added
   - SIMD acceleration for memory operations
   - Connection pooling for database operations

   ### Changed
   - Improved error handling in tool execution

   ### Fixed
   - Memory leak in concurrent task execution
   ```

3. **Build Release**
   ```bash
   # Build wheels for all platforms
   maturin build --release

   # Test release build
   pip install target/wheels/fast_crewai-*.whl
   python -m pytest
   ```

4. **Tag Release**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

## Performance Optimization

### Profiling

```bash
# Profile Rust code
cargo build --release
perf record --call-graph=dwarf target/release/your_binary
perf report

# Profile Python integration
python -m cProfile -o profile.stats your_script.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats()"
```

### Benchmarking

```rust
// Add to Cargo.toml: criterion = "0.4"
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_memory_search(c: &mut Criterion) {
    let storage = RustMemoryStorage::new();
    // Populate with test data

    c.bench_function("memory_search", |b| {
        b.iter(|| storage.search(black_box("query")))
    });
}

criterion_group!(benches, benchmark_memory_search);
criterion_main!(benches);
```

### Optimization Guidelines

1. **Use SIMD When Possible**
   ```rust
   #[cfg(target_arch = "x86_64")]
   use std::arch::x86_64::*;

   // Implement SIMD version with fallback
   ```

2. **Minimize Allocations**
   ```rust
   // Good: Reuse buffers
   let mut buffer = Vec::with_capacity(1024);

   // Bad: Allocate in loop
   for item in items {
       let vec = Vec::new();  // Don't do this
   }
   ```

3. **Use Zero-Copy When Possible**
   ```rust
   // Good: Return string slice
   pub fn get_data(&self) -> &str {
       &self.data
   }

   // Bad: Clone string
   pub fn get_data(&self) -> String {
       self.data.clone()
   }
   ```

## Next Steps

- **[Architecture Guide](ARCHITECTURE.md)** - Understand the technical design
- **[Performance Guide](PERFORMANCE.md)** - Optimize your contributions
- **[API Reference](COMPATIBILITY.md)** - Maintain compatibility
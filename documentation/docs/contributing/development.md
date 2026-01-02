# Development Setup

Guide for setting up a development environment to contribute to Fast-CrewAI.

## Prerequisites

### Required

1. **Python 3.10+**
    ```bash
    python3 --version
    ```

2. **Rust toolchain**
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source ~/.cargo/env
    rustc --version
    ```

3. **uv** (recommended package manager)
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### Optional

- **Docker** for isolated testing
- **make** for convenience commands

## Setup Steps

### 1. Clone Repository

```bash
git clone https://github.com/neul-labs/fast-crewai.git
cd fast-crewai
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync --dev
```

### 3. Build Rust Extension

```bash
# Development build (fast iteration)
uv run maturin develop

# Release build (optimized)
uv run maturin develop --release
```

### 4. Verify Installation

```bash
# Run tests
uv run pytest

# Quick verification
uv run python -c "from fast_crewai import is_acceleration_available; print(f'Rust: {is_acceleration_available()}')"
```

## Development Workflow

### Making Changes

#### Rust Changes

1. Edit `src/lib.rs`
2. Rebuild: `uv run maturin develop`
3. Test: `uv run pytest tests/`

#### Python Changes

1. Edit files in `fast_crewai/`
2. Test directly (no rebuild needed)

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_memory.py -v

# Specific test function
uv run pytest tests/test_memory.py::test_rust_memory_storage -v

# With coverage
./scripts/run_tests.sh coverage

# Fast tests only (exclude slow/integration)
./scripts/run_tests.sh fast
```

### Code Quality

```bash
# Format Python code
uv run ruff format

# Lint Python code
uv run ruff check

# Format Rust code
cargo fmt

# Lint Rust code
cargo clippy
```

## Project Structure

```
fast-crewai/
├── src/
│   └── lib.rs           # Rust implementations
├── fast_crewai/
│   ├── __init__.py      # Package exports
│   ├── shim.py          # Monkey patching system
│   ├── memory.py        # Memory wrapper
│   ├── tools.py         # Tool executor wrapper
│   ├── tasks.py         # Task executor wrapper
│   ├── database.py      # SQLite wrapper
│   └── serialization.py # Message serialization
├── tests/
│   ├── test_memory.py
│   ├── test_tools.py
│   ├── test_tasks.py
│   └── test_integration.py
├── documentation/       # MkDocs documentation
├── Cargo.toml          # Rust dependencies
├── pyproject.toml      # Python dependencies
└── CLAUDE.md           # AI assistant guidance
```

## Adding New Features

### Adding a Rust Component

1. **Implement in Rust** (`src/lib.rs`):
    ```rust
    #[pyclass]
    pub struct RustNewComponent {
        // fields
    }

    #[pymethods]
    impl RustNewComponent {
        #[new]
        pub fn new() -> Self { /* ... */ }

        pub fn method(&self) -> PyResult<String> { /* ... */ }
    }
    ```

2. **Create Python wrapper** (`fast_crewai/new_component.py`):
    ```python
    class AcceleratedNewComponent:
        def __init__(self, use_rust=None):
            if use_rust is None:
                self._use_rust = _RUST_AVAILABLE
            # ...
    ```

3. **Add to shim** (`fast_crewai/shim.py`):
    ```python
    new_patches = [
        ('crewai.module.path', 'OriginalClass', AcceleratedNewComponent),
    ]
    ```

4. **Write tests** (`tests/test_new_component.py`)

5. **Update documentation**

### Adding Tests

```python
import pytest
from fast_crewai import AcceleratedNewComponent

def test_basic_functionality():
    component = AcceleratedNewComponent(use_rust=True)
    result = component.method()
    assert result == expected

@pytest.mark.performance
def test_performance():
    # Performance test
    pass

@pytest.mark.integration
def test_with_crewai():
    # Integration test
    pass
```

## Debugging

### Rust Debugging

```bash
# Build with debug symbols
uv run maturin develop --profile dev

# Enable backtraces
export RUST_BACKTRACE=1
```

### Python Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

import fast_crewai.shim
fast_crewai.shim.enable_acceleration(verbose=True)
```

### Profiling

```python
import cProfile

def workflow():
    # Your code
    pass

cProfile.run('workflow()', 'profile.prof')

# Analyze with snakeviz
# pip install snakeviz
# snakeviz profile.prof
```

## Benchmarking

```bash
# Run benchmark suite
uv run python scripts/test_benchmarking.py --iterations 500

# Generate report
uv run python scripts/test_benchmarking.py --iterations 500 --report-output BENCHMARK.md

# Compare with/without acceleration
make test-comparison
```

## Common Issues

### Build Fails

```bash
# Clean and rebuild
cargo clean
uv run maturin develop
```

### Tests Fail

```bash
# Check Rust is available
uv run python -c "from fast_crewai import is_acceleration_available; print(is_acceleration_available())"

# Run with verbose output
uv run pytest -v --tb=long
```

### Import Errors

```bash
# Rebuild extension
uv run maturin develop

# Verify installation
uv run python -c "import fast_crewai; print(fast_crewai.__file__)"
```

## Pull Request Checklist

- [ ] Tests pass: `uv run pytest`
- [ ] Code formatted: `uv run ruff format && cargo fmt`
- [ ] Linting passes: `uv run ruff check && cargo clippy`
- [ ] Documentation updated if needed
- [ ] Benchmark results included for performance changes

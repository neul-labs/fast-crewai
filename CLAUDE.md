# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fast-CrewAI is a **drop-in performance enhancement layer** that provides high-performance Rust implementations for critical CrewAI components. The key innovation is a sophisticated **monkey patching/shim system** that transparently replaces Python components with Rust equivalents while maintaining 100% API compatibility.

## Essential Commands

### Development Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (includes maturin)
uv sync --dev

# Build Rust extension in development mode (fastest iteration)
uv run maturin develop

# Force rebuild after Rust changes
uv run maturin develop --force
```

### Testing
```bash
# Run all tests
uv run pytest

# Fast tests only (exclude slow/integration/performance)
./scripts/run_tests.sh fast

# Specific test categories
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
./scripts/run_tests.sh performance

# Single test file
uv run pytest tests/test_memory.py -v

# Single test function
uv run pytest tests/test_memory.py::test_rust_memory_storage -v

# Tests with coverage
./scripts/run_tests.sh coverage
```

### Build and Distribution
```bash
# Release build (optimized)
uv run maturin build --release

# Build for specific Python version
uv run maturin develop --python python3.10

# Check package structure
uv run python -c "import fast_crewai; print(fast_crewai.__file__)"
```

## Core Architecture

### Monkey Patching System (`fast_crewai/shim.py`)

The **heart of the system** - enables zero-code integration by replacing CrewAI classes at import time:

```python
# Activation triggers global module replacement
import fast_crewai.shim  # Auto-activates patching

# This import now returns RustMemoryStorage instead of RAGStorage
from crewai.memory import RAGStorage
```

**Key mechanisms:**
- `sys.modules` manipulation for import interception
- Class replacement via `setattr(module, class_name, rust_class)`
- Backup system in `_original_classes` for restoration
- Environment variable control (`FAST_CREWAI_*=true/false/auto`)

### Dual Implementation Pattern

Each component has both Rust and Python implementations with automatic fallback:

- **Rust Core** (`src/lib.rs`): High-performance native implementations
- **Python Wrappers** (`fast_crewai/*.py`): Compatibility layer with fallback logic
- **Auto-Detection**: `use_rust=None` automatically chooses best available implementation

### Component Replacement Targets

```python
# Memory components - ✅ FULLY IMPLEMENTED (TF-IDF semantic search)
'crewai.memory.storage.rag_storage' → AcceleratedMemoryStorage
'crewai.memory.short_term.short_term_memory' → AcceleratedMemoryStorage
'crewai.memory.long_term.long_term_memory' → AcceleratedMemoryStorage
'crewai.memory.entity.entity_memory' → AcceleratedMemoryStorage
# Features: TF-IDF with cosine similarity for semantic search

# Database operations - ✅ FULLY IMPLEMENTED (FTS5 + connection pooling)
'crewai.memory.storage.ltm_sqlite_storage' → AcceleratedSQLiteWrapper
'crewai.memory.storage.kickoff_task_outputs_storage' → AcceleratedSQLiteWrapper
# Features: FTS5 full-text search (11x faster), BM25 ranking, r2d2 connection pooling

# Tool execution - ✅ FULLY IMPLEMENTED (17x faster with caching)
'crewai.tools.base_tool.BaseTool' → AcceleratedBaseTool (inherits from BaseTool)
'crewai.tools.structured_tool.CrewStructuredTool' → AcceleratedStructuredTool
# Features: Result caching with TTL, serde JSON validation, execution statistics

# Task execution - ✅ FULLY IMPLEMENTED (dependency tracking)
'crewai.task.Task' → AcceleratedTask (inherits from Task)
'crewai.crew.Crew' → AcceleratedCrew (inherits from Crew)
# Features: Topological sort, cycle detection, parallel scheduling via Tokio

# Serialization - ✅ FULLY IMPLEMENTED (34x faster)
# AgentMessage class with serde-based JSON serialization
# 34.5x faster serialization, 58% less memory usage
```

## Development Patterns

### Dynamic Inheritance Pattern

Tool and Task acceleration uses a dynamic inheritance pattern to maintain full API compatibility:

```python
def create_accelerated_base_tool():
    """Create accelerated version at runtime by importing and inheriting."""
    try:
        from crewai.tools.base_tool import BaseTool as _OriginalBaseTool

        class AcceleratedBaseTool(_OriginalBaseTool):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._acceleration_enabled = True

            def _run(self, *args, **kwargs):
                # Add acceleration logic here
                return super()._run(*args, **kwargs)

        return AcceleratedBaseTool
    except ImportError:
        return None  # CrewAI not installed

# Create at module import time
AcceleratedBaseTool = create_accelerated_base_tool()
```

**Benefits:**
- Full API compatibility (inherits all methods and attributes)
- Works even if CrewAI isn't installed (returns None)
- Can override specific methods for acceleration
- Maintains original behavior as fallback
- No hardcoded dependencies on CrewAI internals

**Usage in Shim:**
```python
def _patch_tool_components():
    from fast_crewai.tools import AcceleratedBaseTool

    # Only patch if successfully created
    if AcceleratedBaseTool is not None:
        _monkey_patch_class('crewai.tools.base_tool', 'BaseTool', AcceleratedBaseTool)
```

### Adding New Rust Components

1. **Rust Implementation** (`src/lib.rs`):
   ```rust
   #[pyclass]
   pub struct RustNewComponent {
       // Implementation
   }

   #[pymethods]
   impl RustNewComponent {
       #[new]
       pub fn new() -> Self { /* */ }

       pub fn method(&self) -> PyResult<String> { /* */ }
   }
   ```

2. **Python Wrapper** (`fast_crewai/new_component.py`):
   ```python
   class RustNewComponent:
       def __init__(self, use_rust=None):
           self.use_rust = self._detect_rust_availability() if use_rust is None else use_rust
           if self.use_rust:
               self._rust_impl = _core.RustNewComponent()
   ```

3. **Shim Registration** (`fast_crewai/shim.py`):
   ```python
   new_patches = [
       ('crewai.module.path', 'OriginalClass', RustNewComponent),
   ]
   ```

### Error Handling Pattern

All components follow this fallback pattern:
```python
try:
    result = self._rust_impl.method(args)
except Exception as e:
    if self._fallback_enabled:
        print(f"Warning: Rust failed, using Python: {e}")
        self.use_rust = False
        result = self._python_fallback(args)
    else:
        raise
```

### Testing New Components

1. **Unit Tests**: Test Rust implementation directly
2. **Integration Tests**: Test through CrewAI workflows
3. **Compatibility Tests**: Verify identical behavior to Python
4. **Performance Tests**: Benchmark speed improvements
5. **Fallback Tests**: Ensure graceful degradation

## Build System Architecture

### Maturin Configuration (`pyproject.toml`)
- **Build Backend**: `maturin` for Rust-Python integration
- **Module Name**: `fast_crewai._core` (Rust extension)
- **Target**: `src/lib.rs` compiled as `cdylib`

### Development vs Production
- **Development**: `maturin develop` for fast iteration
- **Production**: `maturin build --release` for optimized binaries
- **Distribution**: Wheels built for multiple platforms

## Key Implementation Details

### Memory Safety
- **Rust Side**: Memory-safe by design with ownership system
- **Python Bridge**: `Arc<Mutex<T>>` for thread-safe shared state
- **Error Handling**: Rust `Result<T, E>` converted to Python exceptions

### Performance Optimizations
- **Memory Operations**: TF-IDF with cosine similarity for semantic search
- **Tool Execution**: Result caching with TTL, serde JSON validation (17x faster)
- **Task Execution**: Tokio async runtime, topological sort, dependency tracking
- **Serialization**: serde-based JSON (34x faster, 58% less memory)
- **Database**: FTS5 full-text search (11x faster), BM25 ranking, r2d2 connection pooling

### Configuration System
Environment variables provide fine-grained control:
```bash
FAST_CREWAI_ACCELERATION=1    # Global enable/disable
FAST_CREWAI_MEMORY=true       # Per-component control
FAST_CREWAI_TOOLS=false       # Selective disabling
```

## Testing Strategy

### Test Organization
- `test_memory.py`: Memory component tests
- `test_tools.py`: Tool execution tests
- `test_tasks.py`: Task execution tests
- `test_integration.py`: End-to-end CrewAI workflows
- `test_shim.py`: Monkey patching system tests

### Performance Testing
Use markers to control test execution:
```python
@pytest.mark.performance
def test_memory_benchmark():
    # Benchmark tests

@pytest.mark.slow
def test_large_dataset():
    # Resource-intensive tests
```

## Critical Files for Understanding

1. **`fast_crewai/shim.py`**: The core monkey patching system
2. **`src/lib.rs`**: All Rust implementations and PyO3 bindings
3. **`fast_crewai/__init__.py`**: Package initialization and fallback logic
4. **`pyproject.toml`**: Build configuration and project metadata
5. **`tests/test_integration.py`**: End-to-end usage patterns

## Performance Expectations

When working with this codebase, expect these performance characteristics (see [BENCHMARK.md](BENCHMARK.md) for latest numbers):

### Benchmark Results (as of latest run):

| Component | Improvement | Details |
|-----------|-------------|---------|
| **Serialization** | 🚀 **34.5x faster** | serde vs Python json (80,525 vs 2,333 ops/s) |
| **Tool Execution** | 🚀 **17.3x faster** | Result caching with configurable TTL |
| **FTS Database Search** | 🚀 **11.2x faster** | FTS5 with BM25 vs LIKE queries |
| **Database Query** | 🚀 **1.3x faster** | Connection pooling with r2d2 |
| **Memory Storage** | ✅ **TF-IDF search** | Semantic search using cosine similarity |

### Memory Usage Savings:
- **Tool Execution**: 99% less memory
- **Serialization**: 58% less memory
- **Database**: 31% less memory

### Implementation Status:

| Component | Status | Key Features |
|-----------|--------|--------------|
| **RustMemoryStorage** | ✅ Fully implemented | TF-IDF with cosine similarity for semantic search |
| **RustSQLiteWrapper** | ✅ Fully implemented | FTS5 full-text search, connection pooling, BM25 ranking |
| **RustToolExecutor** | ✅ Fully implemented | Result caching, JSON validation with serde, execution stats |
| **RustTaskExecutor** | ✅ Fully implemented | Dependency tracking, topological sort, cycle detection, Tokio runtime |
| **AgentMessage** | ✅ Fully implemented | serde-based serialization (34x faster) |

### Key Implementation Details:

**Database (RustSQLiteWrapper)**
- Real SQL query execution (not stubbed)
- FTS5 virtual table with automatic sync triggers
- `insert_memory()`, `search_memories()`, `get_all_memories()` methods
- Connection pooling via r2d2

**Tool Executor (RustToolExecutor)**
- `validate_args()` - Fast JSON validation
- `get_cached()` / `cache_result()` - Result caching with TTL
- `batch_validate()` - Batch validation
- `get_stats()` - Execution statistics

**Task Executor (RustTaskExecutor)**
- `register_task()` - Register with dependencies
- `get_execution_order()` - Topological sort (Kahn's algorithm)
- `get_ready_tasks()` - Get tasks with satisfied dependencies
- `mark_started/completed/failed()` - State management
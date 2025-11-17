# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fast-CrewAI is a **drop-in performance enhancement layer** that provides high-performance Rust implementations for critical CrewAI components. The key innovation is a sophisticated **monkey patching/shim system** that transparently replaces Python components with Rust equivalents while maintaining 100% API compatibility.

## Essential Commands

### Development Setup
```bash
# Install build dependencies
pip install maturin

# Build Rust extension in development mode (fastest iteration)
maturin develop

# Force rebuild after Rust changes
maturin develop --force
```

### Testing
```bash
# Run all tests
python -m pytest

# Fast tests only (exclude slow/integration/performance)
./scripts/run_tests.sh fast

# Specific test categories
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
./scripts/run_tests.sh performance

# Single test file
python -m pytest tests/test_memory.py -v

# Single test function
python -m pytest tests/test_memory.py::test_rust_memory_storage -v

# Tests with coverage
./scripts/run_tests.sh coverage
```

### Build and Distribution
```bash
# Release build (optimized)
maturin build --release

# Build for specific Python version
maturin develop --python python3.10

# Check package structure
python -c "import fast_crewai; print(fast_crewai.__file__)"
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
# Memory components (2-5x faster) - ✅ FULLY IMPLEMENTED
'crewai.memory.storage.rag_storage' → AcceleratedMemoryStorage
'crewai.memory.short_term.short_term_memory' → AcceleratedMemoryStorage
'crewai.memory.long_term.long_term_memory' → AcceleratedMemoryStorage
'crewai.memory.entity.entity_memory' → AcceleratedMemoryStorage

# Database operations (2-4x faster) - ✅ FULLY IMPLEMENTED
'crewai.memory.storage.ltm_sqlite_storage' → AcceleratedSQLiteWrapper
'crewai.memory.storage.kickoff_task_outputs_storage' → AcceleratedSQLiteWrapper

# Tool execution - ✅ IMPLEMENTED (Dynamic Inheritance)
'crewai.tools.base_tool.BaseTool' → AcceleratedBaseTool (inherits from BaseTool)
'crewai.tools.structured_tool.CrewStructuredTool' → AcceleratedStructuredTool (inherits from CrewStructuredTool)
# Note: Uses dynamic inheritance pattern - creates subclasses at runtime that override
# performance-critical methods while maintaining full API compatibility

# Task execution - ✅ IMPLEMENTED (Dynamic Inheritance)
'crewai.task.Task' → AcceleratedTask (inherits from Task)
'crewai.crew.Crew' → AcceleratedCrew (inherits from Crew)
# Note: Uses dynamic inheritance pattern - overrides execute/kickoff methods with
# acceleration hooks while preserving all original functionality

# Serialization - ⚠️ PARTIAL (Available but not auto-patched)
# AgentMessage class available for direct use with Rust-accelerated JSON serialization
# System-wide JSON patching not implemented to avoid compatibility issues
# Future: Could patch json.dumps/loads or integrate orjson for global acceleration
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
- **Memory Operations**: SIMD-accelerated vector operations
- **Tool Execution**: Zero-cost abstractions, stack safety
- **Task Execution**: Tokio async runtime with work-stealing
- **Serialization**: Zero-copy operations with serde
- **Database**: Connection pooling with r2d2

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

When working with this codebase, expect these performance characteristics:

### Currently Implemented:
- **Memory Operations**: 2-5x improvement (Rust backend with SIMD acceleration) ✅
- **Database Operations**: 2-4x improvement (connection pooling with r2d2) ✅
- **Tool Execution**: Acceleration hooks enabled via dynamic inheritance ✅
- **Task Execution**: Acceleration hooks enabled via dynamic inheritance ✅

### Partial/Future:
- **Serialization**: AgentMessage class available with Rust acceleration, but not auto-patched system-wide

### Implementation Status:
- Storage and database operations provide the largest performance gains
- Tool and task acceleration use dynamic inheritance to maintain compatibility
- Rust acceleration is automatically used when available, with Python fallback
- All components work whether or not Rust extension is built
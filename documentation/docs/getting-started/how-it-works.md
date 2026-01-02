# How It Works

Fast-CrewAI uses a sophisticated monkey patching system to transparently replace Python components with high-performance Rust implementations while maintaining 100% API compatibility.

## The Monkey Patching System

When you import `fast_crewai.shim`, the library intercepts CrewAI's module imports and replaces key classes with Rust-accelerated versions:

```python
import fast_crewai.shim  # Activates patching

# This import now returns RustMemoryStorage instead of RAGStorage
from crewai.memory import RAGStorage
```

### How Patching Works

The shim system manipulates Python's `sys.modules` to intercept imports:

```python
def _monkey_patch_class(module_path: str, class_name: str, new_class: Any) -> bool:
    """Replace a class in a module with a new implementation."""
    try:
        if module_path in sys.modules:
            module = sys.modules[module_path]
        else:
            module = importlib.import_module(module_path)

        # Save original for restoration
        if hasattr(module, class_name):
            original_class = getattr(module, class_name)
            _original_classes[f"{module_path}.{class_name}"] = original_class

        # Replace with Rust implementation
        setattr(module, class_name, new_class)
        return True
    except Exception:
        return False  # Graceful fallback
```

### What Gets Replaced

| CrewAI Component | Replaced With |
|------------------|---------------|
| `RAGStorage` | `AcceleratedMemoryStorage` |
| `ShortTermMemory` | `AcceleratedMemoryStorage` |
| `LongTermMemory` | `AcceleratedMemoryStorage` |
| `EntityMemory` | `AcceleratedMemoryStorage` |
| `LTMSQLiteStorage` | `AcceleratedSQLiteWrapper` |
| `BaseTool` | `AcceleratedBaseTool` |
| `Task` | `AcceleratedTask` |
| `Crew` | `AcceleratedCrew` |

## Dynamic Inheritance Pattern

Fast-CrewAI uses dynamic inheritance to maintain full API compatibility. Accelerated classes inherit from the original CrewAI classes:

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
```

**Benefits:**

- Full API compatibility (inherits all methods and attributes)
- Works even if CrewAI isn't installed (returns `None`)
- Can override specific methods for acceleration
- Maintains original behavior as fallback

## The Rust Core

All performance-critical code is implemented in Rust using PyO3:

```rust
use pyo3::prelude::*;

#[pyclass]
pub struct RustMemoryStorage {
    data: Arc<Mutex<Vec<MemoryItem>>>,
}

#[pymethods]
impl RustMemoryStorage {
    #[new]
    pub fn new() -> Self { /* ... */ }

    pub fn save(&self, value: &str) -> PyResult<()> { /* ... */ }

    pub fn search(&self, query: &str, limit: usize) -> PyResult<Vec<String>> {
        // TF-IDF cosine similarity search
        let query_frequencies = self.compute_word_frequencies(query);

        let mut scored_results: Vec<(String, f64)> = Vec::new();
        for item in &*data {
            let similarity = self.calculate_cosine_similarity(
                &query_frequencies,
                &item.word_frequencies
            );
            scored_results.push((item.content.clone(), similarity));
        }

        scored_results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        Ok(scored_results.into_iter().take(limit).map(|(c, _)| c).collect())
    }
}
```

### Performance Optimizations

| Technique | Component | Benefit |
|-----------|-----------|---------|
| **SIMD Operations** | Memory search | Vectorized string matching |
| **Zero-Copy** | Serialization | Direct memory access |
| **Async Runtime** | Task execution | Tokio-based concurrency |
| **Connection Pooling** | Database | Shared connections with r2d2 |
| **Result Caching** | Tool execution | Skip repeated computations |

## Automatic Fallback

Every component implements automatic fallback to Python if Rust fails:

```python
class AcceleratedMemoryStorage:
    def __init__(self, use_rust: Optional[bool] = None):
        if use_rust is None:
            self._use_rust = _RUST_AVAILABLE
        else:
            self._use_rust = use_rust and _RUST_AVAILABLE

        if self._use_rust:
            try:
                self._storage = _CoreMemoryStorage()
                self._implementation = "rust"
            except Exception:
                # Graceful fallback to Python
                self._use_rust = False
                self._storage = []
                self._implementation = "python"

    def save(self, value: Any, metadata: Optional[Dict] = None) -> None:
        if self._use_rust:
            try:
                self._storage.save(json.dumps(data))
            except Exception as e:
                # Automatic fallback on error
                print(f"Warning: Rust failed, using Python: {e}")
                self._use_rust = False
                self._storage = []
                self._storage.append(data)
```

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python API    │    │  Rust Core       │    │  Native Libs    │
│   (CrewAI)      │◄──►│  (Performance)   │◄──►│  (System)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
   ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
   │ Memory  │             │ SIMD    │             │ SQLite  │
   │ Tools   │             │ Async   │             │ Threading│
   │ Tasks   │             │ Zero-Copy│             │ I/O     │
   └─────────┘             └─────────┘             └─────────┘
```

## Enabling/Disabling Acceleration

You can control acceleration programmatically:

```python
import fast_crewai.shim

# Enable with verbose output
fast_crewai.shim.enable_acceleration(verbose=True)

# Disable and restore original classes
fast_crewai.shim.disable_acceleration()
```

Or via environment variables:

```bash
# Disable all acceleration
export FAST_CREWAI_ACCELERATION=0

# Enable specific components only
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_TOOLS=false
```

## Next Steps

- [Configuration](../user-guide/configuration.md) - Fine-tune acceleration settings
- [Architecture](../contributing/architecture.md) - Deep dive into the technical architecture

# API Reference

Complete API documentation for Fast-CrewAI accelerated components.

## Core Components

### AcceleratedMemoryStorage

High-performance memory storage with TF-IDF similarity search.

```python
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage(use_rust=True)
```

#### Constructor

**`AcceleratedMemoryStorage(use_rust: Optional[bool] = None)`**
- `use_rust`: Force Rust (`True`) or Python (`False`) implementation. If `None`, auto-detects based on availability and environment variables.

#### Methods

**`save(value: Any, metadata: Optional[Dict[str, Any]] = None) -> None`**
- Save a value to memory with optional metadata
- Automatically serializes data for Rust storage
- Falls back to Python implementation on error

**`search(query: str, limit: int = 3, score_threshold: float = 0.35) -> List[Dict[str, Any]]`**
- Search memory using TF-IDF cosine similarity
- Returns top matching results up to limit
- Results include value, metadata, and timestamp

**`get_all() -> List[Dict[str, Any]]`**
- Get all items in memory
- Returns list of dictionaries with value, metadata, timestamp

**`reset() -> None`**
- Clear all memory storage
- Recreates Rust storage instance

#### Properties

**`implementation: str`**
- Returns `"rust"` or `"python"` indicating current implementation
- Useful for debugging and verification

---

### AcceleratedToolExecutor

High-performance tool execution with result caching and JSON validation.

**Performance**: 🚀 **17x faster** than Python with caching enabled

```python
from fast_crewai import AcceleratedToolExecutor

executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300,
    use_rust=True
)
```

#### Constructor

**`AcceleratedToolExecutor(max_recursion_depth: int = 1000, cache_ttl_seconds: int = 300, use_rust: Optional[bool] = None)`**
- `max_recursion_depth`: Maximum recursion depth for stack safety (default: 1000)
- `cache_ttl_seconds`: Cache time-to-live in seconds (default: 300)
- `use_rust`: Force Rust (`True`) or Python (`False`) implementation

#### Methods

**`execute_tool(tool_name: str, args: Dict[str, Any], use_cache: bool = True) -> str`**
- Execute a tool with given arguments
- Prevents stack overflow with recursion depth checking
- Returns cached result if available and `use_cache=True`
- Returns formatted result string

**`validate_args(args: Dict[str, Any]) -> bool`**
- Validate tool arguments using serde-based JSON validation
- Much faster than Python json module

**`batch_validate(args_list: List[Dict[str, Any]]) -> List[bool]`**
- Batch validate multiple argument sets
- Returns list of validation results

**`clear_cache() -> int`**
- Clear all cached tool results
- Returns number of entries cleared

**`get_stats() -> Dict[str, Any]`**
- Get execution statistics
- Returns dict with `cache_hits`, `cache_misses`, `total_executions`

#### Properties

**`implementation: str`**
- Returns `"rust"` or `"python"` indicating current implementation

---

### AcceleratedTaskExecutor

Task execution with dependency tracking and topological sort.

```python
from fast_crewai import AcceleratedTaskExecutor

executor = AcceleratedTaskExecutor(use_rust=True)
```

#### Constructor

**`AcceleratedTaskExecutor(use_rust: Optional[bool] = None)`**
- `use_rust`: Force Rust (`True`) or Python (`False`) implementation

#### Methods

**`register_task(task_id: str, dependencies: List[str] = []) -> None`**
- Register a task with its dependencies
- Dependencies must be valid task IDs

**`get_execution_order() -> List[str]`**
- Get optimal execution order using topological sort (Kahn's algorithm)
- Raises `ValueError` if circular dependency detected

**`get_ready_tasks() -> List[str]`**
- Get tasks ready for execution (all dependencies completed)
- Returns list of task IDs

**`mark_started(task_id: str) -> None`**
- Mark a task as started/in-progress

**`mark_completed(task_id: str, result: str) -> None`**
- Mark a task as completed with its result

**`execute_concurrent(task_ids: List[str]) -> List[str]`**
- Execute multiple tasks concurrently via Tokio runtime
- Returns list of completion results

**`get_stats() -> Dict[str, Any]`**
- Get execution statistics
- Returns dict with `tasks_scheduled`, `tasks_completed`, `tasks_pending`

#### Properties

**`implementation: str`**
- Returns `"rust"` or `"python"` indicating current implementation

---

### AgentMessage

Zero-copy serialization for agent messages using serde.

**Performance**: 🚀 **34x faster** serialization than Python json

```python
from fast_crewai import AgentMessage

message = AgentMessage(
    id="msg-001",
    sender="agent_1",
    recipient="agent_2",
    content="Message content",
    timestamp=1700000000,
    use_rust=True
)
```

#### Constructor

**`AgentMessage(id: str, sender: str, recipient: str, content: str, timestamp: int, use_rust: Optional[bool] = None)`**
- All fields are required
- `use_rust`: Force Rust (`True`) or Python (`False`) implementation

#### Methods

**`to_json() -> str`**
- Serialize message to JSON string
- Uses serde for 34x faster serialization

**`from_json(json_str: str, use_rust: Optional[bool] = None) -> AgentMessage`** (static)
- Deserialize JSON string to AgentMessage
- Uses serde for 14x faster deserialization

#### Properties

- `id: str` - Message identifier
- `sender: str` - Sender identifier
- `recipient: str` - Recipient identifier
- `content: str` - Message content
- `timestamp: int` - Unix timestamp

---

### AcceleratedSQLiteWrapper

High-performance SQLite wrapper with connection pooling and FTS5 search.

**Performance**: 🚀 **11x faster** FTS5 search than LIKE queries

```python
from fast_crewai import AcceleratedSQLiteWrapper

db = AcceleratedSQLiteWrapper(
    db_path="database.db",
    pool_size=20,
    use_rust=True
)
```

#### Constructor

**`AcceleratedSQLiteWrapper(db_path: str, pool_size: int = 5, use_rust: Optional[bool] = None)`**
- `db_path`: Path to SQLite database file
- `pool_size`: Connection pool size (r2d2 pooling)
- `use_rust`: Force Rust (`True`) or Python (`False`) implementation

#### Methods

**`execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]`**
- Execute SELECT query with parameters
- Returns list of result dictionaries

**`execute_update(query: str, params: Optional[Dict[str, Any]] = None) -> int`**
- Execute UPDATE/INSERT/DELETE query
- Returns number of affected rows

**`execute_batch(queries: List[Tuple[str, Dict[str, Any]]]) -> List[int]`**
- Execute multiple queries in a transaction
- Returns list of affected row counts

**`save_memory(task_description: str, metadata: Dict[str, Any], datetime: str, score: float) -> Optional[int]`**
- Save a memory entry to the database
- Returns row ID (Rust) or None (Python fallback)

**`search_memories_fts(query: str, limit: int = 10) -> List[Dict[str, Any]]`**
- Search memories using FTS5 full-text search with BM25 ranking
- 11x faster than LIKE queries
- Returns list with `id`, `task_description`, `metadata`, `datetime`, `score`, `rank`

**`get_all_memories(limit: int = 100) -> List[Dict[str, Any]]`**
- Get all memories ordered by datetime (most recent first)

**`load_memories(task_description: str, latest_n: int = 5) -> Optional[List[Dict[str, Any]]]`**
- Load memory entries matching task description

**`reset() -> None`**
- Delete all memory entries

#### Properties

**`implementation: str`**
- Returns `"rust"` or `"python"` indicating current implementation

---

## Utility Functions

### Status and Configuration

```python
from fast_crewai import (
    is_acceleration_available,
    get_acceleration_status,
    configure_accelerated_components,
    get_performance_improvements,
    get_environment_info
)
```

**`is_acceleration_available() -> bool`**
- Check if Rust acceleration is available
- Returns `True` if Rust implementation is loaded

**`get_acceleration_status() -> Dict[str, Any]`**
- Get detailed status of all components
- Returns dictionary with availability info for each component

**`configure_accelerated_components(memory: bool = True, tools: bool = True, tasks: bool = True, serialization: bool = True, database: bool = True) -> None`**
- Configure which components use Rust acceleration
- Sets environment variables for component selection

**`get_performance_improvements() -> Dict[str, Dict[str, str]]`**
- Get expected performance improvements by component
- Returns dictionary with improvement estimates

**`get_environment_info() -> Dict[str, Any]`**
- Get current environment configuration
- Returns dictionary with environment variable settings

---

### Automatic Acceleration (Shim)

```python
import fast_crewai.shim  # Auto-enables on import!

# Or manually control:
fast_crewai.shim.enable_acceleration(verbose=True)  # Shows what was patched
fast_crewai.shim.disable_acceleration()  # Restore originals
```

**`enable_acceleration(verbose: bool = False) -> bool`**
- Enable automatic component replacement via monkey patching
- Returns `True` if at least one component was patched

**`disable_acceleration() -> bool`**
- Restore original CrewAI components
- Returns `True` if successful

### What Gets Patched

When you `import fast_crewai.shim`, these CrewAI classes are automatically replaced:

| CrewAI Class | Module | Replaced With |
|--------------|--------|---------------|
| `RAGStorage` | `crewai.memory.storage.rag_storage` | `AcceleratedMemoryStorage` |
| `ShortTermMemory` | `crewai.memory.short_term` | `AcceleratedMemoryStorage` |
| `LongTermMemory` | `crewai.memory.long_term` | `AcceleratedMemoryStorage` |
| `EntityMemory` | `crewai.memory.entity` | `AcceleratedMemoryStorage` |
| `LTMSQLiteStorage` | `crewai.memory.storage.ltm_sqlite_storage` | `AcceleratedSQLiteWrapper` |
| `KickoffTaskOutputsSQLiteStorage` | `crewai.memory.storage` | `AcceleratedSQLiteWrapper` |
| `BaseTool` | `crewai.tools.base_tool` | `AcceleratedBaseTool` |
| `CrewStructuredTool` | `crewai.tools.structured_tool` | `AcceleratedStructuredTool` |
| `Task` | `crewai.task` | `AcceleratedTask` |
| `Crew` | `crewai.crew` | `AcceleratedCrew` |

---

## Environment Variables

Control component behavior through environment variables:

```bash
# Global acceleration toggle
export FAST_CREWAI_ACCELERATION=1    # Enable all acceleration
export FAST_CREWAI_ACCELERATION=0    # Disable all acceleration

# Per-component control
export FAST_CREWAI_MEMORY=true       # Memory acceleration
export FAST_CREWAI_TOOLS=true        # Tool acceleration
export FAST_CREWAI_TASKS=true        # Task acceleration
export FAST_CREWAI_SERIALIZATION=true  # Serialization acceleration
export FAST_CREWAI_DATABASE=true     # Database acceleration
```

Values: `true`, `false`, or `auto` (default - uses Rust if available)

---

## Error Handling

All components provide graceful fallback to Python implementations:

```python
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage(use_rust=True)

# Check implementation being used
if storage.implementation == "rust":
    print("Using Rust implementation")
else:
    print("Using Python fallback")

# Verify Rust is active
from fast_crewai import is_acceleration_available
print(f"Rust available: {is_acceleration_available()}")
```

---

## Performance Characteristics

### Benchmark Results

| Component | Improvement | Rust ops/s | Python ops/s |
|-----------|-------------|------------|--------------|
| **Serialization** | 🚀 **34.5x** | 80,525 | 2,333 |
| **Tool Execution** | 🚀 **17.3x** | 11,616 | 670 |
| **FTS5 Search** | 🚀 **11.2x** | 10,206 | 913 |
| **Database Query** | 🚀 **1.3x** | 1,586 | 1,262 |

### Memory Usage

| Component | Python | Rust | Savings |
|-----------|--------|------|---------|
| Tool Execution | 1.2 MB | 0.0 MB | **99% less** |
| Serialization | 8.0 MB | 3.4 MB | **58% less** |
| Database | 0.1 MB | 0.1 MB | **31% less** |

### Implementation Details

**Memory Storage**
- Search Algorithm: TF-IDF cosine similarity
- Thread Safety: Full thread safety with `Arc<Mutex<>>`
- Fallback: Automatic Python fallback on errors

**Tool Execution**
- Stack Safety: Configurable recursion depth limits
- Caching: Result caching with configurable TTL
- Validation: serde-based JSON validation

**Task Execution**
- Dependency Tracking: Topological sort (Kahn's algorithm)
- Cycle Detection: Automatic circular dependency detection
- Concurrency: Tokio work-stealing scheduler

**Serialization**
- Format: JSON with serde
- Performance: 34x faster serialization, 14x faster deserialization
- Memory: 58% less memory usage

**Database Operations**
- Pooling: r2d2 connection pooling
- Search: FTS5 with BM25 relevance ranking
- Concurrency: Multiple concurrent operations

---

## Examples

### Basic Usage

```python
from fast_crewai import AcceleratedMemoryStorage, AcceleratedToolExecutor

# Memory storage with TF-IDF search
storage = AcceleratedMemoryStorage(use_rust=True)
storage.save("Important data about machine learning", {"priority": "high"})
results = storage.search("machine learning", limit=5)

# Tool execution with caching
executor = AcceleratedToolExecutor(
    max_recursion_depth=1000,
    cache_ttl_seconds=300,
    use_rust=True
)
result = executor.execute_tool("calculator", {"operation": "add", "operands": [1, 2]})

# Check cache stats
stats = executor.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
```

### Task Dependency Management

```python
from fast_crewai import AcceleratedTaskExecutor

executor = AcceleratedTaskExecutor(use_rust=True)

# Register tasks with dependencies
executor.register_task("fetch_data", dependencies=[])
executor.register_task("clean_data", dependencies=["fetch_data"])
executor.register_task("analyze", dependencies=["clean_data"])
executor.register_task("visualize", dependencies=["clean_data"])
executor.register_task("report", dependencies=["analyze", "visualize"])

# Get optimal execution order
order = executor.get_execution_order()
print(f"Execution order: {order}")
# ['fetch_data', 'clean_data', 'analyze', 'visualize', 'report']

# Execute tasks
for task_id in order:
    executor.mark_started(task_id)
    # ... execute task ...
    executor.mark_completed(task_id, "success")
```

### Database with FTS5 Search

```python
from fast_crewai import AcceleratedSQLiteWrapper

db = AcceleratedSQLiteWrapper("memories.db", pool_size=20, use_rust=True)

# Save memories
db.save_memory(
    task_description="Analyze machine learning model performance",
    metadata={"agent": "analyst", "priority": 1},
    datetime="2024-01-01 10:00:00",
    score=0.95
)

# FTS5 search with BM25 ranking (11x faster than LIKE)
results = db.search_memories_fts("machine learning", limit=10)
for result in results:
    print(f"Match: {result['task_description']} (rank: {result['rank']:.2f})")
```

### CrewAI Integration

```python
import fast_crewai.shim  # Enable automatic acceleration
from crewai import Agent, Task, Crew

# Your existing CrewAI code now uses Rust components automatically
agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert analyst")
task = Task(description="Analyze data", expected_output="Report", agent=agent)
crew = Crew(agents=[agent], tasks=[task], memory=True)
result = crew.kickoff()  # Now accelerated with Rust
```

### Performance Benchmarking

```python
import time
from fast_crewai import AcceleratedMemoryStorage, AgentMessage

# Benchmark memory operations
storage = AcceleratedMemoryStorage(use_rust=True)
start = time.time()
for i in range(1000):
    storage.save(f"Document {i} about AI and machine learning")
save_time = time.time() - start

start = time.time()
for i in range(100):
    results = storage.search("machine learning", limit=10)
search_time = time.time() - start

print(f"Save: {1000/save_time:.1f} docs/sec")
print(f"Search: {100/search_time:.1f} queries/sec")

# Benchmark serialization
start = time.time()
for i in range(10000):
    msg = AgentMessage(str(i), "sender", "recipient", f"content_{i}", i, use_rust=True)
    json_str = msg.to_json()
print(f"Serialization: {10000/(time.time()-start):.0f} msgs/sec")
```

# API Reference

Complete API documentation for CrewAI Rust components.

## Core Components

### RustMemoryStorage

High-performance memory storage with TF-IDF similarity search.

```python
from fast_crewai import RustMemoryStorage

storage = RustMemoryStorage()
```

#### Methods

**`save(value: Any, metadata: Optional[Dict[str, Any]] = None) -> None`**
- Save a value to memory with optional metadata
- Automatically serializes data for Rust storage
- Falls back to Python implementation on error

**`search(query: str, limit: int = 3, score_threshold: float = 0.35) -> List[Dict[str, Any]]`**
- Search memory using TF-IDF similarity
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
- Returns "rust" or "python" indicating current implementation
- Useful for debugging and verification

### RustToolExecutor

Stack-safe tool execution with recursion limits.

```python
from fast_crewai import RustToolExecutor

executor = RustToolExecutor(max_recursion_depth=1000)
```

#### Methods

**`execute_tool(tool_name: str, args: str) -> str`**
- Execute a tool with given arguments
- Prevents stack overflow with recursion depth checking
- Returns formatted result string

#### Parameters

- `max_recursion_depth: int` - Maximum recursion depth (default: 1000)

### RustTaskExecutor

Concurrent task execution using Tokio runtime.

```python
from fast_crewai import RustTaskExecutor

executor = RustTaskExecutor()
```

#### Methods

**`execute_concurrent_tasks(tasks: List[str]) -> List[str]`**
- Execute multiple tasks concurrently
- Uses Tokio work-stealing scheduler
- Returns list of completion messages

### AgentMessage

Zero-copy serialization for agent messages.

```python
from fast_crewai import AgentMessage

message = AgentMessage("1", "sender", "recipient", "content", 1234567890)
```

#### Constructor

**`AgentMessage(id: str, sender: str, recipient: str, content: str, timestamp: u64)`**
- Create a new agent message
- All fields are required

#### Methods

**`to_json() -> str`**
- Serialize message to JSON string
- Zero-copy serialization for performance

**`from_json(json_str: str) -> AgentMessage`**
- Deserialize JSON string to AgentMessage
- Static method for creating from JSON

#### Properties

- `id: str` - Message identifier
- `sender: str` - Sender identifier  
- `recipient: str` - Recipient identifier
- `content: str` - Message content
- `timestamp: u64` - Unix timestamp

### RustSQLiteWrapper

High-performance SQLite wrapper with connection pooling.

```python
from fast_crewai import RustSQLiteWrapper

db = RustSQLiteWrapper("database.db", pool_size=10)
```

#### Constructor

**`RustSQLiteWrapper(db_path: str, pool_size: u32)`**
- Create database wrapper with connection pool
- Automatically creates schema if needed

#### Methods

**`execute_query(query: str, params: Dict[str, str]) -> List[Dict[str, str]]`**
- Execute SELECT query with parameters
- Returns list of result dictionaries

**`execute_update(query: str, params: Dict[str, str]) -> int`**
- Execute UPDATE/INSERT/DELETE query
- Returns number of affected rows

**`execute_batch(queries: List[Tuple[str, Dict[str, str]]]) -> List[int]`**
- Execute multiple queries in batch
- Returns list of affected row counts

## Utility Functions

### Configuration

```python
from fast_crewai.utils import (
    is_rust_available,
    get_rust_status,
    configure_rust_components,
    get_performance_improvements,
    get_environment_info
)
```

**`is_rust_available() -> bool`**
- Check if Rust components are available
- Returns True if Rust implementation is loaded

**`get_rust_status() -> dict`**
- Get detailed status of all components
- Returns dictionary with availability info

**`configure_rust_components(memory: bool, tools: bool, tasks: bool, serialization: bool, database: bool)`**
- Configure which components use Rust
- Sets environment variables for component selection

**`get_performance_improvements() -> dict`**
- Get expected performance improvements
- Returns dictionary with improvement estimates

**`get_environment_info() -> dict`**
- Get current environment configuration
- Returns dictionary with environment variables

### Automatic Acceleration

```python
import fast_crewai.shim

# Enable automatic Rust acceleration
fast_crewai.shim.enable_rust_acceleration(verbose=True)

# Disable acceleration
fast_crewai.shim.disable_rust_acceleration()
```

**`enable_rust_acceleration(verbose: bool = False) -> bool`**
- Enable automatic component replacement
- Returns True if successful

**`disable_rust_acceleration() -> bool`**
- Restore original components
- Returns True if successful

## Environment Variables

Control component behavior through environment variables:

```bash
# Enable/disable specific components
export FAST_CREWAI_MEMORY=true
export FAST_CREWAI_TOOLS=true
export FAST_CREWAI_TASKS=false
export FAST_CREWAI_SERIALIZATION=true
export FAST_CREWAI_DATABASE=true

# Enable automatic acceleration
export FAST_CREWAI_ACCELERATION=1
```

## Error Handling

All components provide graceful fallback:

```python
from fast_crewai import RustMemoryStorage

storage = RustMemoryStorage()

# Check implementation being used
if storage.implementation == "rust":
    print("Using Rust implementation")
else:
    print("Using Python fallback")
```

## Performance Characteristics

### Memory Storage
- **Search Algorithm**: TF-IDF cosine similarity
- **Thread Safety**: Full thread safety with Arc<Mutex<>>
- **Fallback**: Automatic Python fallback on errors

### Tool Execution  
- **Stack Safety**: Configurable recursion depth limits
- **Error Handling**: Zero-cost error propagation
- **Fallback**: Graceful degradation to Python

### Task Execution
- **Concurrency**: Tokio work-stealing scheduler
- **Threading**: True parallelism without GIL
- **Fallback**: Python threading fallback

### Serialization
- **Format**: JSON with serde
- **Performance**: Zero-copy operations
- **Fallback**: Python json module

### Database Operations
- **Pooling**: r2d2 connection pooling
- **Concurrency**: Multiple concurrent operations
- **Fallback**: Python sqlite3 module

## Examples

### Basic Usage

```python
from fast_crewai import RustMemoryStorage, RustToolExecutor

# Memory storage
storage = RustMemoryStorage()
storage.save("Important data", {"priority": "high"})
results = storage.search("Important", limit=5)

# Tool execution
executor = RustToolExecutor(max_recursion_depth=1000)
result = executor.execute_tool("calculator", '{"operation": "add", "operands": [1, 2]}')
```

### CrewAI Integration

```python
import fast_crewai.shim  # Enable automatic acceleration
from crewai import Agent, Task, Crew

# Your existing CrewAI code now uses Rust components
agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert")
task = Task(description="Analyze data", expected_output="Report", agent=agent)
crew = Crew(agents=[agent], tasks=[task], memory=True)
result = crew.kickoff()  # Now accelerated with Rust
```

### Performance Testing

```python
import time
from fast_crewai import RustMemoryStorage

# Benchmark memory operations
storage = RustMemoryStorage()
start = time.time()
for i in range(1000):
    storage.save(f"Document {i}")
search_start = time.time()
results = storage.search("Document", limit=10)
end = time.time()

print(f"Save time: {search_start - start:.3f}s")
print(f"Search time: {end - search_start:.3f}s")
print(f"Results: {len(results)}")
```

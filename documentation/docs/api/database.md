# AcceleratedSQLiteWrapper

High-performance SQLite wrapper with FTS5 full-text search and connection pooling.

**Performance:** 11x faster FTS5 search than LIKE queries.

## Class Definition

```python
class AcceleratedSQLiteWrapper:
    def __init__(
        self,
        db_path: str,
        pool_size: int = 5,
        use_rust: Optional[bool] = None
    )
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str` | - | Path to SQLite database file |
| `pool_size` | `int` | `5` | Connection pool size (r2d2 pooling) |
| `use_rust` | `Optional[bool]` | `None` | Force Rust or Python implementation |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `implementation` | `str` | Returns `"rust"` or `"python"` |

## Methods

### save_memory

Save a memory entry to the database.

```python
def save_memory(
    self,
    task_description: str,
    metadata: Dict[str, Any],
    datetime: str,
    score: float
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_description` | `str` | Task description text |
| `metadata` | `Dict[str, Any]` | Metadata dictionary |
| `datetime` | `str` | Timestamp string |
| `score` | `float` | Score value |

**Returns:** `Optional[int]` - Row ID (Rust) or `None` (Python fallback).

**Example:**

```python
db = AcceleratedSQLiteWrapper("memories.db", pool_size=20, use_rust=True)

row_id = db.save_memory(
    task_description="Analyze machine learning model performance",
    metadata={"agent": "analyst", "priority": 1},
    datetime="2024-01-01 10:00:00",
    score=0.95
)
print(f"Saved with ID: {row_id}")
```

---

### search_memories_fts

Search memories using FTS5 full-text search with BM25 ranking.

```python
def search_memories_fts(
    self,
    query: str,
    limit: int = 10
) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | - | Search query |
| `limit` | `int` | `10` | Maximum results |

**Returns:** `List[Dict[str, Any]]` - Results with `id`, `task_description`, `metadata`, `datetime`, `score`, `rank`.

**Example:**

```python
results = db.search_memories_fts("machine learning", limit=10)
for result in results:
    print(f"ID: {result['id']}")
    print(f"Task: {result['task_description']}")
    print(f"BM25 Rank: {result['rank']:.2f}")
```

---

### get_all_memories

Get all memories ordered by datetime.

```python
def get_all_memories(self, limit: int = 100) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `100` | Maximum results |

**Returns:** `List[Dict[str, Any]]` - All memory entries.

---

### load_memories

Load memory entries matching task description.

```python
def load_memories(
    self,
    task_description: str,
    latest_n: int = 5
) -> Optional[List[Dict[str, Any]]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_description` | `str` | - | Task description to match |
| `latest_n` | `int` | `5` | Number of latest entries |

**Returns:** `Optional[List[Dict]]` - Matching entries or `None`.

---

### execute_query

Execute a SELECT query with parameters.

```python
def execute_query(
    self,
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | - | SQL SELECT query |
| `params` | `Optional[Dict]` | `None` | Query parameters |

**Returns:** `List[Dict[str, Any]]` - Query results.

**Example:**

```python
results = db.execute_query(
    "SELECT * FROM long_term_memories WHERE score > ?",
    params={"1": 0.8}
)
```

---

### execute_update

Execute an UPDATE/INSERT/DELETE query.

```python
def execute_update(
    self,
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> int
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | - | SQL query |
| `params` | `Optional[Dict]` | `None` | Query parameters |

**Returns:** `int` - Number of affected rows.

---

### execute_batch

Execute multiple queries in a transaction.

```python
def execute_batch(
    self,
    queries: List[Tuple[str, Dict[str, Any]]]
) -> List[int]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `queries` | `List[Tuple]` | List of (query, params) tuples |

**Returns:** `List[int]` - Affected row counts for each query.

---

### reset

Delete all memory entries.

```python
def reset(self) -> None
```

## Complete Example

```python
from fast_crewai import AcceleratedSQLiteWrapper

# Create database with connection pooling
db = AcceleratedSQLiteWrapper(
    db_path="memories.db",
    pool_size=20,
    use_rust=True
)

print(f"Using: {db.implementation}")

# Save memories
memories = [
    ("Research machine learning algorithms", {"agent": "researcher"}, "2024-01-01", 0.95),
    ("Analyze neural network performance", {"agent": "analyst"}, "2024-01-02", 0.88),
    ("Optimize deep learning models", {"agent": "engineer"}, "2024-01-03", 0.92),
]

for task, meta, dt, score in memories:
    row_id = db.save_memory(task, meta, dt, score)
    print(f"Saved: {task[:30]}... (ID: {row_id})")

# FTS5 search (11x faster than LIKE)
print("\nSearching for 'machine learning':")
results = db.search_memories_fts("machine learning", limit=5)
for result in results:
    print(f"  [{result['rank']:.2f}] {result['task_description']}")

# Get all memories
print(f"\nTotal memories: {len(db.get_all_memories())}")

# Custom query
high_score = db.execute_query(
    "SELECT * FROM long_term_memories WHERE score > ?",
    params={"1": 0.9}
)
print(f"High score entries: {len(high_score)}")

# Reset
# db.reset()
```

## FTS5 Search Features

### Multi-word Search

```python
results = db.search_memories_fts("machine learning performance")
```

### Phrase Search

```python
results = db.search_memories_fts('"neural network"')  # Exact phrase
```

### Prefix Search

```python
results = db.search_memories_fts("learn*")  # Matches learning, learned, etc.
```

### BM25 Ranking

Results are ranked by BM25 relevance score:

- Higher rank = more relevant
- Considers term frequency and document length
- Automatically weights rare terms higher

## Connection Pooling

The r2d2 connection pool provides:

- **Pre-warmed connections**: Reduced latency
- **Concurrent access**: Multiple simultaneous operations
- **Automatic management**: Connection lifecycle handled

### Pool Size Guidelines

| Workload | Pool Size |
|----------|-----------|
| Low concurrency | 5-10 |
| Medium concurrency | 20-30 |
| High concurrency | 50-100 |

```python
# High-concurrency configuration
db = AcceleratedSQLiteWrapper(
    db_path="db.db",
    pool_size=50,
    use_rust=True
)
```

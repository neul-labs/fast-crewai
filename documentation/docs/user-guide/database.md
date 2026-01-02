# Database Acceleration

Fast-CrewAI provides **11x faster** full-text search using SQLite FTS5 with BM25 ranking and connection pooling via r2d2.

## Overview

| Feature | Benefit |
|---------|---------|
| **FTS5 Search** | 11x faster than LIKE queries |
| **BM25 Ranking** | Relevance-based result ordering |
| **Connection Pooling** | r2d2 pooling for concurrency |
| **Auto-sync Triggers** | Automatic FTS index updates |

## Basic Usage

```python
from fast_crewai import AcceleratedSQLiteWrapper

db = AcceleratedSQLiteWrapper(
    db_path="memories.db",
    pool_size=20,
    use_rust=True
)

# Save a memory
db.save_memory(
    task_description="Analyze machine learning model performance",
    metadata={"agent": "analyst", "priority": 1},
    datetime="2024-01-01 10:00:00",
    score=0.95
)

# FTS5 search with BM25 ranking (11x faster!)
results = db.search_memories_fts("machine learning", limit=10)
```

## With CrewAI

When using the shim, CrewAI's database operations are automatically accelerated:

```python
import fast_crewai.shim
from crewai import Crew

# Long-term memory uses accelerated SQLite
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True  # Database operations accelerated
)
```

## Saving Memories

```python
# Save with full metadata
row_id = db.save_memory(
    task_description="Research findings about neural networks",
    metadata={
        "agent": "researcher",
        "topic": "deep_learning",
        "confidence": 0.92
    },
    datetime="2024-01-15 14:30:00",
    score=0.88
)
print(f"Saved with ID: {row_id}")
```

## FTS5 Search

Full-text search with BM25 relevance ranking:

```python
# Basic search
results = db.search_memories_fts("neural networks", limit=10)

for result in results:
    print(f"ID: {result['id']}")
    print(f"Task: {result['task_description']}")
    print(f"Rank: {result['rank']:.2f}")  # BM25 score
    print(f"Score: {result['score']}")
    print("---")
```

### Search Features

```python
# Multi-word search
results = db.search_memories_fts("machine learning performance", limit=5)

# Phrase search (use quotes in query)
results = db.search_memories_fts('"neural network"', limit=5)

# Prefix search
results = db.search_memories_fts("learn*", limit=5)  # Matches learning, learned, etc.
```

## Query Operations

### Execute SELECT Queries

```python
results = db.execute_query(
    "SELECT * FROM long_term_memories WHERE score > ?",
    params={"1": 0.8}
)
```

### Execute UPDATE/INSERT/DELETE

```python
affected = db.execute_update(
    "UPDATE long_term_memories SET score = ? WHERE id = ?",
    params={"1": 0.95, "2": 123}
)
print(f"Updated {affected} rows")
```

### Batch Operations

```python
queries = [
    ("INSERT INTO table (col) VALUES (?)", {"1": "value1"}),
    ("INSERT INTO table (col) VALUES (?)", {"1": "value2"}),
    ("INSERT INTO table (col) VALUES (?)", {"1": "value3"}),
]

results = db.execute_batch(queries)
# Returns list of affected row counts
```

## Other Operations

### Get All Memories

```python
memories = db.get_all_memories(limit=100)
for mem in memories:
    print(f"{mem['datetime']}: {mem['task_description'][:50]}...")
```

### Load Specific Memories

```python
memories = db.load_memories(
    task_description="machine learning",
    latest_n=5
)
```

### Reset Database

```python
db.reset()  # Deletes all memory entries
```

## Connection Pooling

The r2d2 connection pool improves concurrency:

```python
# Configure pool size based on concurrency needs
db = AcceleratedSQLiteWrapper(
    db_path="db.db",
    pool_size=50,  # For high-concurrency workloads
    use_rust=True
)
```

### Pool Size Guidelines

| Workload | Recommended Pool Size |
|----------|----------------------|
| Low concurrency | 5-10 |
| Medium concurrency | 20-30 |
| High concurrency | 50-100 |

## Performance Comparison

### FTS5 vs LIKE

| Query Type | LIKE Query | FTS5 Search | Speedup |
|------------|------------|-------------|---------|
| Single word | 913 ops/s | 10,206 ops/s | 11x |
| Multi-word | 456 ops/s | 9,800 ops/s | 21x |
| Phrase | 312 ops/s | 8,500 ops/s | 27x |

### Connection Pooling

| Operation | No Pool | With Pool | Speedup |
|-----------|---------|-----------|---------|
| Query | 1,262 ops/s | 1,586 ops/s | 1.3x |
| Insert | 380 ops/s | 416 ops/s | 1.1x |
| Concurrent (10 threads) | 2,100 ops/s | 12,500 ops/s | 6x |

## Best Practices

### Index Design

FTS5 automatically indexes `task_description`. For other columns:

```python
# Create additional indexes if needed
db.execute_update(
    "CREATE INDEX IF NOT EXISTS idx_score ON long_term_memories(score)"
)
```

### Batch Inserts

For bulk data loading:

```python
memories = [
    ("Task 1", {"key": "val"}, "2024-01-01", 0.9),
    ("Task 2", {"key": "val"}, "2024-01-02", 0.8),
    # ... many more
]

for task, meta, dt, score in memories:
    db.save_memory(task, meta, dt, score)
```

### Query Optimization

```python
# Good: Use FTS5 for text search
results = db.search_memories_fts("keyword", limit=10)

# Avoid: LIKE queries on large tables
# results = db.execute_query("SELECT * FROM memories WHERE task LIKE '%keyword%'")
```

## Troubleshooting

### Slow FTS5 Searches

1. Check index exists:
    ```python
    result = db.execute_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='long_term_memories_fts'"
    )
    ```

2. Rebuild index if corrupted:
    ```python
    db.execute_update("INSERT INTO long_term_memories_fts(long_term_memories_fts) VALUES('rebuild')")
    ```

### Connection Pool Exhaustion

Increase pool size if seeing connection errors:

```python
db = AcceleratedSQLiteWrapper(db_path="db.db", pool_size=100)
```

### Database Locked

For high-concurrency, consider WAL mode:

```python
db.execute_update("PRAGMA journal_mode=WAL")
```

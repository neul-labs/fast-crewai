# Memory Acceleration

Fast-CrewAI provides high-performance memory storage with TF-IDF semantic search, replacing CrewAI's default memory implementations.

## Overview

| Feature | Description |
|---------|-------------|
| **Search Algorithm** | TF-IDF with cosine similarity |
| **Thread Safety** | Full thread safety with `Arc<Mutex<>>` |
| **Fallback** | Automatic Python fallback on errors |

## Basic Usage

```python
from fast_crewai import AcceleratedMemoryStorage

# Create storage with Rust acceleration
storage = AcceleratedMemoryStorage(use_rust=True)

# Save documents
storage.save("Machine learning is transforming industries")
storage.save("Deep learning models require large datasets")
storage.save("Natural language processing enables text analysis")

# Search using TF-IDF semantic similarity
results = storage.search("machine learning", limit=5)
for result in results:
    print(result)
```

## With CrewAI

When using the shim, CrewAI's memory systems are automatically accelerated:

```python
import fast_crewai.shim
from crewai import Agent, Task, Crew

# Memory is now accelerated automatically
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True  # Uses AcceleratedMemoryStorage
)
```

## Saving Data

### Basic Save

```python
storage.save("Your document content here")
```

### Save with Metadata

```python
storage.save(
    "Important research findings about AI",
    metadata={
        "source": "research_paper",
        "author": "Dr. Smith",
        "priority": "high"
    }
)
```

### Batch Saving

```python
documents = [
    "Document 1 content",
    "Document 2 content",
    "Document 3 content"
]

for doc in documents:
    storage.save(doc)
```

## Searching

### Basic Search

```python
results = storage.search("machine learning", limit=5)
```

### Search with Threshold

```python
results = storage.search(
    "artificial intelligence",
    limit=10,
    score_threshold=0.35  # Minimum similarity score
)
```

### Understanding Results

Results are ranked by TF-IDF cosine similarity:

```python
results = storage.search("neural networks", limit=3)
for i, result in enumerate(results):
    print(f"{i+1}. {result['value'][:50]}...")
    print(f"   Score: {result.get('score', 'N/A')}")
```

## TF-IDF Search Algorithm

Fast-CrewAI uses TF-IDF (Term Frequency-Inverse Document Frequency) with cosine similarity for semantic search:

1. **Term Frequency (TF)**: How often a term appears in a document
2. **Inverse Document Frequency (IDF)**: How unique a term is across all documents
3. **Cosine Similarity**: Measures the angle between query and document vectors

This provides better semantic matching than simple keyword matching.

## Other Operations

### Get All Items

```python
all_items = storage.get_all()
print(f"Total items: {len(all_items)}")
```

### Reset Storage

```python
storage.reset()
```

### Check Implementation

```python
print(f"Using: {storage.implementation}")  # "rust" or "python"
```

## Performance Tips

### Batch Operations

For large datasets, batch your operations:

```python
# Good - reuse storage instance
storage = AcceleratedMemoryStorage(use_rust=True)
for doc in large_dataset:
    storage.save(doc)

# Bad - creating new instances
for doc in large_dataset:
    storage = AcceleratedMemoryStorage()  # Don't do this!
    storage.save(doc)
```

### Optimal Batch Sizes

```python
batch_size = 1000
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    for doc in batch:
        storage.save(doc)
```

## Memory Usage

The Rust implementation uses efficient memory allocation:

| Operation | Python | Rust |
|-----------|--------|------|
| 10k documents | ~50 MB | ~10 MB |
| Search (1k queries) | ~5 MB temp | ~1 MB temp |

## Troubleshooting

### Slow Search Performance

If searches are slow with large datasets:

1. Check you're using Rust:
    ```python
    assert storage.implementation == "rust"
    ```

2. Consider reducing the search limit:
    ```python
    results = storage.search("query", limit=10)  # Instead of 100
    ```

### Memory Issues

For very large datasets:

```python
# Process in batches
batch_size = 10000
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    for doc in batch:
        storage.save(doc)
    # Optional: force garbage collection between batches
    import gc
    gc.collect()
```

### Fallback to Python

If you see "Using Python fallback" warnings:

1. Check Rust installation: `rustc --version`
2. Rebuild: `uv run maturin develop`
3. Check for errors in the build output

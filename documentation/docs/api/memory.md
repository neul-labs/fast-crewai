# AcceleratedMemoryStorage

High-performance memory storage with TF-IDF semantic search.

## Class Definition

```python
class AcceleratedMemoryStorage:
    def __init__(self, use_rust: Optional[bool] = None)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_rust` | `Optional[bool]` | `None` | Force Rust (`True`) or Python (`False`). If `None`, auto-detects. |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `implementation` | `str` | Returns `"rust"` or `"python"` |

## Methods

### save

Save a value to memory with optional metadata.

```python
def save(
    self,
    value: Any,
    metadata: Optional[Dict[str, Any]] = None
) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | `Any` | The value to save (will be serialized) |
| `metadata` | `Optional[Dict]` | Optional metadata dictionary |

**Example:**

```python
storage = AcceleratedMemoryStorage(use_rust=True)

# Basic save
storage.save("Important information about machine learning")

# Save with metadata
storage.save(
    "Research findings on neural networks",
    metadata={
        "source": "paper",
        "author": "Dr. Smith",
        "confidence": 0.95
    }
)
```

---

### search

Search memory using TF-IDF cosine similarity.

```python
def search(
    self,
    query: str,
    limit: int = 3,
    score_threshold: float = 0.35
) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | - | Search query |
| `limit` | `int` | `3` | Maximum results to return |
| `score_threshold` | `float` | `0.35` | Minimum similarity score |

**Returns:** `List[Dict[str, Any]]` - List of matching results with value, metadata, and timestamp.

**Example:**

```python
storage = AcceleratedMemoryStorage(use_rust=True)
storage.save("Machine learning is transforming industries")
storage.save("Deep learning requires large datasets")
storage.save("Python is a popular programming language")

# Search
results = storage.search("machine learning", limit=5)
for result in results:
    print(f"Value: {result['value']}")
    print(f"Metadata: {result.get('metadata', {})}")
    print(f"Timestamp: {result.get('timestamp')}")
```

---

### get_all

Get all items in memory.

```python
def get_all(self) -> List[Dict[str, Any]]
```

**Returns:** `List[Dict[str, Any]]` - All stored items.

**Example:**

```python
all_items = storage.get_all()
print(f"Total items: {len(all_items)}")
```

---

### reset

Clear all memory storage.

```python
def reset(self) -> None
```

**Example:**

```python
storage.reset()
assert len(storage.get_all()) == 0
```

## Complete Example

```python
from fast_crewai import AcceleratedMemoryStorage

# Create storage
storage = AcceleratedMemoryStorage(use_rust=True)
print(f"Using: {storage.implementation}")

# Save documents
documents = [
    ("AI is revolutionizing healthcare", {"domain": "healthcare"}),
    ("Machine learning predicts stock prices", {"domain": "finance"}),
    ("Deep learning enables image recognition", {"domain": "computer_vision"}),
    ("Natural language processing understands text", {"domain": "nlp"}),
]

for content, meta in documents:
    storage.save(content, meta)

# Search
results = storage.search("machine learning AI", limit=3)
print(f"\nSearch results for 'machine learning AI':")
for i, result in enumerate(results, 1):
    print(f"{i}. {result['value']}")

# Get all
all_docs = storage.get_all()
print(f"\nTotal documents: {len(all_docs)}")

# Reset
storage.reset()
print(f"After reset: {len(storage.get_all())} documents")
```

## Search Algorithm

The TF-IDF search algorithm works as follows:

1. **Term Frequency (TF)**: Counts how often each word appears in a document
2. **Inverse Document Frequency (IDF)**: Weights words by their rarity across all documents
3. **Cosine Similarity**: Computes the angle between query and document vectors

This provides semantic matching rather than exact keyword matching.

## Thread Safety

The Rust implementation uses `Arc<Mutex<>>` for full thread safety:

```python
from concurrent.futures import ThreadPoolExecutor
from fast_crewai import AcceleratedMemoryStorage

storage = AcceleratedMemoryStorage(use_rust=True)

def save_document(doc):
    storage.save(doc)

# Safe for concurrent access
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(save_document, documents)
```

## Fallback Behavior

If Rust fails, automatic fallback to Python occurs:

```python
storage = AcceleratedMemoryStorage(use_rust=True)

# If Rust initialization fails, falls back to Python
if storage.implementation == "python":
    print("Warning: Using Python fallback")
```

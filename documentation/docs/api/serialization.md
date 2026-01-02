# AgentMessage

Zero-copy JSON serialization using serde.

**Performance:** 34x faster serialization, 14x faster deserialization than Python json.

## Class Definition

```python
class AgentMessage:
    def __init__(
        self,
        id: str,
        sender: str,
        recipient: str,
        content: str,
        timestamp: int,
        use_rust: Optional[bool] = None
    )
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Unique message identifier |
| `sender` | `str` | Sender agent identifier |
| `recipient` | `str` | Recipient agent identifier |
| `content` | `str` | Message content |
| `timestamp` | `int` | Unix timestamp |
| `use_rust` | `Optional[bool]` | Force Rust or Python implementation |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Message identifier |
| `sender` | `str` | Sender identifier |
| `recipient` | `str` | Recipient identifier |
| `content` | `str` | Message content |
| `timestamp` | `int` | Unix timestamp |

## Methods

### to_json

Serialize message to JSON string.

```python
def to_json(self) -> str
```

**Returns:** `str` - JSON representation.

**Example:**

```python
message = AgentMessage(
    id="msg-001",
    sender="agent_1",
    recipient="agent_2",
    content="Analysis complete",
    timestamp=1700000000,
    use_rust=True
)

json_str = message.to_json()
print(json_str)
# {"id":"msg-001","sender":"agent_1","recipient":"agent_2","content":"Analysis complete","timestamp":1700000000}
```

---

### from_json (static)

Deserialize JSON string to AgentMessage.

```python
@staticmethod
def from_json(json_str: str, use_rust: Optional[bool] = None) -> AgentMessage
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `json_str` | `str` | - | JSON string to deserialize |
| `use_rust` | `Optional[bool]` | `None` | Force implementation |

**Returns:** `AgentMessage` - Deserialized message.

**Example:**

```python
json_str = '{"id":"msg-001","sender":"agent_1","recipient":"agent_2","content":"Hello!","timestamp":1700000000}'

message = AgentMessage.from_json(json_str, use_rust=True)
print(f"From: {message.sender}")
print(f"Content: {message.content}")
```

## Complete Example

```python
from fast_crewai import AgentMessage
import time

# Create messages
messages = []
for i in range(5):
    msg = AgentMessage(
        id=f"msg-{i:03d}",
        sender="researcher",
        recipient="analyst",
        content=f"Finding #{i}: Important discovery about AI",
        timestamp=int(time.time()) + i,
        use_rust=True
    )
    messages.append(msg)

# Serialize all
json_strings = []
for msg in messages:
    json_str = msg.to_json()
    json_strings.append(json_str)
    print(f"Serialized: {json_str[:50]}...")

# Deserialize all
restored = []
for json_str in json_strings:
    msg = AgentMessage.from_json(json_str, use_rust=True)
    restored.append(msg)
    print(f"Restored: {msg.id} from {msg.sender}")

# Verify
for orig, rest in zip(messages, restored):
    assert orig.id == rest.id
    assert orig.content == rest.content
print("\nAll messages verified!")
```

## Performance Comparison

```python
import json
import time
from fast_crewai import AgentMessage

data = {
    "id": "msg-001",
    "sender": "agent_1",
    "recipient": "agent_2",
    "content": "Test message " * 100,  # Large content
    "timestamp": 1700000000
}

iterations = 10000

# Python json
start = time.time()
for _ in range(iterations):
    json_str = json.dumps(data)
    restored = json.loads(json_str)
python_time = time.time() - start

# Rust serde
start = time.time()
for _ in range(iterations):
    msg = AgentMessage(**data, use_rust=True)
    json_str = msg.to_json()
    restored = AgentMessage.from_json(json_str, use_rust=True)
rust_time = time.time() - start

print(f"Python: {iterations/python_time:.0f} roundtrips/sec")
print(f"Rust: {iterations/rust_time:.0f} roundtrips/sec")
print(f"Speedup: {python_time/rust_time:.1f}x")
```

## JSON Format

The JSON output format:

```json
{
    "id": "msg-001",
    "sender": "agent_1",
    "recipient": "agent_2",
    "content": "Message content here",
    "timestamp": 1700000000
}
```

All fields are required and must be present for deserialization.

## Error Handling

### Serialization Errors

```python
try:
    json_str = message.to_json()
except Exception as e:
    print(f"Serialization failed: {e}")
```

### Deserialization Errors

```python
try:
    message = AgentMessage.from_json(invalid_json, use_rust=True)
except Exception as e:
    print(f"Deserialization failed: {e}")
```

### Validation

```python
def safe_deserialize(json_str: str) -> Optional[AgentMessage]:
    try:
        return AgentMessage.from_json(json_str, use_rust=True)
    except Exception:
        return None
```

## Why serde is Faster

1. **Zero-copy parsing**: Direct memory-to-JSON without intermediate objects
2. **No GIL**: Rust operates outside Python's Global Interpreter Lock
3. **SIMD**: Hardware-accelerated string processing where available
4. **Stack allocation**: Efficient memory usage for small messages
5. **No GC pressure**: Less Python object creation means less garbage collection

# Serialization Acceleration

Fast-CrewAI provides **34x faster** JSON serialization using serde, with 58% less memory usage.

## Overview

| Metric | Python json | Rust serde | Improvement |
|--------|-------------|------------|-------------|
| **Serialize** | 2,333 ops/s | 80,525 ops/s | 34x faster |
| **Deserialize** | 3,531 ops/s | 51,525 ops/s | 14x faster |
| **Memory** | 8.0 MB | 3.4 MB | 58% less |

## Basic Usage

```python
from fast_crewai import AgentMessage

# Create a message with Rust acceleration
message = AgentMessage(
    id="msg-001",
    sender="agent_1",
    recipient="agent_2",
    content="Analysis complete. Found 3 key insights.",
    timestamp=1700000000,
    use_rust=True
)

# Serialize to JSON (34x faster)
json_str = message.to_json()
print(json_str)

# Deserialize from JSON (14x faster)
restored = AgentMessage.from_json(json_str, use_rust=True)
print(f"Content: {restored.content}")
```

## AgentMessage Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique message identifier |
| `sender` | `str` | Sender agent identifier |
| `recipient` | `str` | Recipient agent identifier |
| `content` | `str` | Message content |
| `timestamp` | `int` | Unix timestamp |

## Serialization

```python
message = AgentMessage(
    id="msg-123",
    sender="researcher",
    recipient="analyst",
    content="Here are the research findings...",
    timestamp=1700000000,
    use_rust=True
)

# Fast serialization with serde
json_str = message.to_json()

# Output:
# {"id":"msg-123","sender":"researcher","recipient":"analyst","content":"Here are the research findings...","timestamp":1700000000}
```

## Deserialization

```python
json_str = '{"id":"msg-001","sender":"agent_1","recipient":"agent_2","content":"Hello!","timestamp":1700000000}'

# Fast deserialization with serde
message = AgentMessage.from_json(json_str, use_rust=True)

# Access fields
print(f"From: {message.sender}")
print(f"To: {message.recipient}")
print(f"Content: {message.content}")
```

## Batch Operations

For high-throughput scenarios:

```python
from fast_crewai import AgentMessage
import time

messages_data = [
    {"id": str(i), "sender": "agent", "recipient": "user",
     "content": f"Message {i}", "timestamp": i}
    for i in range(10000)
]

# Serialize many messages
start = time.time()
json_strings = []
for data in messages_data:
    msg = AgentMessage(**data, use_rust=True)
    json_strings.append(msg.to_json())

elapsed = time.time() - start
print(f"Serialized {len(messages_data)} messages in {elapsed:.3f}s")
print(f"Throughput: {len(messages_data)/elapsed:.0f} msgs/sec")
```

## Performance Comparison

```python
import json
import time
from fast_crewai import AgentMessage

# Test data
data = {
    "id": "msg-001",
    "sender": "agent_1",
    "recipient": "agent_2",
    "content": "Test message content " * 100,
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

print(f"Python: {iterations/python_time:.0f} ops/sec")
print(f"Rust: {iterations/rust_time:.0f} ops/sec")
print(f"Speedup: {python_time/rust_time:.1f}x")
```

## Why serde is Faster

1. **Zero-copy parsing**: Parses JSON directly without intermediate objects
2. **No GIL contention**: Rust code runs without Python's Global Interpreter Lock
3. **SIMD operations**: Hardware-accelerated string processing
4. **Efficient memory**: Stack allocation where possible

## Best Practices

### Use for High-Volume Messaging

```python
# Good: Use for agent communication
for event in event_stream:
    msg = AgentMessage(
        id=str(uuid.uuid4()),
        sender=agent_id,
        recipient=target_id,
        content=event.data,
        timestamp=int(time.time()),
        use_rust=True
    )
    queue.put(msg.to_json())
```

### Reuse Message Patterns

```python
# Create template and modify
def create_message(content: str) -> str:
    msg = AgentMessage(
        id=str(uuid.uuid4()),
        sender="system",
        recipient="user",
        content=content,
        timestamp=int(time.time()),
        use_rust=True
    )
    return msg.to_json()
```

### Validate Before Deserializing

```python
def safe_deserialize(json_str: str) -> Optional[AgentMessage]:
    try:
        return AgentMessage.from_json(json_str, use_rust=True)
    except Exception as e:
        print(f"Invalid message: {e}")
        return None
```

## Troubleshooting

### Serialization Errors

If `to_json()` fails:

1. Check all fields are provided:
    ```python
    # All fields are required
    msg = AgentMessage(
        id="...",      # Required
        sender="...",  # Required
        recipient="...",  # Required
        content="...",    # Required
        timestamp=123,    # Required
        use_rust=True
    )
    ```

2. Ensure content is valid UTF-8 string

### Deserialization Errors

If `from_json()` fails:

1. Verify JSON structure:
    ```python
    import json
    try:
        parsed = json.loads(json_str)
        print(f"Keys: {parsed.keys()}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
    ```

2. Check all required fields are present

### Performance Not as Expected

Verify Rust is being used:

```python
msg = AgentMessage("1", "a", "b", "c", 123, use_rust=True)

# Check if using Rust implementation
# (Implementation details depend on internal structure)
```

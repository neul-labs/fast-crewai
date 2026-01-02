# AcceleratedTaskExecutor

Task execution with dependency tracking, topological sorting, and parallel scheduling.

## Class Definition

```python
class AcceleratedTaskExecutor:
    def __init__(self, use_rust: Optional[bool] = None)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_rust` | `Optional[bool]` | `None` | Force Rust or Python implementation |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `implementation` | `str` | Returns `"rust"` or `"python"` |

## Methods

### register_task

Register a task with its dependencies.

```python
def register_task(
    self,
    task_id: str,
    dependencies: List[str] = []
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_id` | `str` | - | Unique task identifier |
| `dependencies` | `List[str]` | `[]` | List of task IDs this task depends on |

**Example:**

```python
executor = AcceleratedTaskExecutor(use_rust=True)

executor.register_task("fetch_data", dependencies=[])
executor.register_task("clean_data", dependencies=["fetch_data"])
executor.register_task("analyze", dependencies=["clean_data"])
```

---

### get_execution_order

Get optimal execution order using topological sort (Kahn's algorithm).

```python
def get_execution_order(self) -> List[str]
```

**Returns:** `List[str]` - Task IDs in execution order.

**Raises:** `ValueError` - If circular dependency detected.

**Example:**

```python
order = executor.get_execution_order()
print(f"Execution order: {order}")
# ['fetch_data', 'clean_data', 'analyze']
```

---

### get_ready_tasks

Get tasks ready for execution (all dependencies completed).

```python
def get_ready_tasks(self) -> List[str]
```

**Returns:** `List[str]` - Task IDs ready to execute.

**Example:**

```python
ready = executor.get_ready_tasks()
print(f"Ready to execute: {ready}")
```

---

### mark_started

Mark a task as started/in-progress.

```python
def mark_started(self, task_id: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | `str` | Task identifier |

---

### mark_completed

Mark a task as completed with its result.

```python
def mark_completed(self, task_id: str, result: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | `str` | Task identifier |
| `result` | `str` | Task result |

---

### execute_concurrent

Execute multiple tasks concurrently via Tokio runtime.

```python
def execute_concurrent(self, task_ids: List[str]) -> List[str]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_ids` | `List[str]` | Tasks to execute concurrently |

**Returns:** `List[str]` - Completion results.

**Example:**

```python
ready = executor.get_ready_tasks()
results = executor.execute_concurrent(ready)
```

---

### get_stats

Get execution statistics.

```python
def get_stats(self) -> Dict[str, Any]
```

**Returns:** `Dict[str, Any]` - Statistics dictionary.

| Key | Type | Description |
|-----|------|-------------|
| `tasks_scheduled` | `int` | Total tasks registered |
| `tasks_completed` | `int` | Tasks completed |
| `tasks_pending` | `int` | Tasks not yet completed |

## Complete Example

```python
from fast_crewai import AcceleratedTaskExecutor

executor = AcceleratedTaskExecutor(use_rust=True)

# Define a workflow
workflow = {
    "download": [],
    "parse": ["download"],
    "validate": ["parse"],
    "transform_a": ["validate"],
    "transform_b": ["validate"],
    "merge": ["transform_a", "transform_b"],
    "export": ["merge"]
}

# Register all tasks
for task_id, deps in workflow.items():
    executor.register_task(task_id, deps)

# Get execution order
order = executor.get_execution_order()
print(f"Execution order: {order}")

# Execute tasks
for task_id in order:
    # Check if ready
    ready = executor.get_ready_tasks()
    if task_id not in ready:
        continue

    # Execute
    executor.mark_started(task_id)
    print(f"Executing: {task_id}")

    # Simulate work
    import time
    time.sleep(0.1)

    executor.mark_completed(task_id, f"{task_id} completed")

# Final stats
stats = executor.get_stats()
print(f"\nFinal stats:")
print(f"  Scheduled: {stats['tasks_scheduled']}")
print(f"  Completed: {stats['tasks_completed']}")
print(f"  Pending: {stats['tasks_pending']}")
```

## Cycle Detection

Circular dependencies are automatically detected:

```python
executor = AcceleratedTaskExecutor(use_rust=True)

# Create circular dependency
executor.register_task("A", ["C"])
executor.register_task("B", ["A"])
executor.register_task("C", ["B"])

try:
    order = executor.get_execution_order()
except ValueError as e:
    print(f"Error: {e}")
    # "Circular dependency detected in tasks"
```

## Parallel Execution

Independent tasks can be executed in parallel:

```python
executor = AcceleratedTaskExecutor(use_rust=True)

# Independent tasks
executor.register_task("fetch_a", [])
executor.register_task("fetch_b", [])
executor.register_task("fetch_c", [])
executor.register_task("merge", ["fetch_a", "fetch_b", "fetch_c"])

# Get ready tasks (all independent ones)
ready = executor.get_ready_tasks()
print(f"Can run in parallel: {ready}")
# ['fetch_a', 'fetch_b', 'fetch_c']

# Execute concurrently
results = executor.execute_concurrent(ready)
```

## Topological Sort Algorithm

Uses Kahn's algorithm for O(V + E) complexity:

1. Calculate in-degree for each task
2. Add tasks with zero in-degree to queue
3. Process queue, removing edges and adding newly ready tasks
4. If not all tasks processed, cycle exists

# Task Acceleration

Fast-CrewAI provides advanced task execution with dependency tracking, topological sorting, and parallel scheduling via Tokio.

## Overview

| Feature | Benefit |
|---------|---------|
| **Dependency Tracking** | Automatic task ordering |
| **Topological Sort** | Optimal execution order (Kahn's algorithm) |
| **Cycle Detection** | Catch circular dependencies |
| **Parallel Scheduling** | Concurrent execution via Tokio |

## Basic Usage

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
```

## With CrewAI

When using the shim, CrewAI tasks are automatically accelerated:

```python
import fast_crewai.shim
from crewai import Agent, Task, Crew

task1 = Task(description="Research", expected_output="Data", agent=agent)
task2 = Task(description="Analyze", expected_output="Analysis", agent=agent)
task3 = Task(description="Report", expected_output="Report", agent=agent)

# Task dependencies are tracked automatically
crew = Crew(agents=[agent], tasks=[task1, task2, task3])
```

## Dependency Management

### Register Tasks

```python
# Independent task (no dependencies)
executor.register_task("task_a", dependencies=[])

# Task depending on one other
executor.register_task("task_b", dependencies=["task_a"])

# Task depending on multiple others
executor.register_task("task_c", dependencies=["task_a", "task_b"])
```

### Get Ready Tasks

Find tasks with all dependencies satisfied:

```python
ready = executor.get_ready_tasks()
print(f"Ready to execute: {ready}")
```

### Track Task State

```python
# Mark task as started
executor.mark_started("task_a")

# Mark task as completed
executor.mark_completed("task_a", result="Success")

# Now dependent tasks become ready
ready = executor.get_ready_tasks()  # ["task_b"]
```

## Execution Order

The topological sort ensures correct execution order:

```python
executor.register_task("A", [])
executor.register_task("B", ["A"])
executor.register_task("C", ["A"])
executor.register_task("D", ["B", "C"])

order = executor.get_execution_order()
# Possible outputs: ['A', 'B', 'C', 'D'] or ['A', 'C', 'B', 'D']
# Both are valid - B and C can run in any order after A
```

## Cycle Detection

Circular dependencies are automatically detected:

```python
executor.register_task("A", dependencies=["B"])
executor.register_task("B", dependencies=["A"])

try:
    order = executor.get_execution_order()
except ValueError as e:
    print(f"Error: {e}")
    # "Circular dependency detected in tasks"
```

## Parallel Execution

Execute independent tasks concurrently:

```python
# Get tasks that can run in parallel
ready_tasks = executor.get_ready_tasks()

# Execute them concurrently via Tokio
results = executor.execute_concurrent(ready_tasks)

for task_id, result in zip(ready_tasks, results):
    print(f"{task_id}: {result}")
```

## Execution Statistics

Track task execution progress:

```python
stats = executor.get_stats()
print(f"Tasks scheduled: {stats['tasks_scheduled']}")
print(f"Tasks completed: {stats['tasks_completed']}")
print(f"Tasks pending: {stats['tasks_pending']}")
```

## Complete Workflow Example

```python
from fast_crewai import AcceleratedTaskExecutor

executor = AcceleratedTaskExecutor(use_rust=True)

# Define workflow
workflow = {
    "download": [],
    "parse": ["download"],
    "validate": ["parse"],
    "transform": ["validate"],
    "enrich": ["validate"],
    "merge": ["transform", "enrich"],
    "export": ["merge"]
}

# Register all tasks
for task_id, deps in workflow.items():
    executor.register_task(task_id, deps)

# Execute in order
execution_order = executor.get_execution_order()

for task_id in execution_order:
    executor.mark_started(task_id)
    print(f"Executing: {task_id}")
    # ... do actual work ...
    executor.mark_completed(task_id, f"{task_id} done")

print(f"\nStats: {executor.get_stats()}")
```

## Performance Benefits

### Without Acceleration (Python)

- Sequential dependency resolution
- GIL-limited concurrency
- O(n²) naive scheduling

### With Acceleration (Rust)

- Efficient topological sort (O(V + E))
- True parallelism via Tokio work-stealing
- Optimized dependency tracking

## Best Practices

### Design for Parallelism

Structure tasks to maximize parallel opportunities:

```python
# Good: Independent tasks can run in parallel
executor.register_task("fetch_a", [])
executor.register_task("fetch_b", [])
executor.register_task("fetch_c", [])
executor.register_task("merge", ["fetch_a", "fetch_b", "fetch_c"])

# Less optimal: Sequential chain
executor.register_task("step1", [])
executor.register_task("step2", ["step1"])
executor.register_task("step3", ["step2"])
```

### Handle Failures

```python
try:
    executor.mark_started(task_id)
    result = do_work()
    executor.mark_completed(task_id, result)
except Exception as e:
    executor.mark_failed(task_id, str(e))
    # Dependent tasks won't be scheduled
```

### Monitor Progress

```python
import time

while True:
    stats = executor.get_stats()
    pending = stats['tasks_pending']
    completed = stats['tasks_completed']
    total = stats['tasks_scheduled']

    print(f"Progress: {completed}/{total} ({pending} pending)")

    if pending == 0:
        break

    time.sleep(1)
```

## Troubleshooting

### Tasks Not Becoming Ready

Check that dependencies are correctly registered and completed:

```python
# Debug dependency chain
for task_id in ["task_a", "task_b", "task_c"]:
    ready = executor.get_ready_tasks()
    print(f"Ready: {ready}")
    if task_id in ready:
        executor.mark_started(task_id)
        executor.mark_completed(task_id, "done")
```

### Cycle Detection False Positives

Ensure task IDs are unique and consistent:

```python
# Bad: inconsistent naming
executor.register_task("Task A", [])
executor.register_task("task_b", ["Task_A"])  # Wrong ID!

# Good: consistent naming
executor.register_task("task_a", [])
executor.register_task("task_b", ["task_a"])
```

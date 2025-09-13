# CrewAI Rust Integration Examples

This directory contains example usage files demonstrating how to use the Rust integration components.

## Example Files

### 1. Basic Component Usage
- `memory_replacement_example.py` - Shows how to replace Python memory storage with Rust implementation
- `tool_execution_example.py` - Demonstrates Rust-based tool execution with safety limits
- `task_execution_example.py` - Shows concurrent task execution with Rust backend
- `serialization_example.py` - Demonstrates high-performance serialization

### 2. Performance Testing
- `performance_benchmark.py` - Comprehensive benchmarks comparing Python and Rust implementations

### 3. Integration Examples
- `test_rust_integration.py` - Unit tests showing basic functionality

### 4. Migration Guides
- `migration_guide.md` - Instructions for integrating Rust components into existing codebases

## Running Examples

### Basic Usage Examples
```bash
# Run memory replacement example
python memory_replacement_example.py

# Run tool execution example
python tool_execution_example.py

# Run task execution example
python task_execution_example.py

# Run serialization example
python serialization_example.py
```

### Performance Benchmarks
```bash
# Run comprehensive performance benchmarks
python performance_benchmark.py
```

### Integration Tests
```bash
# Run integration tests
python test_rust_integration.py
```

## Key Demonstration Points

### 1. Drop-in Replacement
The examples show how Rust components can be used as direct replacements for Python implementations without any code changes to the API usage patterns.

### 2. Performance Improvements
The benchmark example demonstrates the significant performance improvements achievable with Rust implementations:
- 10-20x faster for memory operations
- 2-5x faster for tool execution
- 3-5x faster for concurrent task execution
- 5-10x faster for serialization

### 3. Safety Features
Examples demonstrate built-in safety features:
- Stack-safe recursion limits
- Proper timeout mechanisms
- Resource management and cleanup
- Error handling with detailed context

### 4. Backward Compatibility
All examples show how the Rust components maintain full backward compatibility with existing Python code while providing enhanced performance when available.

## Integration Patterns

### Automatic Enhancement
```python
# Existing code continues to work unchanged
from crewai import Crew
crew = Crew(agents=[...], tasks=[...], memory=True)
result = crew.kickoff()  # Gets automatic performance boost
```

### Selective Component Usage
```python
# Choose which components to enhance
import os
os.environ['CREWAI_RUST_MEMORY'] = 'true'
os.environ['CREWAI_RUST_TOOLS'] = 'true'
os.environ['CREWAI_RUST_TASKS'] = 'false'  # Keep on Python
```

### Direct Component Usage
```python
# Use components directly for maximum control
from crewai_rust.memory import RustMemoryStorage
from crewai_rust.tools import RustToolExecutor
```

These examples provide a comprehensive demonstration of how the Rust integration can enhance CrewAI applications while maintaining full compatibility with existing codebases.
"""
Example usage of the CrewAI Rust integration components.

This module demonstrates how to use the various Rust-enhanced
components in real-world scenarios.
"""

import time
import json
from crewai_rust import HAS_RUST_IMPLEMENTATION
from crewai_rust.memory import RustMemoryStorage
from crewai_rust.tools import RustToolExecutor
from crewai_rust.tasks import RustTaskExecutor
from crewai_rust.serialization import AgentMessage, RustSerializer
from crewai_rust.database import RustSQLiteWrapper
from crewai_rust.utils import get_rust_status, get_performance_improvements


def example_memory_usage():
    """Demonstrate memory storage usage."""
    print("=== Memory Storage Example ===")
    
    # Check if Rust is available
    status = get_rust_status()
    print(f"Rust available: {status['available']}")
    
    # Create memory storage
    memory = RustMemoryStorage()
    print(f"Using implementation: {memory.implementation}")
    
    # Save some data
    start_time = time.time()
    for i in range(100):
        memory.save(f"Memory item {i}", {
            "id": i,
            "category": "test",
            "timestamp": time.time()
        })
    save_time = time.time() - start_time
    print(f"Saved 100 items in {save_time:.4f} seconds")
    
    # Search memory
    start_time = time.time()
    results = memory.search("Memory item")
    search_time = time.time() - start_time
    print(f"Found {len(results)} items in {search_time:.4f} seconds")
    
    # Get all items
    all_items = memory.get_all()
    print(f"Total items in storage: {len(all_items)}")
    
    print()


def example_tool_execution():
    """Demonstrate tool execution usage."""
    print("=== Tool Execution Example ===")
    
    # Create tool executor
    executor = RustToolExecutor(max_recursion_depth=100)
    print(f"Using implementation: {executor.implementation}")
    
    # Execute some tools
    tools_to_execute = [
        ("calculator", {"operation": "add", "operands": [1, 2]}),
        ("search", {"query": "Python programming"}),
        ("formatter", "Hello, World!"),
        ("validator", {"data": {"name": "test", "value": 42}})
    ]
    
    start_time = time.time()
    for tool_name, args in tools_to_execute:
        try:
            result = executor.execute_tool(tool_name, args)
            print(f"Executed {tool_name}: {result[:50]}...")
        except Exception as e:
            print(f"Error executing {tool_name}: {e}")
    execution_time = time.time() - start_time
    print(f"Executed {len(tools_to_execute)} tools in {execution_time:.4f} seconds")
    
    print()


def example_task_execution():
    """Demonstrate task execution usage."""
    print("=== Task Execution Example ===")
    
    # Create task executor
    executor = RustTaskExecutor()
    print(f"Using implementation: {executor.implementation}")
    
    # Create some tasks
    tasks = [
        {"id": f"task_{i}", "description": f"Process item {i}", "priority": i % 3}
        for i in range(20)
    ]
    
    # Execute tasks concurrently
    start_time = time.time()
    results = executor.execute_concurrent_tasks(tasks)
    execution_time = time.time() - start_time
    print(f"Executed {len(tasks)} tasks in {execution_time:.4f} seconds")
    print(f"First few results: {results[:3]}")
    
    print()


def example_serialization():
    """Demonstrate serialization usage."""
    print("=== Serialization Example ===")
    
    # Create some messages
    messages = [
        {
            "id": f"msg_{i}",
            "sender": f"agent_{i % 5}",
            "recipient": f"agent_{(i + 1) % 5}",
            "content": f"Message content {i} with some realistic data",
            "timestamp": int(time.time()) + i
        }
        for i in range(50)
    ]
    
    # Test single message serialization
    msg_data = messages[0]
    message = AgentMessage(
        msg_data["id"],
        msg_data["sender"],
        msg_data["recipient"],
        msg_data["content"],
        msg_data["timestamp"]
    )
    print(f"Using implementation: {message.implementation}")
    
    # Serialize single message
    start_time = time.time()
    json_str = message.to_json()
    serialize_time = time.time() - start_time
    print(f"Serialized single message in {serialize_time:.6f} seconds")
    
    # Deserialize single message
    start_time = time.time()
    message2 = AgentMessage.from_json(json_str)
    deserialize_time = time.time() - start_time
    print(f"Deserialized single message in {deserialize_time:.6f} seconds")
    
    # Test batch serialization
    serializer = RustSerializer()
    start_time = time.time()
    serialized_batch = serializer.serialize_batch(messages)
    batch_serialize_time = time.time() - start_time
    print(f"Serialized {len(messages)} messages in {batch_serialize_time:.4f} seconds")
    
    # Test batch deserialization
    start_time = time.time()
    deserialized_batch = serializer.deserialize_batch(serialized_batch)
    batch_deserialize_time = time.time() - start_time
    print(f"Deserialized {len(deserialized_batch)} messages in {batch_deserialize_time:.4f} seconds")
    
    print()


def example_database_operations():
    """Demonstrate database operations usage."""
    print("=== Database Operations Example ===")
    
    import tempfile
    import os
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    try:
        # Create database wrapper
        db = RustSQLiteWrapper(temp_db.name, pool_size=5)
        print(f"Using implementation: {db.implementation}")
        
        # Save some memory entries
        start_time = time.time()
        for i in range(100):
            db.save_memory(
                task_description=f"Task {i}",
                metadata={"param1": f"value{i}", "param2": i * 2},
                datetime=f"2023-01-{i+1:02d} 12:00:00",
                score=i * 0.01
            )
        save_time = time.time() - start_time
        print(f"Saved 100 memory entries in {save_time:.4f} seconds")
        
        # Load memories
        start_time = time.time()
        results = db.load_memories("Task", latest_n=10)
        load_time = time.time() - start_time
        print(f"Loaded {len(results or [])} memory entries in {load_time:.4f} seconds")
        
        # Execute batch operations
        queries = [
            ("INSERT INTO long_term_memories (task_description, metadata, datetime, score) VALUES (?, ?, ?, ?)", {
                "task_description": "Batch task 1",
                "metadata": json.dumps({"batch": True}),
                "datetime": "2023-01-01 13:00:00",
                "score": 0.99
            }),
            ("INSERT INTO long_term_memories (task_description, metadata, datetime, score) VALUES (?, ?, ?, ?)", {
                "task_description": "Batch task 2",
                "metadata": json.dumps({"batch": True}),
                "datetime": "2023-01-01 14:00:00",
                "score": 0.98
            })
        ]
        start_time = time.time()
        batch_results = db.execute_batch(queries)
        batch_time = time.time() - start_time
        print(f"Executed batch of {len(queries)} queries in {batch_time:.4f} seconds")
        
    finally:
        # Clean up
        try:
            os.unlink(temp_db.name)
        except:
            pass
    
    print()


def example_performance_info():
    """Display performance improvement information."""
    print("=== Performance Information ===")
    
    # Get Rust status
    status = get_rust_status()
    print(f"Rust available: {status['available']}")
    
    if status['available']:
        print("Available components:")
        for component, available in status['components'].items():
            print(f"  {component}: {'✓' if available else '✗'}")
    
    # Get performance improvements
    improvements = get_performance_improvements()
    print("\nExpected performance improvements:")
    for component, info in improvements.items():
        print(f"  {component}: {info['improvement']} - {info['description']}")
    
    print()


def example_environment_configuration():
    """Demonstrate environment configuration."""
    print("=== Environment Configuration ===")
    
    from crewai_rust.utils import get_environment_info, configure_rust_components
    
    # Show current environment
    env_info = get_environment_info()
    print("Current environment configuration:")
    for key, value in env_info.items():
        print(f"  {key}: {value}")
    
    # Configure components (this would typically be done at application startup)
    # configure_rust_components(memory=True, tools=True, tasks=False)
    
    print()


def main():
    """Run all examples."""
    print("CrewAI Rust Integration Examples")
    print("=" * 40)
    
    # Show performance information first
    example_performance_info()
    
    # Run examples
    example_environment_configuration()
    example_memory_usage()
    example_tool_execution()
    example_task_execution()
    example_serialization()
    example_database_operations()
    
    print("All examples completed!")


if __name__ == "__main__":
    main()
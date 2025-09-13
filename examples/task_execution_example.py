# Example: Replacing Python Task Execution with Rust Implementation

# This example shows how we could replace the existing Python task execution
# system with a high-performance Rust implementation

from crewai_rust import RustTaskExecutor
import time
import asyncio

class RustTaskExecutorWrapper:
    """
    A high-performance concurrent task executor using Rust backend
    """
    
    def __init__(self):
        # Initialize the Rust task executor
        self._rust_executor = RustTaskExecutor()
        self.execution_times = []
    
    def execute_tasks_concurrently(self, tasks):
        """
        Execute multiple tasks concurrently using the Rust backend
        """
        start_time = time.time()
        
        try:
            # Execute tasks using the Rust backend
            # Convert tasks to string format for Rust
            task_strings = [str(task) for task in tasks]
            results = self._rust_executor.execute_concurrent_tasks(task_strings)
            
            # Track execution time
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)
            
            return results
            
        except Exception as e:
            raise Exception(f"Concurrent task execution failed: {str(e)}")
    
    async def execute_tasks_concurrently_async(self, tasks):
        """
        Execute multiple tasks concurrently using the Rust backend (async version)
        """
        # For this example, we'll just call the sync version
        # In a real implementation, we might want to use asyncio.to_thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_tasks_concurrently, tasks)
    
    def execute_task_with_timeout(self, task, timeout_seconds=30):
        """
        Execute a single task with a timeout
        """
        # In a full implementation, we would use the Rust backend's timeout features
        # For now, we'll simulate this with a simple approach
        start_time = time.time()
        
        try:
            # Execute using the Rust backend
            result = self._rust_executor.execute_concurrent_tasks([str(task)])
            
            # Check if we exceeded the timeout
            execution_time = time.time() - start_time
            if execution_time > timeout_seconds:
                raise Exception(f"Task execution timed out after {timeout_seconds} seconds")
            
            self.execution_times.append(execution_time)
            
            # Return the first (and only) result
            return result[0] if result else None
            
        except Exception as e:
            raise Exception(f"Task execution failed: {str(e)}")
    
    def get_average_execution_time(self):
        """
        Get the average execution time for task executions so far
        """
        if not self.execution_times:
            return 0
        return sum(self.execution_times) / len(self.execution_times)
    
    def get_execution_stats(self):
        """
        Get detailed execution statistics
        """
        if not self.execution_times:
            return {"total_executions": 0, "average_time": 0, "min_time": 0, "max_time": 0}
        
        return {
            "total_executions": len(self.execution_times),
            "average_time": sum(self.execution_times) / len(self.execution_times),
            "min_time": min(self.execution_times),
            "max_time": max(self.execution_times)
        }

# Example usage:
if __name__ == "__main__":
    # Create a Rust-backed task executor
    executor = RustTaskExecutorWrapper()
    
    # Create some test tasks
    tasks = [
        "Task 1: Calculate 2 + 2",
        "Task 2: Search for 'Python programming'",
        "Task 3: Format 'Hello, World!'",
        "Task 4: Generate a random number",
        "Task 5: Check system status"
    ]
    
    # Execute tasks concurrently
    print("Executing tasks concurrently...")
    start_time = time.time()
    results = executor.execute_tasks_concurrently(tasks)
    end_time = time.time()
    
    print(f"Executed {len(tasks)} tasks in {end_time - start_time:.2f} seconds")
    for i, result in enumerate(results):
        print(f"Task {i+1} result: {result}")
    
    # Print execution statistics
    stats = executor.get_execution_stats()
    print(f"\nExecution statistics: {stats}")
    
    # Test single task with timeout
    print("\nTesting single task with timeout...")
    try:
        result = executor.execute_task_with_timeout("Single task test", timeout_seconds=5)
        print(f"Single task result: {result}")
    except Exception as e:
        print(f"Single task error: {e}")
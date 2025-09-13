# Example: Replacing Python Tool Execution with Rust Implementation

# This example shows how we could replace the existing Python tool execution
# system with a high-performance Rust implementation

from crewai_rust import RustToolExecutor
import time

class RustToolExecutorWrapper:
    """
    A drop-in replacement for CrewAI's tool execution using Rust backend
    """
    
    def __init__(self, max_recursion_depth=100, timeout_seconds=30):
        # Initialize the Rust tool executor
        self._rust_executor = RustToolExecutor(max_recursion_depth)
        self.timeout_seconds = timeout_seconds
        self.execution_times = []
    
    def execute_tool(self, tool_name, arguments):
        """
        Execute a tool using the Rust backend with safety limits
        """
        start_time = time.time()
        
        try:
            # Convert arguments to string format for Rust
            import json
            args_str = json.dumps(arguments) if isinstance(arguments, (dict, list)) else str(arguments)
            
            # Execute using the Rust backend
            result = self._rust_executor.execute_tool(tool_name, args_str)
            
            # Track execution time
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)
            
            # Convert result back to Python object if it's JSON
            try:
                import json
                return json.loads(result)
            except:
                return result
                
        except RuntimeError as e:
            # Handle recursion limit exceeded
            if "Maximum recursion depth exceeded" in str(e):
                raise Exception(f"Tool execution failed: Maximum recursion depth exceeded for tool '{tool_name}'")
            else:
                raise Exception(f"Tool execution failed: {str(e)}")
    
    def get_average_execution_time(self):
        """
        Get the average execution time for tools executed so far
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
    # Create a Rust-backed tool executor
    executor = RustToolExecutorWrapper(max_recursion_depth=5)
    
    # Execute some tools
    try:
        result1 = executor.execute_tool("calculator", {"operation": "add", "operands": [2, 3]})
        print(f"Result 1: {result1}")
        
        result2 = executor.execute_tool("search", {"query": "Python programming"})
        print(f"Result 2: {result2}")
        
        result3 = executor.execute_tool("formatter", "Hello, World!")
        print(f"Result 3: {result3}")
        
        # Print execution statistics
        stats = executor.get_execution_stats()
        print(f"Execution statistics: {stats}")
        
        # Test recursion limit
        print("Testing recursion limit...")
        for i in range(10):
            try:
                result = executor.execute_tool(f"recursive_tool_{i}", {"depth": i})
                print(f"Recursive tool {i} result: {result}")
            except Exception as e:
                print(f"Recursion limit caught at iteration {i}: {e}")
                break
                
    except Exception as e:
        print(f"Error: {e}")
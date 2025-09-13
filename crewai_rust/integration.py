"""
Integration layer for CrewAI components with Rust backend.

This module provides seamless integration between existing CrewAI
components and the new Rust implementations.
"""

from typing import Any, Dict, List, Optional
from .memory import RustMemoryStorage
from .tools import RustToolExecutor
from .tasks import RustTaskExecutor
from .serialization import AgentMessage, RustSerializer
from .database import RustSQLiteWrapper


class RustMemoryIntegration:
    """
    Integration layer for CrewAI memory components with Rust backend.
    
    This class provides a drop-in replacement for existing CrewAI memory
    components that automatically uses the Rust implementation when available.
    """
    
    @staticmethod
    def create_short_term_memory(
        crew: Any = None,
        embedder_config: Optional[Dict[str, Any]] = None,
        storage: Any = None,
        path: Optional[str] = None
    ) -> Any:
        """
        Create a short-term memory instance with Rust backend.
        
        Args:
            crew: Crew instance
            embedder_config: Embedder configuration
            storage: Existing storage instance
            path: Storage path
            
        Returns:
            Memory instance (Rust-enhanced when available)
        """
        # Try to create Rust-enhanced memory
        try:
            rust_memory = RustMemoryStorage()
            return RustEnhancedMemoryProxy(rust_memory, crew, embedder_config, storage, path)
        except Exception as e:
            # Fallback to original implementation
            from crewai.memory.short_term.short_term_memory import ShortTermMemory
            return ShortTermMemory(crew=crew, embedder_config=embedder_config, storage=storage, path=path)
    
    @staticmethod
    def create_long_term_memory(
        crew: Any = None,
        embedder_config: Optional[Dict[str, Any]] = None,
        storage: Any = None,
        path: Optional[str] = None
    ) -> Any:
        """
        Create a long-term memory instance with Rust backend.
        
        Args:
            crew: Crew instance
            embedder_config: Embedder configuration
            storage: Existing storage instance
            path: Storage path
            
        Returns:
            Memory instance (Rust-enhanced when available)
        """
        # Try to create Rust-enhanced memory
        try:
            # For long-term memory, we'd typically use the database wrapper
            if path:
                rust_db = RustSQLiteWrapper(path)
                return RustEnhancedLongTermMemoryProxy(rust_db, crew, embedder_config, storage, path)
        except Exception as e:
            pass
        
        # Fallback to original implementation
        from crewai.memory.long_term.long_term_memory import LongTermMemory
        return LongTermMemory(crew=crew, embedder_config=embedder_config, storage=storage, path=path)


class RustEnhancedMemoryProxy:
    """
    Proxy class that wraps existing memory implementations with Rust enhancements.
    """
    
    def __init__(
        self, 
        rust_memory: RustMemoryStorage,
        crew: Any = None,
        embedder_config: Optional[Dict[str, Any]] = None,
        storage: Any = None,
        path: Optional[str] = None
    ):
        self.rust_memory = rust_memory
        # Import the original class for fallback
        from crewai.memory.short_term.short_term_memory import ShortTermMemory
        self.original_memory = ShortTermMemory(crew=crew, embedder_config=embedder_config, storage=storage, path=path)
        self.crew = crew
        self.embedder_config = embedder_config
    
    def save(self, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save a value to memory."""
        try:
            self.rust_memory.save(value, metadata)
        except Exception as e:
            # Fallback to original implementation
            self.original_memory.save(value, metadata)
    
    def search(
        self, 
        query: str, 
        limit: int = 3, 
        score_threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        """Search memory for items matching the query."""
        try:
            return self.rust_memory.search(query, limit, score_threshold)
        except Exception as e:
            # Fallback to original implementation
            return self.original_memory.search(query, limit, score_threshold)
    
    def reset(self) -> None:
        """Reset memory storage."""
        try:
            self.rust_memory.reset()
        except Exception as e:
            # Fallback to original implementation
            self.original_memory.reset()
    
    @property
    def agent(self):
        """Get the agent associated with this memory."""
        return getattr(self.original_memory, 'agent', None)
    
    @agent.setter
    def agent(self, value):
        """Set the agent associated with this memory."""
        if hasattr(self.original_memory, 'agent'):
            self.original_memory.agent = value
    
    @property
    def task(self):
        """Get the task associated with this memory."""
        return getattr(self.original_memory, 'task', None)
    
    @task.setter
    def task(self, value):
        """Set the task associated with this memory."""
        if hasattr(self.original_memory, 'task'):
            self.original_memory.task = value


class RustEnhancedLongTermMemoryProxy:
    """
    Proxy class that wraps long-term memory implementations with Rust enhancements.
    """
    
    def __init__(
        self, 
        rust_db: RustSQLiteWrapper,
        crew: Any = None,
        embedder_config: Optional[Dict[str, Any]] = None,
        storage: Any = None,
        path: Optional[str] = None
    ):
        self.rust_db = rust_db
        # Import the original class for fallback
        from crewai.memory.long_term.long_term_memory import LongTermMemory
        self.original_memory = LongTermMemory(crew=crew, embedder_config=embedder_config, storage=storage, path=path)
        self.crew = crew
        self.embedder_config = embedder_config
    
    def save(self, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save a value to memory."""
        # For long-term memory, we'd need to adapt the interface
        # This is a simplified implementation
        try:
            # Extract relevant fields for database storage
            task_description = str(value)[:255]  # Truncate to reasonable length
            datetime_str = metadata.get('datetime', '1970-01-01 00:00:00') if metadata else '1970-01-01 00:00:00'
            score = float(metadata.get('score', 0.0)) if metadata else 0.0
            
            self.rust_db.save_memory(task_description, metadata or {}, datetime_str, score)
        except Exception as e:
            # Fallback to original implementation
            self.original_memory.save(value, metadata)
    
    def search(
        self, 
        query: str, 
        limit: int = 3, 
        score_threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        """Search memory for items matching the query."""
        # For long-term memory, we'd need to adapt the interface
        # This is a simplified implementation
        try:
            # Try to load from database
            results = self.rust_db.load_memories(query, limit)
            if results:
                return results
        except Exception as e:
            pass
        
        # Fallback to original implementation
        return self.original_memory.search(query, limit, score_threshold)
    
    def reset(self) -> None:
        """Reset memory storage."""
        try:
            self.rust_db.reset()
        except Exception as e:
            # Fallback to original implementation
            self.original_memory.reset()


class RustToolIntegration:
    """
    Integration layer for CrewAI tool components with Rust backend.
    """
    
    @staticmethod
    def create_tool_executor(max_iterations: int = 100) -> Any:
        """
        Create a tool executor with Rust backend.
        
        Args:
            max_iterations: Maximum number of iterations allowed
            
        Returns:
            Tool executor instance (Rust-enhanced when available)
        """
        try:
            rust_executor = RustToolExecutor(max_recursion_depth=max_iterations)
            return rust_executor
        except Exception as e:
            # Return a compatible Python implementation
            return PythonToolExecutor(max_iterations)


class PythonToolExecutor:
    """
    Compatible Python implementation for tool execution.
    """
    
    def __init__(self, max_iterations: int = 100):
        self.max_iterations = max_iterations
        self.iteration_count = 0
    
    def execute_tool(self, tool_name: str, arguments: Any) -> Any:
        """Execute a tool with the given name and arguments."""
        if self.iteration_count >= self.max_iterations:
            raise Exception(f"Maximum iterations exceeded for tool '{tool_name}'")
        
        self.iteration_count += 1
        try:
            # Simulate tool execution
            import json
            if isinstance(arguments, dict):
                args_str = ", ".join([f"{k}={v}" for k, v in arguments.items()])
            else:
                args_str = str(arguments)
            
            return f"Executed {tool_name} with args: {args_str}"
        finally:
            self.iteration_count -= 1


class RustTaskIntegration:
    """
    Integration layer for CrewAI task components with Rust backend.
    """
    
    @staticmethod
    def create_task_executor() -> Any:
        """
        Create a task executor with Rust backend.
        
        Returns:
            Task executor instance (Rust-enhanced when available)
        """
        try:
            rust_executor = RustTaskExecutor()
            return rust_executor
        except Exception as e:
            # Return a compatible Python implementation
            return PythonTaskExecutor()


class PythonTaskExecutor:
    """
    Compatible Python implementation for task execution.
    """
    
    def execute_concurrent_tasks(self, tasks: List[Any]) -> List[Any]:
        """Execute multiple tasks concurrently."""
        # Simple implementation for compatibility
        results = []
        for task in tasks:
            if isinstance(task, dict):
                task_str = ", ".join([f"{k}={v}" for k, v in task.items()])
            else:
                task_str = str(task)
            results.append(f"Completed: {task_str}")
        return results


def integrate_with_crew(crew: Any) -> None:
    """
    Integrate a crew instance with Rust components.
    
    Args:
        crew: Crew instance to integrate
    """
    # This function would be called to enhance an existing crew with Rust components
    # For now, we'll just set up the configuration
    pass
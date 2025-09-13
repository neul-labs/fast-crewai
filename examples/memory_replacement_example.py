# Example: Replacing Python Memory Storage with Rust Implementation

# This example shows how we could replace the existing Python memory system
# with a high-performance Rust implementation

from crewai_rust import RustMemoryStorage

class RustShortTermMemory:
    """
    A drop-in replacement for CrewAI's ShortTermMemory using Rust backend
    """
    
    def __init__(self, *args, **kwargs):
        # Initialize the Rust memory storage
        self._rust_storage = RustMemoryStorage()
        # Maintain compatibility with existing interface
        self.agent = kwargs.get('agent')
        self.task = kwargs.get('task')
    
    def save(self, value, metadata=None):
        """
        Save a value to memory using the Rust backend
        """
        # Convert the value and metadata to a string format for storage
        import json
        data = {
            'value': value,
            'metadata': metadata
        }
        serialized = json.dumps(data)
        self._rust_storage.save(serialized)
    
    def search(self, query, limit=3, score_threshold=0.35):
        """
        Search memory using the Rust backend
        """
        # Search using the Rust backend
        results = self._rust_storage.search(query)
        
        # Convert results back to the expected format
        import json
        converted_results = []
        for result in results[:limit]:
            try:
                data = json.loads(result)
                converted_results.append(data)
            except:
                # Handle legacy data format
                converted_results.append({'value': result, 'metadata': {}})
        
        return converted_results
    
    def reset(self):
        """
        Reset memory (in a real implementation, this would clear the Rust storage)
        """
        # In a full implementation, we would clear the Rust storage
        pass

# Example usage:
if __name__ == "__main__":
    # Create a Rust-backed memory instance
    memory = RustShortTermMemory()
    
    # Save some data
    memory.save("First memory item", {"type": "test", "priority": 1})
    memory.save("Second memory item", {"type": "test", "priority": 2})
    memory.save("Another item with different content", {"type": "other", "priority": 3})
    
    # Search memory
    results = memory.search("memory")
    print(f"Found {len(results)} results containing 'memory':")
    for result in results:
        print(f"  - {result['value']} (metadata: {result['metadata']})")
    
    # Search with different query
    results = memory.search("item")
    print(f"Found {len(results)} results containing 'item'")
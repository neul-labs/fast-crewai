"""
High-performance memory storage implementation using Rust backend.

This module provides a drop-in replacement for CrewAI's memory storage
systems with significant performance improvements.
"""

import os
import json
import time
from typing import Any, Dict, List, Optional
from . import HAS_RUST_IMPLEMENTATION

# Try to import the Rust implementation
if HAS_RUST_IMPLEMENTATION:
    try:
        from ._core import RustMemoryStorage as _RustMemoryStorage
        _RUST_AVAILABLE = True
    except ImportError:
        _RUST_AVAILABLE = False
else:
    _RUST_AVAILABLE = False


class RustMemoryStorage:
    """
    High-performance memory storage using Rust backend.
    
    This class provides a drop-in replacement for CrewAI's memory storage
    with significant performance improvements while maintaining full
    API compatibility.
    """
    
    def __init__(self, use_rust: Optional[bool] = None):
        """
        Initialize the memory storage.
        
        Args:
            use_rust: Whether to use the Rust implementation. If None, 
                     automatically detects based on availability and 
                     environment variables.
        """
        # Check if Rust implementation should be used
        if use_rust is None:
            # Check environment variable
            env_setting = os.getenv('CREWAI_RUST_MEMORY', 'auto').lower()
            if env_setting == 'true':
                self._use_rust = True
            elif env_setting == 'false':
                self._use_rust = False
            else:  # 'auto' or other values
                self._use_rust = _RUST_AVAILABLE
        else:
            self._use_rust = use_rust and _RUST_AVAILABLE
        
        # Initialize the appropriate implementation
        if self._use_rust:
            try:
                self._storage = _RustMemoryStorage()
                self._implementation = "rust"
            except Exception as e:
                # Fallback to Python implementation
                self._use_rust = False
                self._storage = []
                self._implementation = "python"
                print(f"Warning: Failed to initialize Rust memory storage, falling back to Python: {e}")
        else:
            self._storage = []
            self._implementation = "python"
    
    def save(self, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Save a value to memory.
        
        Args:
            value: The value to save
            metadata: Optional metadata associated with the value
        """
        if self._use_rust:
            try:
                # Serialize data for Rust storage
                data = {
                    'value': value,
                    'metadata': metadata or {},
                    'timestamp': time.time()
                }
                serialized = json.dumps(data, default=str)
                self._storage.save(serialized)
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust memory save failed, using Python fallback: {e}")
                self._use_rust = False
                self._storage.append({
                    'value': value,
                    'metadata': metadata or {},
                    'timestamp': time.time()
                })
        else:
            self._storage.append({
                'value': value,
                'metadata': metadata or {},
                'timestamp': time.time()
            })
    
    def search(
        self, 
        query: str, 
        limit: int = 3, 
        score_threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        """
        Search memory for items matching the query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of matching items with their metadata
        """
        if self._use_rust:
            try:
                # Use Rust implementation for search
                serialized_results = self._storage.search(query)
                results = []
                for item in serialized_results[:limit]:
                    try:
                        data = json.loads(item)
                        results.append(data)
                    except (json.JSONDecodeError, KeyError):
                        # Handle legacy or malformed data
                        results.append({
                            'value': item,
                            'metadata': {},
                            'timestamp': time.time()
                        })
                return results
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust memory search failed, using Python fallback: {e}")
                self._use_rust = False
                return self._python_search(query, limit, score_threshold)
        else:
            return self._python_search(query, limit, score_threshold)
    
    def _python_search(
        self, 
        query: str, 
        limit: int = 3, 
        score_threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        """Python implementation of search for fallback."""
        results = []
        query_lower = query.lower()
        
        for item in self._storage:
            # Simple string matching for demonstration
            # In a real implementation, this would use more sophisticated matching
            item_str = str(item.get('value', '')).lower()
            if query_lower in item_str:
                results.append(item)
        
        # Sort by recency and limit results
        results.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return results[:limit]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all items in memory.
        
        Returns:
            List of all items in memory
        """
        if self._use_rust:
            try:
                serialized_items = self._storage.get_all()
                items = []
                for item in serialized_items:
                    try:
                        data = json.loads(item)
                        items.append(data)
                    except (json.JSONDecodeError, KeyError):
                        items.append({
                            'value': item,
                            'metadata': {},
                            'timestamp': time.time()
                        })
                return items
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust memory get_all failed, using Python fallback: {e}")
                self._use_rust = False
                return self._storage
        else:
            return self._storage
    
    def reset(self) -> None:
        """Reset memory storage."""
        if self._use_rust:
            try:
                # Rust implementation doesn't currently have a reset method
                # so we'll recreate the storage
                self._storage = _RustMemoryStorage()
            except Exception as e:
                # Fallback to Python implementation on error
                print(f"Warning: Rust memory reset failed, using Python fallback: {e}")
                self._use_rust = False
                self._storage = []
        else:
            self._storage = []
    
    @property
    def implementation(self) -> str:
        """Get the current implementation type."""
        return self._implementation
    
    def __len__(self) -> int:
        """Get the number of items in storage."""
        if self._use_rust:
            try:
                return len(self._storage.get_all())
            except:
                return len(self._storage)  # Fallback
        else:
            return len(self._storage)
    
    def __repr__(self) -> str:
        """String representation of the storage."""
        return f"RustMemoryStorage(implementation={self.implementation}, items={len(self)})"
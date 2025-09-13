"""
CrewAI Rust Integration Package

This package provides high-performance Rust implementations for critical 
CrewAI components while maintaining full backward compatibility.

The components automatically fall back to Python implementations when
Rust is not available, ensuring zero breaking changes.
"""

try:
    # Try to import the Rust extension
    from ._core import (
        RustMemoryStorage,
        RustToolExecutor,
        RustTaskExecutor,
        AgentMessage,
        RustSQLiteWrapper,
    )
    
    # Mark Rust implementation as available
    HAS_RUST_IMPLEMENTATION = True
    
except ImportError:
    # Rust implementation not available, set flags to False
    HAS_RUST_IMPLEMENTATION = False
    
    # Create placeholder classes to prevent ImportError
    class RustMemoryStorage:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Rust implementation not available")
    
    class RustToolExecutor:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Rust implementation not available")
            
    class RustTaskExecutor:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Rust implementation not available")
            
    class AgentMessage:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Rust implementation not available")
            
    class RustSQLiteWrapper:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Rust implementation not available")

# Version information
__version__ = "0.1.0"
__author__ = "CrewAI"

# Import public API
from .memory import RustMemoryStorage
from .tools import RustToolExecutor
from .tasks import RustTaskExecutor
from .serialization import AgentMessage
from .database import RustSQLiteWrapper

# Import utility functions
from .utils import (
    is_rust_available,
    get_rust_status,
    configure_rust_components,
    get_performance_improvements,
    get_environment_info
)

# Import integration utilities
from .integration import (
    RustMemoryIntegration,
    RustToolIntegration,
    RustTaskIntegration
)

__all__ = [
    "HAS_RUST_IMPLEMENTATION",
    "RustMemoryStorage",
    "RustToolExecutor",
    "RustTaskExecutor",
    "AgentMessage",
    "RustSQLiteWrapper",
    "is_rust_available",
    "get_rust_status",
    "configure_rust_components",
    "get_performance_improvements",
    "get_environment_info",
    "RustMemoryIntegration",
    "RustToolIntegration",
    "RustTaskIntegration",
]
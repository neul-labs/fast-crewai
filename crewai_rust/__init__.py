"""
CrewAI Rust Integration Package

This package provides high-performance Rust implementations for critical 
CrewAI components while maintaining full backward compatibility.

To use these components, you must explicitly import and use them in your code.
They do not automatically replace the standard CrewAI components.

However, automatic shimming is available through:
1. Environment variable: CREWAI_RUST_ACCELERATION=1
2. Import hook: import crewai_rust.shim
3. Bootstrap script: crewai-rust-bootstrap

The components automatically fall back to Python implementations when
Rust is not available, ensuring zero breaking changes.
"""

import os

# Version information
__version__ = "0.1.0"
__author__ = "CrewAI"

# Auto-enable Rust acceleration if environment variable is set
# Note: We do this after defining __version__ to avoid circular imports
if os.environ.get('CREWAI_RUST_ACCELERATION') == '1':
    try:
        # Import locally to avoid circular imports
        def _enable_rust_acceleration():
            try:
                from .shim import enable_rust_acceleration
                return enable_rust_acceleration()
            except Exception:
                return False
        
        _enable_rust_acceleration()
    except Exception:
        # Silently fail if shimming doesn't work
        pass

# Import the actual components (this will handle the Rust vs Python fallback)
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
"""
CrewAI Accelerate Package

This package provides high-performance acceleration for critical
CrewAI components while maintaining full backward compatibility.

To use these components, you must explicitly import and use them in your code.
They do not automatically replace the standard CrewAI components.

However, automatic shimming is available through:
1. Environment variable: FAST_CREWAI_ACCELERATION=1
2. Import hook: import fast_crewai.shim
3. Bootstrap script: fast-crewai-bootstrap

The components automatically fall back to Python implementations when
acceleration is not available, ensuring zero breaking changes.
"""

import os

# Version information
__version__ = "0.1.0"
__author__ = "CrewAI"

# Auto-enable acceleration if environment variable is set
# Note: We do this after defining __version__ to avoid circular imports
if os.environ.get("FAST_CREWAI_ACCELERATION") == "1":
    try:
        # Import locally to avoid circular imports
        def _enable_acceleration():
            try:
                from .shim import enable_acceleration

                return enable_acceleration()
            except Exception:
                return False

        _enable_acceleration()
    except Exception:
        # Silently fail if shimming doesn't work
        pass

# Import the actual components (this will handle the acceleration vs Python fallback)
try:
    # Try to import the accelerated extension
    from ._core import (AcceleratedMemoryStorage, AcceleratedMessage,
                        AcceleratedSQLiteWrapper, AcceleratedTaskExecutor,
                        AcceleratedToolExecutor)

    # Mark acceleration implementation as available
    HAS_ACCELERATION_IMPLEMENTATION = True

except ImportError:
    # Acceleration implementation not available, set flags to False
    HAS_ACCELERATION_IMPLEMENTATION = False

    # Create placeholder classes to prevent ImportError
    class AcceleratedMemoryStorage:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Acceleration implementation not available")

    class AcceleratedToolExecutor:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Acceleration implementation not available")

    class AcceleratedTaskExecutor:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Acceleration implementation not available")

    class AcceleratedMessage:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Acceleration implementation not available")

    class AcceleratedSQLiteWrapper:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Acceleration implementation not available")


from .database import AcceleratedSQLiteWrapper
# Import integration utilities
from .integration import (AcceleratedMemoryIntegration,
                          AcceleratedTaskIntegration,
                          AcceleratedToolIntegration)
# Import public API
from .memory import AcceleratedMemoryStorage
from .serialization import AgentMessage, RustSerializer
from .tasks import AcceleratedTaskExecutor
from .tools import AcceleratedToolExecutor
# Import utility functions
from .utils import (configure_accelerated_components, get_acceleration_status,
                    get_environment_info, get_performance_improvements,
                    is_acceleration_available)

__all__ = [
    "HAS_ACCELERATION_IMPLEMENTATION",
    "AcceleratedMemoryStorage",
    "AcceleratedToolExecutor",
    "AcceleratedTaskExecutor",
    "AgentMessage",
    "RustSerializer",
    "AcceleratedSQLiteWrapper",
    "is_acceleration_available",
    "get_acceleration_status",
    "configure_accelerated_components",
    "get_performance_improvements",
    "get_environment_info",
    "AcceleratedMemoryIntegration",
    "AcceleratedToolIntegration",
    "AcceleratedTaskIntegration",
]

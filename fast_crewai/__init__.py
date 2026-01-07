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

import logging
import os

# Configure module logger
_logger = logging.getLogger(__name__)

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
            except Exception as e:
                _logger.debug("Failed to enable acceleration: %s", e)
                return False

        _enable_acceleration()
    except Exception as e:
        # Silently fail if shimming doesn't work
        _logger.debug("Acceleration initialization failed: %s", e)
        pass

# Check if acceleration implementation is available
try:
    from ._core import AgentMessage as _CoreMessage  # noqa: F401
    from ._core import RustMemoryStorage as _CoreMemoryStorage
    from ._core import RustSQLiteWrapper as _CoreSQLiteWrapper
    from ._core import RustTaskExecutor as _CoreTaskExecutor
    from ._core import RustToolExecutor as _CoreToolExecutor

    HAS_ACCELERATION_IMPLEMENTATION = True
    # These are available but we prefer the wrapper classes from submodules
    del _CoreMemoryStorage, _CoreMessage, _CoreSQLiteWrapper
    del _CoreTaskExecutor, _CoreToolExecutor

except ImportError:
    # Acceleration implementation not available
    HAS_ACCELERATION_IMPLEMENTATION = False


# Import public API from submodules (these provide Python fallbacks)
from .database import AcceleratedSQLiteWrapper
from .integration import (
    AcceleratedMemoryIntegration,
    AcceleratedTaskIntegration,
    AcceleratedToolIntegration,
)
from .memory import AcceleratedMemoryStorage
from .serialization import AgentMessage, RustSerializer
from .tasks import AcceleratedTaskExecutor
from .tools import AcceleratedToolExecutor
from .utils import (
    configure_accelerated_components,
    get_acceleration_status,
    get_environment_info,
    get_performance_improvements,
    is_acceleration_available,
)

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

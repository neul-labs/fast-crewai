"""
Internal constants for fast_crewai.

This module contains constants that need to be accessed by submodules
without creating circular imports.
"""

# Try to import the Rust core to determine if acceleration is available
try:
    from ._core import (  # noqa: F401
        AcceleratedMemoryStorage,
        AcceleratedSQLiteWrapper,
        AcceleratedTaskExecutor,
        AcceleratedToolExecutor,
        AgentMessage,
    )

    HAS_ACCELERATION_IMPLEMENTATION = True
except ImportError:
    HAS_ACCELERATION_IMPLEMENTATION = False

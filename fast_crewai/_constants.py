"""
Internal constants for fast_crewai.

This module contains constants that need to be accessed by submodules
without creating circular imports.
"""

# Try to import the Rust core to determine if acceleration is available
try:
    from ._core import (  # noqa: F401
        AgentMessage,
        RustMemoryStorage,
        RustSQLiteWrapper,
        RustTaskExecutor,
        RustToolExecutor,
    )

    # Create aliases for consistent naming (Rust names -> Accelerated names)
    # These aliases allow submodules to import as "Accelerated*"
    AcceleratedMemoryStorage = RustMemoryStorage
    AcceleratedSQLiteWrapper = RustSQLiteWrapper
    AcceleratedTaskExecutor = RustTaskExecutor
    AcceleratedToolExecutor = RustToolExecutor

    HAS_ACCELERATION_IMPLEMENTATION = True
except ImportError:
    # Define as None so imports don't fail
    RustMemoryStorage = None
    RustSQLiteWrapper = None
    RustTaskExecutor = None
    RustToolExecutor = None
    AcceleratedMemoryStorage = None
    AcceleratedSQLiteWrapper = None
    AcceleratedTaskExecutor = None
    AcceleratedToolExecutor = None
    AgentMessage = None

    HAS_ACCELERATION_IMPLEMENTATION = False

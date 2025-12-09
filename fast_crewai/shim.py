"""
Bootstrap script to automatically shim fast-crewai components into CrewAI.
Usage:
    import crewai
    import fast_crewai.shim  # This automatically replaces components

Or:
    import crewai
    from fast_crewai.shim import enable_acceleration
    enable_acceleration()
"""

import importlib
import sys
from typing import Any

# Track original classes to allow restoration
_original_classes = {}


def _monkey_patch_class(module_path: str, class_name: str, new_class: Any) -> bool:
    """
    Replace a class in a module with a new implementation.

    Args:
        module_path: Path to the module (e.g., 'crewai.memory')
        class_name: Name of the class to replace
        new_class: New class implementation

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Import the module
        if module_path in sys.modules:
            module = sys.modules[module_path]
        else:
            module = importlib.import_module(module_path)

        # Save original class if it exists
        if hasattr(module, class_name):
            original_class = getattr(module, class_name)
            _original_classes[f"{module_path}.{class_name}"] = original_class

        # Replace the class
        setattr(module, class_name, new_class)
        return True

    except Exception:
        # Only print debug info if in verbose mode
        return False


def _patch_memory_components():
    """Patch memory-related components."""
    patches_applied = 0
    patches_failed = 0

    try:
        from fast_crewai.memory import AcceleratedMemoryStorage

        # Patch main memory storage components with correct module paths
        memory_patches = [
            (
                "crewai.memory.storage.rag_storage",
                "RAGStorage",
                AcceleratedMemoryStorage,
            ),
            (
                "crewai.memory.short_term.short_term_memory",
                "ShortTermMemory",
                AcceleratedMemoryStorage,
            ),
            ("crewai.memory.memory", "Memory", AcceleratedMemoryStorage),
            (
                "crewai.memory.long_term.long_term_memory",
                "LongTermMemory",
                AcceleratedMemoryStorage,
            ),
            (
                "crewai.memory.entity.entity_memory",
                "EntityMemory",
                AcceleratedMemoryStorage,
            ),
        ]

        for module_path, class_name, new_class in memory_patches:
            if _monkey_patch_class(module_path, class_name, new_class):
                patches_applied += 1
            else:
                patches_failed += 1

    except Exception as e:
        print(f"⚠️  Memory component patching failed: {e}")
        patches_failed += 1

    return patches_applied, patches_failed


def _patch_tool_components():
    """
    Patch tool-related components with dynamically inherited accelerated classes.

    Uses dynamic inheritance to create accelerated versions that properly inherit
    from CrewAI's BaseTool and CrewStructuredTool classes.
    """
    patches_applied = 0
    patches_failed = 0

    try:
        from fast_crewai.tools import AcceleratedBaseTool, AcceleratedStructuredTool

        # Only patch if the accelerated classes were successfully created
        if AcceleratedBaseTool is not None:
            tool_patches = [
                ("crewai.tools.base_tool", "BaseTool", AcceleratedBaseTool),
            ]

            for module_path, class_name, new_class in tool_patches:
                if _monkey_patch_class(module_path, class_name, new_class):
                    patches_applied += 1
                else:
                    patches_failed += 1

        if AcceleratedStructuredTool is not None:
            structured_patches = [
                (
                    "crewai.tools.structured_tool",
                    "CrewStructuredTool",
                    AcceleratedStructuredTool,
                ),
            ]

            for module_path, class_name, new_class in structured_patches:
                if _monkey_patch_class(module_path, class_name, new_class):
                    patches_applied += 1
                else:
                    patches_failed += 1

    except ImportError:
        # CrewAI not installed, skip patching
        pass
    except Exception:
        # Unexpected error, log and continue
        patches_failed += 1

    return patches_applied, patches_failed


def _patch_task_components():
    """
    Patch task-related components with dynamically inherited accelerated classes.

    Uses dynamic inheritance to create accelerated versions that properly inherit
    from CrewAI's Task and Crew classes.
    """
    patches_applied = 0
    patches_failed = 0

    try:
        from fast_crewai.tasks import AcceleratedCrew, AcceleratedTask

        # Only patch if the accelerated classes were successfully created
        if AcceleratedTask is not None:
            task_patches = [
                ("crewai.task", "Task", AcceleratedTask),
            ]

            for module_path, class_name, new_class in task_patches:
                if _monkey_patch_class(module_path, class_name, new_class):
                    patches_applied += 1
                else:
                    patches_failed += 1

        if AcceleratedCrew is not None:
            crew_patches = [
                ("crewai.crew", "Crew", AcceleratedCrew),
            ]

            for module_path, class_name, new_class in crew_patches:
                if _monkey_patch_class(module_path, class_name, new_class):
                    patches_applied += 1
                else:
                    patches_failed += 1

    except ImportError:
        # CrewAI not installed, skip patching
        pass
    except Exception:
        # Unexpected error, log and continue
        patches_failed += 1

    return patches_applied, patches_failed


def _patch_database_components():
    """Patch database-related components."""
    patches_applied = 0
    patches_failed = 0

    try:
        from fast_crewai.database import AcceleratedSQLiteWrapper

        # Patch database components with correct class names
        database_patches = [
            (
                "crewai.memory.storage.ltm_sqlite_storage",
                "LTMSQLiteStorage",
                AcceleratedSQLiteWrapper,
            ),
            (
                "crewai.memory.storage.kickoff_task_outputs_storage",
                "KickoffTaskOutputsSQLiteStorage",
                AcceleratedSQLiteWrapper,
            ),
        ]

        for module_path, class_name, new_class in database_patches:
            if _monkey_patch_class(module_path, class_name, new_class):
                patches_applied += 1
            else:
                patches_failed += 1

    except Exception as e:
        print(f"⚠️  Database component patching failed: {e}")
        patches_failed += 1

    return patches_applied, patches_failed


def _patch_serialization_components():
    """
    Patch serialization-related components.

    Note: Serialization acceleration could patch JSON encoding/decoding functions,
    but this is not yet implemented. Event classes should not be replaced.
    """
    patches_applied = 0
    patches_failed = 0

    # Serialization patching: Could accelerate json.dumps/json.loads with Rust implementations
    # However, this is complex and may have compatibility issues, so it's not implemented yet.
    # Future implementation could:
    # 1. Monkey-patch json.dumps and json.loads with faster implementations
    # 2. Use orjson or similar high-performance JSON libraries
    # 3. Add Rust-based JSON encoding/decoding in the _core module

    # For now, serialization acceleration is provided through the AgentMessage class
    # which can be used directly for message serialization, but we don't patch
    # system-wide JSON functions to avoid compatibility issues.

    return patches_applied, patches_failed


def enable_acceleration(verbose: bool = False) -> bool:
    """
    Monkey patch CrewAI components with accelerated equivalents.
    This function replaces CrewAI's core components with their accelerated counterparts.

    Args:
        verbose: Whether to print detailed information about patching

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        total_patches_applied = 0
        total_patches_failed = 0

        if verbose:
            print("🚀 Enabling acceleration for CrewAI...")

        # Patch each component type
        memory_applied, memory_failed = _patch_memory_components()
        total_patches_applied += memory_applied
        total_patches_failed += memory_failed

        tool_applied, tool_failed = _patch_tool_components()
        total_patches_applied += tool_applied
        total_patches_failed += tool_failed

        task_applied, task_failed = _patch_task_components()
        total_patches_applied += task_applied
        total_patches_failed += task_failed

        db_applied, db_failed = _patch_database_components()
        total_patches_applied += db_applied
        total_patches_failed += db_failed

        serialization_applied, serialization_failed = _patch_serialization_components()
        total_patches_applied += serialization_applied
        total_patches_failed += serialization_failed

        if verbose:
            print("Acceleration bootstrap completed!")
            print(f"  - Memory patches applied: {memory_applied}, failed: {memory_failed}")
            print(f"  - Tool patches applied: {tool_applied}, failed: {tool_failed}")
            print(f"  - Task patches applied: {task_applied}, failed: {task_failed}")
            print(f"  - Database patches applied: {db_applied}, failed: {db_failed}")
            print(f"  - Serialization patches: {serialization_applied} (not yet implemented)")
            print(f"  - Total patches applied: {total_patches_applied}")
            print(f"  - Total patches failed: {total_patches_failed}")

        if total_patches_applied > 0 and verbose:
            print("\n🚀 Performance improvements now active:")
            if memory_applied > 0:
                print("  - Memory Storage: 2-5x faster")
            if db_applied > 0:
                print("  - Database Operations: 2-4x faster")
            if tool_applied > 0:
                print("  - Tool Execution: Acceleration hooks enabled")
            if task_applied > 0:
                print("  - Task Execution: Acceleration hooks enabled")
            if serialization_applied > 0:
                print("  - Serialization: Accelerated JSON processing")

        return total_patches_applied > 0

    except ImportError as e:
        if verbose:
            print(f"⚠️  Acceleration components not available: {e}")
        return False
    except Exception as e:
        if verbose:
            print(f"❌ Failed to enable acceleration: {e}")
        return False


def disable_acceleration() -> bool:
    """
    Restore original CrewAI components.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        restored = 0
        for full_path, original_class in _original_classes.items():
            try:
                module_path, class_name = full_path.rsplit(".", 1)
                if module_path in sys.modules:
                    module = sys.modules[module_path]
                    setattr(module, class_name, original_class)
                    restored += 1
            except Exception:
                continue

        _original_classes.clear()
        print(f"✅ Restored {restored} original classes")
        return True

    except Exception as e:
        print(f"❌ Failed to restore original classes: {e}")
        return False


# Auto-enable when imported as a module (but not when run as main)
if __name__ != "__main__":
    enable_acceleration()

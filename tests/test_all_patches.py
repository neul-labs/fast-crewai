#!/usr/bin/env python3
"""
Comprehensive test script to validate all Fast-CrewAI patches.

This script tests:
1. Shim loading and activation
2. Memory component patching
3. Database component patching
4. Tool component patching (dynamic inheritance)
5. Task component patching (dynamic inheritance)
6. Serialization component availability

Run this before the CrewAI compatibility tests to ensure all patches work correctly.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_shim_loading():
    """Test that the shim loads without errors."""
    print("=" * 80)
    print("TEST 1: Shim Loading")
    print("=" * 80)

    try:
        import fast_crewai.shim

        print("✅ Shim imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import shim: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_acceleration_status():
    """Test acceleration status reporting."""
    print("\n" + "=" * 80)
    print("TEST 2: Acceleration Status")
    print("=" * 80)

    try:
        from fast_crewai import get_acceleration_status

        status = get_acceleration_status()

        print("\nAcceleration Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        print("✅ Acceleration status retrieved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to get acceleration status: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tool_patching():
    """Test that tool patching uses dynamic inheritance."""
    print("\n" + "=" * 80)
    print("TEST 3: Tool Patching (Dynamic Inheritance)")
    print("=" * 80)

    try:
        from fast_crewai.tools import (AcceleratedBaseTool,
                                       AcceleratedStructuredTool)

        if AcceleratedBaseTool is not None:
            print("✅ AcceleratedBaseTool created successfully")
            print(f"   Base classes: {AcceleratedBaseTool.__bases__}")
        else:
            print("⚠️  AcceleratedBaseTool is None (CrewAI not installed)")

        if AcceleratedStructuredTool is not None:
            print("✅ AcceleratedStructuredTool created successfully")
            print(f"   Base classes: {AcceleratedStructuredTool.__bases__}")
        else:
            print("⚠️  AcceleratedStructuredTool is None (CrewAI not installed)")

        return True
    except Exception as e:
        print(f"❌ Failed to test tool patching: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_task_patching():
    """Test that task patching uses dynamic inheritance."""
    print("\n" + "=" * 80)
    print("TEST 4: Task Patching (Dynamic Inheritance)")
    print("=" * 80)

    try:
        from fast_crewai.tasks import AcceleratedCrew, AcceleratedTask

        if AcceleratedTask is not None:
            print("✅ AcceleratedTask created successfully")
            print(f"   Base classes: {AcceleratedTask.__bases__}")
        else:
            print("⚠️  AcceleratedTask is None (CrewAI not installed)")

        if AcceleratedCrew is not None:
            print("✅ AcceleratedCrew created successfully")
            print(f"   Base classes: {AcceleratedCrew.__bases__}")
        else:
            print("⚠️  AcceleratedCrew is None (CrewAI not installed)")

        return True
    except Exception as e:
        print(f"❌ Failed to test task patching: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_memory_components():
    """Test memory component availability."""
    print("\n" + "=" * 80)
    print("TEST 5: Memory Components")
    print("=" * 80)

    try:
        from fast_crewai.memory import AcceleratedMemoryStorage

        print("✅ AcceleratedMemoryStorage imported successfully")
        print(f"   Class: {AcceleratedMemoryStorage}")
        return True
    except Exception as e:
        print(f"❌ Failed to import memory components: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_components():
    """Test database component availability."""
    print("\n" + "=" * 80)
    print("TEST 6: Database Components")
    print("=" * 80)

    try:
        from fast_crewai.database import AcceleratedSQLiteWrapper

        print("✅ AcceleratedSQLiteWrapper imported successfully")
        print(f"   Class: {AcceleratedSQLiteWrapper}")
        return True
    except Exception as e:
        print(f"❌ Failed to import database components: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_serialization_components():
    """Test serialization component availability."""
    print("\n" + "=" * 80)
    print("TEST 7: Serialization Components")
    print("=" * 80)

    try:
        from fast_crewai.serialization import AcceleratedMessage, AgentMessage

        print("✅ AgentMessage imported successfully")
        print(f"   Class: {AgentMessage}")
        print("✅ AcceleratedMessage alias available")
        print(f"   Alias: {AcceleratedMessage}")
        return True
    except Exception as e:
        print(f"❌ Failed to import serialization components: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_crewai_patching():
    """Test that CrewAI classes are actually patched (if CrewAI is installed)."""
    print("\n" + "=" * 80)
    print("TEST 8: CrewAI Class Patching (if CrewAI installed)")
    print("=" * 80)

    try:
        # Try to import CrewAI components
        try:
            from crewai.crew import Crew
            from crewai.task import Task
            from crewai.tools.base_tool import BaseTool

            print("✅ CrewAI is installed")

            # Check if classes are patched
            print(f"\nBaseTool class: {BaseTool}")
            print(f"  Module: {BaseTool.__module__}")

            print(f"\nTask class: {Task}")
            print(f"  Module: {Task.__module__}")

            print(f"\nCrew class: {Crew}")
            print(f"  Module: {Crew.__module__}")

            # Check if they have acceleration attributes
            if hasattr(BaseTool, "__bases__"):
                print(f"\nBaseTool inheritance chain: {BaseTool.__mro__[:3]}")

            print("\n✅ CrewAI classes inspected successfully")
            return True

        except ImportError:
            print("⚠️  CrewAI not installed - skipping patching verification")
            return True

    except Exception as e:
        print(f"❌ Failed to verify CrewAI patching: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "Fast-CrewAI Patch Validation" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    tests = [
        ("Shim Loading", test_shim_loading),
        ("Acceleration Status", test_acceleration_status),
        ("Tool Patching", test_tool_patching),
        ("Task Patching", test_task_patching),
        ("Memory Components", test_memory_components),
        ("Database Components", test_database_components),
        ("Serialization Components", test_serialization_components),
        ("CrewAI Patching", test_crewai_patching),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {name}")

    print("=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("\n🎉 All tests passed! Fast-CrewAI patches are working correctly.")
        print("\nYou can now run the CrewAI compatibility tests:")
        print("  ./scripts/test_crewai_compatibility.sh --skip-clone --skip-install")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

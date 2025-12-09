#!/usr/bin/env python3
"""
CrewAI Accelerate Bootstrap Script

This script can be used to automatically shim fast-crewai components
into CrewAI without requiring code changes.

Usage:
    python -m fast_crewai.bootstrap

Or set environment variable:
    export FAST_CREWAI_ACCELERATION=1
    python your_crewai_app.py
"""

import sys


def bootstrap_acceleration():
    """Bootstrap acceleration into CrewAI."""
    try:
        # Check if CrewAI is already imported
        if "crewai" in sys.modules:
            print("⚠️  CrewAI already imported. Acceleration may not work fully.")
            print("   Please import this bootstrap script before importing CrewAI.")

        # Import and enable acceleration
        from fast_crewai.shim import enable_acceleration

        success = enable_acceleration()

        if success:
            print("\n🚀 CrewAI acceleration is now active!")
            print(
                "   No code changes required - your existing CrewAI code will run faster."
            )
        else:
            print("\n❌ Failed to enable acceleration.")

    except Exception as e:
        print(f"❌ Error during bootstrap: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        return

    bootstrap_acceleration()


if __name__ == "__main__":
    main()

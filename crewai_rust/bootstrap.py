#!/usr/bin/env python3
"""
CrewAI Rust Acceleration Bootstrap Script

This script can be used to automatically shim crewai-rust components
into CrewAI without requiring code changes.

Usage:
    python -m crewai_rust.bootstrap
    
Or set environment variable:
    export CREWAI_RUST_ACCELERATION=1
    python your_crewai_app.py
"""

import os
import sys

def bootstrap_rust_acceleration():
    """Bootstrap Rust acceleration into CrewAI."""
    try:
        # Check if CrewAI is already imported
        if 'crewai' in sys.modules:
            print("⚠️  CrewAI already imported. Rust acceleration may not work fully.")
            print("   Please import this bootstrap script before importing CrewAI.")
        
        # Import and enable Rust acceleration
        from crewai_rust.shim import enable_rust_acceleration
        success = enable_rust_acceleration()
        
        if success:
            print("\n🚀 CrewAI Rust acceleration is now active!")
            print("   No code changes required - your existing CrewAI code will run faster.")
        else:
            print("\n❌ Failed to enable Rust acceleration.")
            
    except Exception as e:
        print(f"❌ Error during bootstrap: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        return
        
    bootstrap_rust_acceleration()

if __name__ == "__main__":
    main()
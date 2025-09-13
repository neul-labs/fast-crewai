#!/bin/bash
# Script to build and test the crewai-rust package

echo "Building crewai-rust package with maturin..."

# Check if maturin is installed
if ! command -v maturin &> /dev/null
then
    echo "maturin could not be found, installing..."
    pip install maturin
fi

# Build the package in development mode
echo "Building in development mode..."
maturin develop

# Run a simple test
echo "Running basic import test..."
python test_package.py

echo "Build and test completed!"
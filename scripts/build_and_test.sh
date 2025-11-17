#!/bin/bash
# Script to build and test the fast-crewai package

echo "Building fast-crewai package with maturin..."

# Check if maturin is installed
if ! command -v maturin &> /dev/null
then
    echo "maturin could not be found, installing..."
    pip install maturin
fi

# Build the package in development mode
echo "Building in development mode..."
maturin develop

# Run tests
echo "Running test suite..."
python -m pytest tests/test_package_import.py -v

echo "Build and test completed!"
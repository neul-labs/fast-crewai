#!/bin/bash
# Script to build and test the fast-crewai package

echo "Building fast-crewai package with maturin..."

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "uv could not be found. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
uv sync --dev

# Build the package in development mode
echo "Building in development mode..."
uv run maturin develop

# Run tests
echo "Running test suite..."
uv run pytest tests/test_package_import.py -v

echo "Build and test completed!"

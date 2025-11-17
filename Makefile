# Makefile for Fast-CrewAI
# Provides convenient commands for development and testing

.PHONY: help install install-dev build test test-fast test-coverage test-compatibility clean lint format docs

# Default target
help:
	@echo "Fast-CrewAI - Available Commands:"
	@echo "======================================"
	@echo ""
	@echo "Setup:"
	@echo "  install           - Install package in development mode"
	@echo "  install-dev       - Install with development dependencies"
	@echo "  build             - Build the Rust extension"
	@echo ""
	@echo "Testing:"
	@echo "  test              - Run all tests"
	@echo "  test-fast         - Run fast tests only"
	@echo "  test-coverage     - Run tests with coverage report"
	@echo "  test-compatibility- Test compatibility with CrewAI"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint              - Run linting checks"
	@echo "  format            - Format code with black and isort"
	@echo ""
	@echo "Documentation:"
	@echo "  docs              - Build documentation"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean             - Clean build artifacts"
	@echo "  clean-test        - Clean test artifacts and compatibility test environment"

# Installation
install:
	pip install -r requirements.txt
	maturin develop

install-dev:
	pip install -r requirements-dev.txt
	maturin develop

# Building
build:
	maturin develop

# Testing
test:
	pytest -v

test-fast:
	pytest -m "not slow and not integration and not performance" -v

test-coverage:
	pytest --cov=fast_crewai --cov-report=html --cov-report=term

test-compatibility:
	@echo "Running CrewAI compatibility tests..."
	./scripts/test_crewai_compatibility.sh

test-compatibility-keep:
	@echo "Running CrewAI compatibility tests (keeping environment)..."
	./scripts/test_crewai_compatibility.sh --keep-env

# Code quality
lint:
	flake8 fast_crewai tests
	mypy fast_crewai

format:
	black fast_crewai tests
	isort fast_crewai tests

# Documentation
docs:
	cd docs && make html

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-test:
	rm -rf test_compatibility/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

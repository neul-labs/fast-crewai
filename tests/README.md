# CrewAI Rust Test Suite

This directory contains comprehensive tests for the CrewAI Rust acceleration project.

## Test Structure

```
tests/
├── __init__.py                # Test package initialization
├── conftest.py               # Pytest configuration and fixtures
├── requirements.txt          # Test dependencies
├── README.md                # This file
├── test_package_import.py    # Basic package import tests
├── test_memory.py           # Memory storage component tests
├── test_tools.py            # Tool execution component tests
├── test_tasks.py            # Task execution component tests
├── test_shim.py             # Shim system tests
└── test_integration.py      # End-to-end integration tests
```

## Test Categories

### Unit Tests
- **test_package_import.py**: Basic package functionality
- **test_memory.py**: Memory storage components
- **test_tools.py**: Tool execution components
- **test_tasks.py**: Task execution components
- **test_shim.py**: Monkey patching system

### Integration Tests
- **test_integration.py**: End-to-end workflows with CrewAI

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Optional: Install CrewAI for integration tests
pip install crewai
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_memory.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=crewai_rust
```

### Selective Test Execution

```bash
# Run only fast tests (exclude slow tests)
pytest -m "not slow"

# Run only unit tests (exclude integration tests)
pytest -m "not integration"

# Run only performance tests
pytest -m "performance"

# Run tests that require Rust acceleration
pytest -m "rust_required"
```

### Advanced Options

```bash
# Run with detailed output
pytest --tb=short -v

# Run with coverage report
pytest --cov=crewai_rust --cov-report=html

# Run specific test class
pytest tests/test_memory.py::TestRustMemoryStorage

# Run specific test method
pytest tests/test_memory.py::TestRustMemoryStorage::test_memory_save_basic

# Run tests matching pattern
pytest -k "memory"
```

### Performance Testing

```bash
# Run performance benchmarks
pytest tests/test_integration.py::TestPerformanceIntegration -v

# Run with benchmark reporting
pytest --benchmark-only
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run on 4 processes
pytest -n 4
```

## Test Markers

Tests are organized with markers for easy selection:

- `@pytest.mark.slow`: Tests that take longer to run
- `@pytest.mark.integration`: Tests requiring CrewAI integration
- `@pytest.mark.performance`: Performance and benchmark tests
- `@pytest.mark.rust_required`: Tests requiring Rust acceleration

## Test Fixtures

Common fixtures available in all tests:

- `rust_available`: Boolean indicating if Rust acceleration is available
- `crewai_available`: Boolean indicating if CrewAI is available
- `clean_environment`: Provides isolated test environment
- `memory_storage`: Pre-configured memory storage instance
- `tool_executor`: Pre-configured tool executor instance
- `task_executor`: Pre-configured task executor instance
- `sample_documents`: List of sample documents for testing
- `sample_metadata`: List of sample metadata for testing

## Writing New Tests

### Test File Naming
- Use `test_*.py` naming convention
- Group related tests in the same file
- Use descriptive test class names

### Test Structure
```python
import pytest
from crewai_rust import RustMemoryStorage

class TestNewComponent:
    """Test cases for new component."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        component = RustMemoryStorage()
        assert component is not None

    @pytest.mark.slow
    def test_performance(self):
        """Test performance characteristics."""
        # Performance test implementation
        pass

    @pytest.mark.integration
    def test_crewai_integration(self):
        """Test integration with CrewAI."""
        try:
            import crewai
            # Integration test implementation
        except ImportError:
            pytest.skip("CrewAI not available")
```

### Assertion Guidelines
- Use descriptive assertion messages
- Test both success and failure cases
- Verify return types and values
- Test edge cases and error conditions

### Mock Usage
```python
from unittest.mock import patch, MagicMock

def test_with_mocking():
    """Test with mocked dependencies."""
    with patch('crewai_rust.RustMemoryStorage') as mock_storage:
        mock_storage.return_value.save.return_value = True
        # Test implementation
```

## Continuous Integration

These tests are designed to run in CI environments:

- Tests automatically skip when dependencies are unavailable
- Performance tests can be selectively disabled
- Integration tests require CrewAI installation
- All tests should pass without external services

## Troubleshooting

### Common Issues

1. **ImportError for CrewAI**
   ```bash
   # Install CrewAI for integration tests
   pip install crewai

   # Or skip integration tests
   pytest -m "not integration"
   ```

2. **Rust Acceleration Not Available**
   ```bash
   # Check Rust installation
   python -c "from crewai_rust import is_rust_available; print(is_rust_available())"

   # Or skip Rust-required tests
   pytest -m "not rust_required"
   ```

3. **Slow Test Execution**
   ```bash
   # Skip slow tests
   pytest -m "not slow"

   # Run in parallel
   pytest -n auto
   ```

### Debug Mode
```bash
# Run with Python debugger
pytest --pdb

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## Contributing

When adding new tests:

1. Follow existing naming conventions
2. Add appropriate markers for test categorization
3. Include docstrings explaining test purpose
4. Handle optional dependencies gracefully
5. Update this README if adding new test categories

## Test Coverage

Aim for comprehensive coverage of:

- All public APIs
- Error conditions and edge cases
- Integration points with CrewAI
- Performance characteristics
- Fallback behavior when Rust is unavailable
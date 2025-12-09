"""
Pytest configuration for CrewAI Rust tests.
"""

import os
import sys

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require CrewAI)"
    )
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line(
        "markers",
        "rust_required: marks tests that require Rust acceleration to be available",
    )
    # Configure markers based on command line options
    _configure_markers(config)


@pytest.fixture(scope="session")
def rust_available():
    """Check if Rust acceleration is available."""
    try:
        from fast_crewai import is_rust_available

        return is_rust_available()
    except ImportError:
        return False


@pytest.fixture(scope="session")
def crewai_available():
    """Check if CrewAI is available for integration testing."""
    try:
        import crewai  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.fixture
def clean_environment():
    """Provide a clean environment for testing."""
    # Store original environment
    original_env = os.environ.get("FAST_CREWAI_ACCELERATION")
    original_modules = {}

    # Modules that might be affected by testing
    test_modules = [
        "fast_crewai.shim",
        "crewai.memory.storage.rag_storage",
        "crewai.tools.structured_tool",
        "crewai.task",
        "crewai.crew",
    ]

    for module in test_modules:
        if module in sys.modules:
            original_modules[module] = sys.modules[module]

    yield

    # Restore environment
    if original_env is None:
        os.environ.pop("FAST_CREWAI_ACCELERATION", None)
    else:
        os.environ["FAST_CREWAI_ACCELERATION"] = original_env

    # Restore modules
    for module, mod_obj in original_modules.items():
        sys.modules[module] = mod_obj


@pytest.fixture
def memory_storage():
    """Provide a memory storage instance for testing."""
    from fast_crewai import RustMemoryStorage

    return RustMemoryStorage()


@pytest.fixture
def tool_executor():
    """Provide a tool executor instance for testing."""
    from fast_crewai import RustToolExecutor

    return RustToolExecutor()


@pytest.fixture
def task_executor():
    """Provide a task executor instance for testing."""
    from fast_crewai import RustTaskExecutor

    return RustTaskExecutor()


@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return [
        "Document about artificial intelligence and machine learning",
        "Text discussing automation in manufacturing",
        "Research paper on neural networks and deep learning",
        "Article about robotics and computer vision",
        "Study on natural language processing applications",
    ]


@pytest.fixture
def sample_metadata():
    """Provide sample metadata for testing."""
    return [
        {"topic": "AI", "category": "research", "priority": "high"},
        {"topic": "automation", "category": "industry", "priority": "medium"},
        {"topic": "ML", "category": "research", "priority": "high"},
        {"topic": "robotics", "category": "engineering", "priority": "medium"},
        {"topic": "NLP", "category": "research", "priority": "high"},
    ]


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower() or "crewai" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)

        # Mark performance tests
        if "performance" in item.nodeid.lower() or "benchmark" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)

        # Mark slow tests
        if "slow" in item.nodeid.lower() or "large" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)

        # Mark tests that require Rust
        if "rust" in item.nodeid.lower() and "fallback" not in item.nodeid.lower():
            item.add_marker(pytest.mark.rust_required)


def pytest_runtest_setup(item):
    """Setup for individual test runs."""
    # Skip tests that require Rust if it's not available
    if item.get_closest_marker("rust_required"):
        try:
            from fast_crewai import is_rust_available

            if not is_rust_available():
                pytest.skip("Rust acceleration not available")
        except ImportError:
            pytest.skip("fast_crewai package not available")

    # Skip integration tests if CrewAI is not available
    if item.get_closest_marker("integration"):
        try:
            import crewai  # noqa: F401
        except ImportError:
            pytest.skip("CrewAI not available for integration testing")


# Custom pytest command line options
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )
    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="run performance tests",
    )


def _configure_markers(config):
    """Configure test collection based on command line options."""
    if not config.option.run_slow:
        config.option.markexpr = "not slow"

    if not config.option.run_integration:
        if config.option.markexpr:
            config.option.markexpr += " and not integration"
        else:
            config.option.markexpr = "not integration"

    if not config.option.run_performance:
        if config.option.markexpr:
            config.option.markexpr += " and not performance"
        else:
            config.option.markexpr = "not performance"

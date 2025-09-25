"""
Test configuration and fixtures for quake-cli.
"""

import asyncio

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "hypothesis: mark test as property-based test")
    config.addinivalue_line("markers", "asyncio: mark test as async test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--run-integration"):
        # Run all tests including integration
        return

    # Skip integration tests by default
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_data():
    """Provide sample data for testing."""
    return {
        "test_records": [
            {"id": 1, "name": "Test Item 1", "active": True},
            {"id": 2, "name": "Test Item 2", "active": False},
            {"id": 3, "name": "Test Item 3", "active": True},
        ]
    }

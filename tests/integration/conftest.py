"""
Configuration for integration tests.

This module provides shared fixtures and configuration for integration tests
that make real API calls to the GeoNet service.
"""



def pytest_configure(config):
    """Configure pytest for integration tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (real API calls)"
    )


# @pytest.fixture(scope="session", autouse=True)
# def integration_test_setup():
#     """Set up integration test environment."""
#     # This fixture runs once per test session
#     # Could be used to verify API connectivity, set up test data, etc.
#     print("\n🌐 Running integration tests against live GeoNet API")
#     yield
#     print("\n✅ Integration tests completed")


# Mark all tests in this directory as integration tests
# pytestmark = pytest.mark.integration

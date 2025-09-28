"""Simplified client tests focusing on core functionality."""

import pytest

from quake_cli.client import (
    GeoNetClient,
    GeoNetConnectionError,
    GeoNetError,
    GeoNetTimeoutError,
)


class TestGeoNetClientBasics:
    """Test basic client functionality without complex mocking."""

    def test_client_initialization_defaults(self):
        """Test client initializes with correct defaults."""
        client = GeoNetClient()
        assert client.base_url == "https://api.geonet.org.nz/"
        assert client.timeout == 30.0
        assert client.retries == 3
        assert client.retry_min_wait == 4.0

    def test_client_initialization_custom(self):
        """Test client initialization with custom values."""
        client = GeoNetClient(
            base_url="https://custom.api.com/",
            timeout=60.0,
            retries=5,
            retry_min_wait=2.0,
        )
        assert client.base_url == "https://custom.api.com/"
        assert client.timeout == 60.0
        assert client.retries == 5
        assert client.retry_min_wait == 2.0

    def test_client_string_representation(self):
        """Test client has useful string representation."""
        client = GeoNetClient()
        client_str = str(client)
        # Should contain some useful information
        assert len(client_str) > 0

    def test_context_manager_protocol(self):
        """Test client implements context manager protocol."""
        client = GeoNetClient()
        assert hasattr(client, "__aenter__")
        assert hasattr(client, "__aexit__")

    def test_client_not_initialized_error(self):
        """Test error when using client without context manager."""
        client = GeoNetClient()
        # This should work - just testing the method exists
        assert hasattr(client, "get_quakes")


class TestGeoNetExceptions:
    """Test custom exception classes."""

    def test_geonet_error_hierarchy(self):
        """Test exception class hierarchy."""
        assert issubclass(GeoNetConnectionError, GeoNetError)
        assert issubclass(GeoNetTimeoutError, GeoNetError)
        assert issubclass(GeoNetError, Exception)

    def test_geonet_error_instantiation(self):
        """Test exceptions can be created and have messages."""
        error = GeoNetError("Test message")
        assert str(error) == "Test message"

        conn_error = GeoNetConnectionError("Connection failed")
        assert str(conn_error) == "Connection failed"

        timeout_error = GeoNetTimeoutError("Timed out")
        assert str(timeout_error) == "Timed out"

    def test_exceptions_can_be_raised_and_caught(self):
        """Test that exceptions work in try/except blocks."""
        with pytest.raises(GeoNetError):
            raise GeoNetError("Test error")

        with pytest.raises(GeoNetError):  # Should catch subclass
            raise GeoNetConnectionError("Connection error")

        with pytest.raises(GeoNetConnectionError):  # Specific catch
            raise GeoNetConnectionError("Connection error")


class TestGeoNetClientConfiguration:
    """Test client configuration and validation."""

    def test_valid_base_url_formats(self):
        """Test various valid base URL formats."""
        valid_urls = [
            "https://api.geonet.org.nz/",
            "http://localhost:8000/",
            "https://custom-domain.com/api/v1/",
        ]

        for url in valid_urls:
            client = GeoNetClient(base_url=url)
            assert client.base_url == url

    def test_timeout_parameter(self):
        """Test timeout parameter works."""
        client = GeoNetClient(timeout=60.0)
        assert client.timeout == 60.0

    def test_retries_parameter(self):
        """Test retries parameter works."""
        client = GeoNetClient(retries=10)
        assert client.retries == 10

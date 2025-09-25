"""Test GeoNet API client."""

import os
from unittest.mock import patch

import httpx
import pytest
from pytest_httpx import HTTPXMock

from quake_cli.client import (
    GeoNetAPIError,
    GeoNetClient,
    GeoNetConnectionError,
    GeoNetError,
    GeoNetTimeoutError,
)
from quake_cli.models import QuakeFeature, QuakeResponse


class TestGeoNetClient:
    """Test GeoNetClient initialization and configuration."""

    def test_default_initialization(self):
        """Test client initialization with default values."""
        client = GeoNetClient()

        assert client.base_url == "https://api.geonet.org.nz/"
        assert client.timeout == 30.0
        assert client.retries == 3
        assert client.retry_min_wait == 4.0
        assert client.retry_max_wait == 10.0

    def test_custom_initialization(self):
        """Test client initialization with custom values."""
        client = GeoNetClient(
            base_url="https://test.api.com/",
            timeout=60.0,
            retries=5,
            retry_min_wait=2.0,
            retry_max_wait=20.0,
        )

        assert client.base_url == "https://test.api.com/"
        assert client.timeout == 60.0
        assert client.retries == 5
        assert client.retry_min_wait == 2.0
        assert client.retry_max_wait == 20.0

    def test_environment_variable_initialization(self):
        """Test client initialization from environment variables."""
        env_vars = {
            "GEONET_API_URL": "https://env.api.com/",
            "GEONET_TIMEOUT": "45",
            "GEONET_RETRIES": "4",
            "GEONET_RETRY_MIN_WAIT": "3",
            "GEONET_RETRY_MAX_WAIT": "15",
        }

        with patch.dict(os.environ, env_vars):
            client = GeoNetClient()

        assert client.base_url == "https://env.api.com/"
        assert client.timeout == 45.0
        assert client.retries == 4
        assert client.retry_min_wait == 3.0
        assert client.retry_max_wait == 15.0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        client = GeoNetClient()

        async with client as c:
            assert c.client is not None
            assert isinstance(c.client, httpx.AsyncClient)
            assert c.client.base_url == "https://api.geonet.org.nz/"
            assert c.client.timeout.pool == 30.0

        # Client should be closed after context exit
        # Note: We can't easily test this without accessing private attributes

    @pytest.mark.asyncio
    async def test_request_without_context_manager(self):
        """Test that requests fail without context manager."""
        client = GeoNetClient()

        with pytest.raises(GeoNetError, match="Client not initialized"):
            await client.get_quakes()


class TestGeoNetClientRequests:
    """Test GeoNet API client HTTP requests."""

    @pytest.fixture
    def sample_quake_response(self):
        """Sample quake response data."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "publicID": "2024p123456",
                        "time": "2024-01-15T10:30:00.000Z",
                        "depth": 5.5,
                        "magnitude": 4.2,
                        "locality": "10 km north of Wellington",
                        "MMI": 4,
                        "quality": "best",
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [174.7633, -36.8485, 5.5],
                    },
                }
            ],
        }

    @pytest.fixture
    def sample_quake_feature(self):
        """Sample single quake feature data."""
        return {
            "type": "Feature",
            "properties": {
                "publicID": "2024p123456",
                "time": "2024-01-15T10:30:00.000Z",
                "depth": 5.5,
                "magnitude": 4.2,
                "locality": "10 km north of Wellington",
                "MMI": 4,
                "quality": "best",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [174.7633, -36.8485, 5.5],
            },
        }

    @pytest.mark.asyncio
    async def test_get_quakes_success(
        self, httpx_mock: HTTPXMock, sample_quake_response
    ):
        """Test successful get_quakes request."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake",
            json=sample_quake_response,
        )

        async with GeoNetClient() as client:
            response = await client.get_quakes()

        assert isinstance(response, QuakeResponse)
        assert len(response.features) == 1
        assert response.features[0].properties.publicID == "2024p123456"
        assert response.features[0].properties.magnitude == 4.2

    @pytest.mark.asyncio
    async def test_get_quakes_with_mmi_filter(
        self, httpx_mock: HTTPXMock, sample_quake_response
    ):
        """Test get_quakes with MMI filter."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake?MMI=4",
            json=sample_quake_response,
        )

        async with GeoNetClient() as client:
            response = await client.get_quakes(mmi=4)

        assert len(response.features) == 1

    @pytest.mark.asyncio
    async def test_get_quakes_with_limit(
        self, httpx_mock: HTTPXMock, sample_quake_response
    ):
        """Test get_quakes with client-side limit."""
        # Add multiple features to test limiting
        sample_quake_response["features"] = sample_quake_response["features"] * 5

        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake",
            json=sample_quake_response,
        )

        async with GeoNetClient() as client:
            response = await client.get_quakes(limit=2)

        assert len(response.features) == 2

    @pytest.mark.asyncio
    async def test_get_quakes_invalid_mmi(self):
        """Test get_quakes with invalid MMI value."""
        async with GeoNetClient() as client:
            with pytest.raises(ValueError, match="MMI must be between -1 and 12"):
                await client.get_quakes(mmi=15)

            with pytest.raises(ValueError, match="MMI must be between -1 and 12"):
                await client.get_quakes(mmi=-5)

    @pytest.mark.asyncio
    async def test_get_quake_success(self, httpx_mock: HTTPXMock, sample_quake_feature):
        """Test successful get_quake request."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake/2024p123456",
            json=sample_quake_feature,
        )

        async with GeoNetClient() as client:
            feature = await client.get_quake("2024p123456")

        assert isinstance(feature, QuakeFeature)
        assert feature.properties.publicID == "2024p123456"
        assert feature.properties.magnitude == 4.2

    @pytest.mark.asyncio
    async def test_get_quake_not_found(self, httpx_mock: HTTPXMock):
        """Test get_quake with non-existent earthquake."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake/nonexistent",
            status_code=404,
            text="Not Found",
        )

        async with GeoNetClient() as client:
            with pytest.raises(GeoNetError, match="Earthquake nonexistent not found"):
                await client.get_quake("nonexistent")

    @pytest.mark.asyncio
    async def test_get_quake_empty_id(self):
        """Test get_quake with empty ID."""
        async with GeoNetClient() as client:
            with pytest.raises(ValueError, match="public_id cannot be empty"):
                await client.get_quake("")

            with pytest.raises(ValueError, match="public_id cannot be empty"):
                await client.get_quake("   ")

    @pytest.mark.asyncio
    async def test_get_quake_history_success(self, httpx_mock: HTTPXMock):
        """Test successful get_quake_history request."""
        history_data = [
            {"version": 1, "time": "2024-01-15T10:30:00.000Z", "latitude": -36.8485},
            {"version": 2, "time": "2024-01-15T10:31:00.000Z", "latitude": -36.8486},
        ]

        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake/history/2024p123456",
            json=history_data,
        )

        async with GeoNetClient() as client:
            history = await client.get_quake_history("2024p123456")

        assert isinstance(history, list)
        assert len(history) == 2
        assert history[0]["version"] == 1

    @pytest.mark.asyncio
    async def test_get_quake_history_not_found(self, httpx_mock: HTTPXMock):
        """Test get_quake_history with non-existent earthquake."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake/history/nonexistent",
            status_code=404,
            text="Not Found",
        )

        async with GeoNetClient() as client:
            with pytest.raises(
                GeoNetError, match="Earthquake history for nonexistent not found"
            ):
                await client.get_quake_history("nonexistent")

    @pytest.mark.asyncio
    async def test_get_quake_stats_success(self, httpx_mock: HTTPXMock):
        """Test successful get_quake_stats request."""
        stats_data = {
            "total_count": 150,
            "period": "24 hours",
            "max_magnitude": 5.2,
            "avg_magnitude": 3.4,
        }

        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake/stats",
            json=stats_data,
        )

        async with GeoNetClient() as client:
            stats = await client.get_quake_stats()

        assert stats["total_count"] == 150
        assert stats["period"] == "24 hours"

    @pytest.mark.asyncio
    async def test_search_quakes_with_filters(self, httpx_mock: HTTPXMock):
        """Test search_quakes with various filters."""
        # Create response with multiple earthquakes of different magnitudes
        features = []
        for i, magnitude in enumerate([3.5, 4.2, 5.1, 2.8], 1):
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "publicID": f"2024p{i:06d}",
                        "time": "2024-01-15T10:30:00.000Z",
                        "depth": 5.5,
                        "magnitude": magnitude,
                        "locality": "Wellington",
                        "MMI": 4,
                        "quality": "best",
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [174.7633, -36.8485, 5.5],
                    },
                }
            )

        response_data = {"type": "FeatureCollection", "features": features}

        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake",
            json=response_data,
        )

        async with GeoNetClient() as client:
            # Test magnitude filtering
            response = await client.search_quakes(min_magnitude=4.0)

        assert len(response.features) == 2  # 4.2 and 5.1
        assert all(f.properties.magnitude >= 4.0 for f in response.features)

    @pytest.mark.asyncio
    async def test_health_check_success(self, httpx_mock: HTTPXMock):
        """Test successful health check."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/",
            json={"status": "ok"},
        )

        async with GeoNetClient() as client:
            is_healthy = await client.health_check()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, httpx_mock: HTTPXMock):
        """Test health check failure."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/",
            status_code=500,
        )

        async with GeoNetClient() as client:
            is_healthy = await client.health_check()

        assert is_healthy is False


class TestGeoNetClientErrorHandling:
    """Test error handling in GeoNet client."""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        with patch(
            "httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection failed")
        ):
            async with GeoNetClient() as client:
                with pytest.raises(GeoNetConnectionError, match="Connection failed"):
                    await client.get_quakes()

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        with patch(
            "httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Timeout")
        ):
            async with GeoNetClient() as client:
                with pytest.raises(GeoNetTimeoutError, match="Request timed out"):
                    await client.get_quakes()

    @pytest.mark.asyncio
    async def test_http_status_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP status errors."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake",
            status_code=500,
            text="Internal Server Error",
        )

        async with GeoNetClient() as client:
            with pytest.raises(GeoNetAPIError, match="API returned 500"):
                await client.get_quakes()

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake",
            content=b"invalid json",
        )

        async with GeoNetClient() as client:
            with pytest.raises(GeoNetError, match="Unexpected error"):
                await client.get_quakes()

    @pytest.mark.asyncio
    async def test_invalid_data_structure(self, httpx_mock: HTTPXMock):
        """Test handling of invalid data structure."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.geonet.org.nz/quake",
            json={"invalid": "structure"},
        )

        async with GeoNetClient() as client:
            with pytest.raises(GeoNetError, match="Failed to parse"):
                await client.get_quakes()


class TestGeoNetClientRetryLogic:
    """Test retry logic configuration."""

    def test_retry_decorator_creation(self):
        """Test that retry decorator is created with correct configuration."""
        client = GeoNetClient(retries=5, retry_min_wait=2.0, retry_max_wait=20.0)
        decorator = client._create_retry_decorator()

        # Test that decorator is created (basic smoke test)
        assert decorator is not None


class TestGeoNetErrorClasses:
    """Test custom error classes."""

    def test_geonet_error(self):
        """Test base GeoNetError."""
        error = GeoNetError("Test error", status_code=400)
        assert str(error) == "Test error"
        assert error.status_code == 400

    def test_geonet_connection_error(self):
        """Test GeoNetConnectionError inherits from GeoNetError."""
        error = GeoNetConnectionError("Connection failed")
        assert isinstance(error, GeoNetError)
        assert str(error) == "Connection failed"

    def test_geonet_timeout_error(self):
        """Test GeoNetTimeoutError inherits from GeoNetError."""
        error = GeoNetTimeoutError("Timeout")
        assert isinstance(error, GeoNetError)
        assert str(error) == "Timeout"

    def test_geonet_api_error(self):
        """Test GeoNetAPIError inherits from GeoNetError."""
        error = GeoNetAPIError("API error", status_code=500)
        assert isinstance(error, GeoNetError)
        assert str(error) == "API error"
        assert error.status_code == 500

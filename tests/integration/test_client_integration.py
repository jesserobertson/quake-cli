"""
Integration tests for GeoNet client using generated mock data.

These tests use real API response data saved as mocks to test the complete
client functionality offline while maintaining realistic data.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response

from gnet.client import GeoNetClient
from gnet.models import cap, intensity, quake, volcano
from tests.mocks.loader import get_test_earthquake_id, mock_loader


class TestClientIntegration:
    """Integration tests for GeoNet client with mock data."""

    @pytest.fixture
    def mock_response(self):
        """Create a mock httpx.Response."""

        def _create_mock_response(data, status_code=200):
            mock_resp = AsyncMock(spec=Response)
            mock_resp.status_code = status_code
            mock_resp.json.return_value = data
            mock_resp.text = str(data) if isinstance(data, dict) else data
            return mock_resp

        return _create_mock_response

    @pytest.mark.asyncio
    async def test_get_quakes_integration(self, mock_response):
        """Test getting earthquakes with real mock data."""
        # Load real API response data
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None, "Mock data for quakes_all not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_quakes()

                assert result.is_ok()
                response = result.unwrap()
                assert isinstance(response, quake.Response)
                assert len(response.features) > 0

                # Verify structure of first earthquake
                feature = response.features[0]
                assert isinstance(feature, quake.Feature)
                assert feature.properties.publicID
                assert feature.properties.magnitude.value > 0
                assert feature.properties.time.origin
                assert feature.geometry.longitude
                assert feature.geometry.latitude

    @pytest.mark.asyncio
    async def test_get_quakes_with_mmi_filter(self, mock_response):
        """Test getting earthquakes with MMI filter using mock data."""
        mock_data = mock_loader.get_mock_data("quakes_mmi4")
        assert mock_data is not None, "Mock data for quakes_mmi4 not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_quakes(mmi=4)

                assert result.is_ok()
                response = result.unwrap()
                assert len(response.features) > 0

                # All earthquakes should have significant intensity
                for feature in response.features:
                    if feature.properties.intensity:
                        assert feature.properties.intensity.mmi >= 4

    @pytest.mark.asyncio
    async def test_get_quake_by_id(self, mock_response):
        """Test getting a specific earthquake by ID."""
        # Use the first earthquake from our mock data
        earthquake_id = get_test_earthquake_id()
        assert earthquake_id is not None, "No test earthquake ID available"

        # For single earthquake, we'll use the same structure but with one feature
        mock_data = mock_loader.get_mock_data("quakes_all")
        single_quake_data = {
            "type": "FeatureCollection",
            "features": [mock_data["features"][0]],  # Just the first earthquake
        }

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(single_quake_data)

            async with GeoNetClient() as client:
                result = await client.get_quake(earthquake_id)

                assert result.is_ok()
                feature = result.unwrap()
                assert isinstance(feature, quake.Feature)
                assert feature.properties.publicID == earthquake_id

    @pytest.mark.asyncio
    async def test_get_quake_stats(self, mock_response):
        """Test getting earthquake statistics."""
        mock_data = mock_loader.get_mock_data("quake_stats")
        assert mock_data is not None, "Mock data for quake_stats not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_quake_stats()

                assert result.is_ok()
                stats = result.unwrap()
                assert isinstance(stats, dict)

                # Verify expected statistics structure
                assert "magnitudeCount" in stats
                assert "rate" in stats

    @pytest.mark.asyncio
    async def test_get_intensity_reported(self, mock_response):
        """Test getting reported intensity data."""
        mock_data = mock_loader.get_mock_data("intensity_reported")
        assert mock_data is not None, "Mock data for intensity_reported not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_intensity("reported")

                assert result.is_ok()
                response = result.unwrap()
                assert isinstance(response, intensity.Response)

    @pytest.mark.asyncio
    async def test_get_intensity_measured(self, mock_response):
        """Test getting measured intensity data."""
        mock_data = mock_loader.get_mock_data("intensity_measured")
        assert mock_data is not None, "Mock data for intensity_measured not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_intensity("measured")

                assert result.is_ok()
                response = result.unwrap()
                assert isinstance(response, intensity.Response)
                assert len(response.features) > 0

    @pytest.mark.asyncio
    async def test_get_volcano_alerts(self, mock_response):
        """Test getting volcano alert data."""
        mock_data = mock_loader.get_mock_data("volcano_alerts")
        assert mock_data is not None, "Mock data for volcano_alerts not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_volcano_alerts()

                assert result.is_ok()
                response = result.unwrap()
                assert isinstance(response, volcano.Response)
                assert len(response.features) > 0

                # Verify volcano alert structure
                for feature in response.features:
                    assert feature.properties.id  # volcano ID
                    assert feature.properties.title  # volcano name
                    assert feature.properties.level >= 0  # alert level

    @pytest.mark.asyncio
    async def test_get_cap_feed(self, mock_response):
        """Test getting CAP alert feed."""
        mock_data = mock_loader.get_mock_data("cap_feed")
        assert mock_data is not None, "Mock data for cap_feed not found"

        # CAP feed returns XML, so we need to mock the text response
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <id>https://api.geonet.org.nz/cap/1.2/GPA1.0/feed/atom1.0/quake</id>
    <title>CAP quakes</title>
    <updated>2025-09-28T10:30:00Z</updated>
    <author>
        <name>GNS Science (GeoNet)</name>
        <email>info@geonet.org.nz</email>
    </author>
</feed>"""

        mock_resp = AsyncMock(spec=Response)
        mock_resp.status_code = 200
        mock_resp.text = mock_xml

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_resp

            async with GeoNetClient() as client:
                result = await client.get_cap_feed()

                assert result.is_ok()
                cap_feed = result.unwrap()
                assert isinstance(cap_feed, cap.CapFeed)

    @pytest.mark.asyncio
    async def test_search_quakes_with_filters(self, mock_response):
        """Test searching earthquakes with magnitude and MMI filters."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None, "Mock data for quakes_all not found"

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.search_quakes(min_magnitude=3.0, limit=5)

                assert result.is_ok()
                response = result.unwrap()
                assert len(response.features) <= 5

                # All returned earthquakes should meet magnitude criteria
                for feature in response.features:
                    assert feature.properties.magnitude.value >= 3.0

    @pytest.mark.asyncio
    async def test_health_check(self, mock_response):
        """Test API health check."""
        mock_data = mock_loader.get_mock_data("quakes_all")

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.health_check()

                assert result.is_ok()
                assert result.unwrap() is True

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_response):
        """Test client error handling with bad responses."""
        # Test 404 error
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response({}, status_code=404)

            async with GeoNetClient() as client:
                result = await client.get_quakes()

                assert result.is_err()
                error_msg = result.unwrap_err()
                assert "404" in error_msg


class TestClientWithRealDataValidation:
    """Tests that validate our mock data against expected model structures."""

    def test_mock_data_completeness(self):
        """Test that all expected mock data files exist."""
        expected_mocks = [
            "quakes_all",
            "quakes_mmi4",
            "quake_stats",
            "intensity_reported",
            "intensity_measured",
            "volcano_alerts",
            "cap_feed",
        ]

        available_mocks = mock_loader.list_available_mocks()

        for expected in expected_mocks:
            assert expected in available_mocks, f"Missing mock data: {expected}"

    def test_quake_data_structure_validation(self):
        """Test that earthquake mock data matches expected structure."""
        for mock_type in ["quakes_all", "quakes_mmi4"]:
            data = mock_loader.get_mock_data(mock_type)
            assert data is not None

            # Validate GeoJSON structure
            assert data["type"] == "FeatureCollection"
            assert "features" in data
            assert len(data["features"]) > 0

            # Validate first feature structure
            feature_data = data["features"][0]
            assert feature_data["type"] == "Feature"
            assert "properties" in feature_data
            assert "geometry" in feature_data

            # Validate properties
            props = feature_data["properties"]
            assert "publicID" in props
            assert "time" in props
            assert "magnitude" in props
            assert "depth" in props
            assert "locality" in props

    def test_model_parsing_with_mock_data(self):
        """Test that mock data can be parsed by our Pydantic models."""
        # Test quake response parsing
        quakes_data = mock_loader.get_mock_data("quakes_all")

        # Convert to our model format (simulate what client.py does)
        features = []
        for feature_data in quakes_data["features"][:1]:  # Just test first one
            props = feature_data["properties"]
            coords = feature_data["geometry"]["coordinates"]

            # This tests the same parsing logic as in client.py
            from datetime import datetime

            from gnet.models.common import Point

            properties = quake.Properties.from_legacy_api(
                publicID=props["publicID"],
                time=datetime.fromisoformat(props["time"].replace("Z", "+00:00")),
                magnitude=props["magnitude"],
                depth=props["depth"],
                locality=props["locality"],
                MMI=props.get("MMI"),
                quality=props["quality"],
                longitude=coords[0],
                latitude=coords[1],
            )

            feature = quake.Feature(
                properties=properties, geometry=Point(coordinates=coords)
            )
            features.append(feature)

        response = quake.Response(features=features)

        # Verify the parsing worked
        assert len(response.features) == 1
        assert response.features[0].properties.publicID
        assert response.features[0].properties.magnitude.value > 0

"""
Integration tests for GeoNet API.

These tests make real API calls to the GeoNet service to ensure
the client works correctly with the live API.
"""

import asyncio
from datetime import datetime, timedelta

import pytest

from quake_cli.client import GeoNetClient, GeoNetError
from quake_cli.models import QuakeFeature, QuakeResponse


class TestGeoNetAPIIntegration:
    """Test real API calls to GeoNet service."""

    @pytest.fixture
    def client(self):
        """Create a GeoNet client for testing."""
        return GeoNetClient(timeout=30.0)  # Longer timeout for real API

    @pytest.mark.asyncio
    async def test_api_health_check(self, client):
        """Test that the GeoNet API is reachable."""
        async with client:
            is_healthy = await client.health_check()
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_get_recent_quakes(self, client):
        """Test getting recent earthquakes."""
        async with client:
            response = await client.get_quakes(limit=5)

            # Verify response structure
            assert isinstance(response, QuakeResponse)
            assert response.type == "FeatureCollection"
            assert isinstance(response.features, list)
            assert len(response.features) <= 5

            # If there are earthquakes, verify their structure
            if response.features:
                quake = response.features[0]
                assert isinstance(quake, QuakeFeature)
                assert quake.type == "Feature"
                assert hasattr(quake.properties, 'publicID')
                assert hasattr(quake.properties, 'time')
                assert hasattr(quake.properties, 'magnitude')
                assert hasattr(quake.properties, 'depth')
                assert hasattr(quake.geometry, 'coordinates')

                # Verify coordinate structure
                coords = quake.geometry.coordinates
                assert len(coords) >= 2  # At least lon, lat
                assert isinstance(coords[0], (int, float))  # longitude
                assert isinstance(coords[1], (int, float))  # latitude

    @pytest.mark.asyncio
    async def test_get_quakes_with_mmi_filter(self, client):
        """Test getting earthquakes with MMI filter."""
        async with client:
            # Get earthquakes with MMI >= 3 (should be felt)
            response = await client.get_quakes(mmi=3, limit=10)

            assert isinstance(response, QuakeResponse)
            # MMI filtered results might be empty, but response should be valid
            assert response.type == "FeatureCollection"
            assert isinstance(response.features, list)

    @pytest.mark.asyncio
    async def test_search_quakes_with_magnitude_filter(self, client):
        """Test searching earthquakes with magnitude filter."""
        async with client:
            # Get earthquakes with magnitude >= 4.0
            response = await client.search_quakes(min_magnitude=4.0, limit=15)

            assert isinstance(response, QuakeResponse)
            assert response.type == "FeatureCollection"

            # Verify all returned earthquakes meet the magnitude criteria
            for quake in response.features:
                assert quake.properties.magnitude >= 4.0

    @pytest.mark.asyncio
    async def test_get_specific_earthquake(self, client):
        """Test getting a specific earthquake by ID."""
        async with client:
            # First get some recent earthquakes to get a valid ID
            recent = await client.get_quakes(limit=5)

            if recent.features:
                # Test getting the first earthquake by ID
                earthquake_id = recent.features[0].properties.publicID
                specific_quake = await client.get_quake(earthquake_id)

                assert isinstance(specific_quake, QuakeFeature)
                assert specific_quake.properties.publicID == earthquake_id
                assert specific_quake.type == "Feature"

    @pytest.mark.asyncio
    async def test_get_earthquake_history(self, client):
        """Test getting earthquake location history."""
        async with client:
            # Get recent earthquakes to find one with potential history
            recent = await client.get_quakes(limit=10)

            if recent.features:
                # Test history for the first earthquake
                earthquake_id = recent.features[0].properties.publicID
                try:
                    history = await client.get_quake_history(earthquake_id)
                    # History might be empty but should be a list
                    assert isinstance(history, list)
                except GeoNetError:
                    # Some earthquakes might not have history data
                    # This is acceptable for the integration test
                    pass

    @pytest.mark.asyncio
    async def test_get_earthquake_stats(self, client):
        """Test getting earthquake statistics."""
        async with client:
            stats = await client.get_quake_stats()

            # Verify stats structure
            assert isinstance(stats, dict)
            # Stats should contain some summary information
            assert len(stats) > 0

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test that API errors are handled properly."""
        async with client:
            # Test with invalid earthquake ID
            with pytest.raises(GeoNetError):
                await client.get_quake("invalid_earthquake_id_12345")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test that the client can handle concurrent requests."""
        async with client:
            # Make multiple concurrent requests
            tasks = [
                client.get_quakes(limit=3),
                client.get_quakes(limit=3),
                client.health_check(),
            ]

            results = await asyncio.gather(*tasks)

            # Verify all requests succeeded
            assert len(results) == 3
            assert isinstance(results[0], QuakeResponse)
            assert isinstance(results[1], QuakeResponse)
            assert isinstance(results[2], bool)

    @pytest.mark.asyncio
    async def test_data_freshness(self, client):
        """Test that earthquake data is reasonably fresh."""
        async with client:
            response = await client.get_quakes(limit=5)

            if response.features:
                # Check that at least one earthquake is from the last 30 days
                now = datetime.now()
                thirty_days_ago = now - timedelta(days=30)

                recent_found = False
                for quake in response.features:
                    quake_time = quake.properties.time
                    if isinstance(quake_time, str):
                        # Parse ISO timestamp
                        quake_time = datetime.fromisoformat(quake_time.replace('Z', '+00:00'))

                    # Convert to naive datetime for comparison
                    if quake_time.tzinfo:
                        quake_time = quake_time.replace(tzinfo=None)

                    if quake_time >= thirty_days_ago:
                        recent_found = True
                        break

                # Should have at least one recent earthquake
                assert recent_found, "No earthquakes found from the last 30 days"


class TestGeoNetAPIRobustness:
    """Test API robustness and edge cases."""

    @pytest.fixture
    def client(self):
        """Create a GeoNet client with shorter timeout for robustness tests."""
        return GeoNetClient(timeout=10.0, retries=2)

    @pytest.mark.asyncio
    async def test_large_limit_request(self, client):
        """Test requesting a large number of earthquakes."""
        async with client:
            # Request up to 100 earthquakes (API might limit this)
            response = await client.get_quakes(limit=100)

            assert isinstance(response, QuakeResponse)
            assert len(response.features) <= 100
            # Should get at least some earthquakes (unless API is empty)
            # We won't assert a minimum since the API might have limits

    @pytest.mark.asyncio
    async def test_boundary_magnitude_values(self, client):
        """Test edge cases for magnitude filtering."""
        async with client:
            # Test very high magnitude (unlikely to find matches)
            response = await client.search_quakes(min_magnitude=8.0, limit=5)
            assert isinstance(response, QuakeResponse)
            # Might be empty, but should be valid response

            # Test reasonable magnitude range
            response = await client.search_quakes(
                min_magnitude=2.0, max_magnitude=10.0, limit=10
            )
            assert isinstance(response, QuakeResponse)

            # Verify magnitude constraints
            for quake in response.features:
                assert 2.0 <= quake.properties.magnitude <= 10.0

    @pytest.mark.asyncio
    async def test_client_reuse(self, client):
        """Test that the client can be reused across multiple sessions."""
        # First session
        async with client:
            response1 = await client.get_quakes(limit=2)
            assert isinstance(response1, QuakeResponse)

        # Second session - should work fine
        async with client:
            response2 = await client.get_quakes(limit=2)
            assert isinstance(response2, QuakeResponse)

        # Responses might be different due to timing, but both should be valid
        assert response1.type == response2.type == "FeatureCollection"
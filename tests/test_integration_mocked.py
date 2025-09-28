"""
Integration tests using real API mock data.

These tests use pytest.mark.integration to mark them as integration tests
and use real API response data saved as mocks to test offline functionality.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response
from typer.testing import CliRunner

from gnet.cli.main import app
from gnet.client import GeoNetClient
from gnet.models import quake, volcano
from tests.mocks.loader import mock_loader


@pytest.mark.integration
class TestIntegrationWithMocks:
    """Integration tests using mock data from real API responses."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

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

    def _convert_mock_to_legacy_format(self, mock_data):
        """Convert new model format back to legacy API format for client testing."""
        if not isinstance(mock_data, dict) or "features" not in mock_data:
            return mock_data

        legacy_features = []
        for feature in mock_data["features"]:
            # Convert new model format back to what the API originally returned
            props = feature["properties"]
            geom = feature["geometry"]

            legacy_props = {
                "publicID": props["publicID"],
                "time": props["time"]["origin"],  # Use the datetime string
                "magnitude": props["magnitude"]["value"],
                "depth": abs(props["location"]["elevation"])
                if props["location"]["elevation"]
                else 0,
                "locality": props["location"]["locality"],
                "quality": props["quality"]["level"],
            }

            # Add MMI if intensity exists
            if props.get("intensity"):
                legacy_props["MMI"] = props["intensity"]["mmi"]

            legacy_feature = {
                "type": "Feature",
                "properties": legacy_props,
                "geometry": {"type": "Point", "coordinates": geom["coordinates"]},
            }
            legacy_features.append(legacy_feature)

        return {"type": "FeatureCollection", "features": legacy_features}

    def test_mock_data_availability(self):
        """Test that mock data is available and complete."""
        expected_mocks = ["quakes_all", "quake_stats", "volcano_alerts", "cap_feed"]

        available_mocks = mock_loader.list_available_mocks()
        for expected in expected_mocks:
            assert expected in available_mocks, f"Missing mock data: {expected}"

        # Test that we can load each mock
        for mock_type in expected_mocks:
            data = mock_loader.get_mock_data(mock_type)
            assert data is not None, f"Could not load mock data: {mock_type}"

    @pytest.mark.asyncio
    async def test_client_with_quake_mock_data(self, mock_response):
        """Test client with real earthquake mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None

        # Convert to legacy format for client
        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            async with GeoNetClient() as client:
                result = await client.get_quakes()

                assert result.is_ok()
                response = result.unwrap()
                assert isinstance(response, quake.Response)
                assert len(response.features) > 0

                # Verify first earthquake structure
                feature = response.features[0]
                assert feature.properties.publicID
                assert feature.properties.magnitude.value > 0

    @pytest.mark.asyncio
    async def test_client_with_stats_mock_data(self, mock_response):
        """Test client with real stats mock data."""
        mock_data = mock_loader.get_mock_data("quake_stats")
        assert mock_data is not None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            async with GeoNetClient() as client:
                result = await client.get_quake_stats()

                assert result.is_ok()
                stats = result.unwrap()
                assert isinstance(stats, dict)
                assert "magnitudeCount" in stats

    @pytest.mark.asyncio
    async def test_client_with_volcano_mock_data(self, mock_response):
        """Test client with real volcano mock data."""
        mock_data = mock_loader.get_mock_data("volcano_alerts")
        assert mock_data is not None

        # Convert to legacy format
        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            async with GeoNetClient() as client:
                result = await client.get_volcano_alerts()

                assert result.is_ok()
                response = result.unwrap()
                assert isinstance(response, volcano.Response)
                assert len(response.features) > 0

    def test_cli_quake_list_with_mock_data(self, runner, mock_response):
        """Test CLI quake list command with mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None

        # Convert to legacy format
        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            result = runner.invoke(app, ["quake", "list", "--limit", "3"])

            assert result.exit_code == 0
            assert "Recent Earthquakes" in result.stdout

    def test_cli_quake_list_json_output(self, runner, mock_response):
        """Test CLI JSON output with mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None

        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            result = runner.invoke(
                app, ["quake", "list", "--format", "json", "--limit", "2"]
            )

            assert result.exit_code == 0
            # Should be valid JSON
            try:
                output_data = json.loads(result.stdout)
                assert "features" in output_data
                assert len(output_data["features"]) > 0
            except json.JSONDecodeError:
                pytest.fail("Output is not valid JSON")

    def test_cli_stats_command_with_mock_data(self, runner, mock_response):
        """Test CLI stats command with mock data."""
        mock_data = mock_loader.get_mock_data("quake_stats")
        assert mock_data is not None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            result = runner.invoke(app, ["quake", "stats"])

            assert result.exit_code == 0
            assert "magnitudeCount" in result.stdout

    def test_cli_volcano_alerts_with_mock_data(self, runner, mock_response):
        """Test CLI volcano alerts with mock data."""
        mock_data = mock_loader.get_mock_data("volcano_alerts")
        assert mock_data is not None

        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            result = runner.invoke(app, ["volcano", "alerts"])

            assert result.exit_code == 0
            assert "Volcano Alert Levels" in result.stdout

    def test_cli_health_check_with_mock_data(self, runner, mock_response):
        """Test CLI health check with mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")

        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            result = runner.invoke(app, ["quake", "health"])

            assert result.exit_code == 0
            assert "✅" in result.stdout or "healthy" in result.stdout.lower()

    def test_error_handling_with_mock_responses(self, runner, mock_response):
        """Test error handling with mock error responses."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response({}, status_code=404)

            result = runner.invoke(app, ["quake", "list"])

            assert result.exit_code == 1
            assert "Error" in result.stdout

    def test_command_aliases_with_mock_data(self, runner, mock_response):
        """Test command aliases work with mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            # Test 'q' alias for 'quake'
            result1 = runner.invoke(app, ["q", "list", "--limit", "1"])
            result2 = runner.invoke(app, ["quake", "list", "--limit", "1"])

            assert result1.exit_code == 0
            assert result2.exit_code == 0
            assert "Recent Earthquakes" in result1.stdout
            assert "Recent Earthquakes" in result2.stdout


# Tests that can run without integration mark
class TestMockDataStructure:
    """Test mock data structure and integrity (runs in regular test suite)."""

    def test_mock_files_exist(self):
        """Test that expected mock files exist."""
        expected_files = ["quakes_all", "quake_stats", "volcano_alerts"]
        available = mock_loader.list_available_mocks()

        for expected in expected_files:
            assert expected in available, f"Mock file {expected} not found"

    def test_mock_data_has_metadata(self):
        """Test that mock data includes proper metadata."""
        for mock_type in mock_loader.list_available_mocks():
            metadata = mock_loader.get_mock_metadata(mock_type)
            assert metadata is not None
            assert "generated_at" in metadata
            assert "source" in metadata
            assert metadata["source"] == "GeoNet API"

    def test_earthquake_mock_data_structure(self):
        """Test earthquake mock data has expected structure."""
        for mock_type in ["quakes_all", "quakes_mmi4"]:
            if mock_loader.is_mock_available(mock_type):
                data = mock_loader.get_mock_data(mock_type)
                assert data["type"] == "FeatureCollection"
                assert "features" in data
                assert len(data["features"]) > 0

                # Check first feature structure
                feature = data["features"][0]
                assert feature["type"] == "Feature"
                assert "properties" in feature
                assert "geometry" in feature

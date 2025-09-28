"""
Integration tests for CLI commands using generated mock data.

These tests verify the complete CLI functionality using real API response
data saved as mocks, ensuring the full command pipeline works correctly.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response
from typer.testing import CliRunner

from gnet.cli.main import app
from tests.mocks.loader import mock_loader


class TestCLIIntegration:
    """Integration tests for CLI commands with mock data."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
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

    def test_quake_list_command_integration(self, runner, mock_response):
        """Test 'gnet quake list' with real mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            result = runner.invoke(app, ["quake", "list", "--limit", "5"])

            assert result.exit_code == 0
            # Check that output contains earthquake data
            assert "Recent Earthquakes" in result.stdout

    def test_quake_list_json_output(self, runner, mock_response):
        """Test 'gnet quake list' with JSON output format."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            result = runner.invoke(app, ["quake", "list", "--format", "json"])

            assert result.exit_code == 0
            # Should be valid JSON
            try:
                output_data = json.loads(result.stdout)
                assert "features" in output_data
                assert len(output_data["features"]) > 0
            except json.JSONDecodeError:
                pytest.fail("Output is not valid JSON")

    def test_quake_stats_command_integration(self, runner, mock_response):
        """Test 'gnet quake stats' command."""
        mock_data = mock_loader.get_mock_data("quake_stats")
        assert mock_data is not None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            result = runner.invoke(app, ["quake", "stats"])

            assert result.exit_code == 0
            # Should contain statistics data
            assert "magnitudeCount" in result.stdout
            assert "rate" in result.stdout

    def test_quake_health_command_integration(self, runner, mock_response):
        """Test 'gnet quake health' command."""
        mock_data = mock_loader.get_mock_data("quakes_all")

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            result = runner.invoke(app, ["quake", "health"])

            assert result.exit_code == 0
            assert "✅" in result.stdout or "healthy" in result.stdout.lower()

    def test_volcano_alerts_command_integration(self, runner, mock_response):
        """Test 'gnet volcano alerts' command."""
        mock_data = mock_loader.get_mock_data("volcano_alerts")
        assert mock_data is not None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response(mock_data)

            result = runner.invoke(app, ["volcano", "alerts"])

            assert result.exit_code == 0
            assert "Volcano Alert Levels" in result.stdout

    def test_cap_feed_command_integration(self, runner, mock_response):
        """Test 'gnet quake cap-feed' command."""
        # CAP feed returns XML
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <id>https://api.geonet.org.nz/cap/1.2/GPA1.0/feed/atom1.0/quake</id>
    <title>CAP quakes</title>
    <updated>2025-09-28T10:30:00Z</updated>
    <author>
        <name>GNS Science (GeoNet)</name>
        <email>info@geonet.org.nz</email>
    </author>
    <entry>
        <id>geonet.org.nz/quake/2025p123456</id>
        <title>M4.2 earthquake Wellington area</title>
        <updated>2025-09-28T10:30:00Z</updated>
        <published>2025-09-28T10:25:00Z</published>
        <summary>Moderate earthquake near Wellington</summary>
    </entry>
</feed>"""

        mock_resp = AsyncMock(spec=Response)
        mock_resp.status_code = 200
        mock_resp.text = mock_xml

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_resp

            result = runner.invoke(app, ["quake", "cap-feed"])

            assert result.exit_code == 0
            assert "CAP Alert Feed" in result.stdout

    def test_error_handling_integration(self, runner, mock_response):
        """Test CLI error handling with API errors."""
        # Test 404 error
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response({}, status_code=404)

            result = runner.invoke(app, ["quake", "list"])

            assert result.exit_code == 1
            assert "Error" in result.stdout

"""Test CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from quake_cli.cli import app
from quake_cli.client import GeoNetError
from quake_cli.models import QuakeFeature, QuakeGeometry, QuakeProperties, QuakeResponse


class TestCLICommands:
    """Test CLI command functionality."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @pytest.fixture
    def sample_quake_response(self):
        """Sample QuakeResponse for testing."""
        features = [
            QuakeFeature(
                type="Feature",
                properties=QuakeProperties(
                    publicID="2024p123456",
                    time="2024-01-15T10:30:00.000Z",
                    depth=5.5,
                    magnitude=4.2,
                    locality="10 km north of Wellington",
                    MMI=4,
                    quality="best",
                ),
                geometry=QuakeGeometry(
                    type="Point",
                    coordinates=[174.7633, -36.8485, 5.5],
                ),
            ),
            QuakeFeature(
                type="Feature",
                properties=QuakeProperties(
                    publicID="2024p789012",
                    time="2024-01-16T14:45:00.000Z",
                    depth=8.2,
                    magnitude=3.8,
                    locality="Auckland",
                    MMI=None,
                    quality="preliminary",
                ),
                geometry=QuakeGeometry(
                    type="Point",
                    coordinates=[174.7645, -36.8500, 8.2],
                ),
            ),
        ]

        return QuakeResponse(type="FeatureCollection", features=features)

    @pytest.fixture
    def sample_quake_feature(self):
        """Sample QuakeFeature for testing."""
        return QuakeFeature(
            type="Feature",
            properties=QuakeProperties(
                publicID="2024p123456",
                time="2024-01-15T10:30:00.000Z",
                depth=5.5,
                magnitude=4.2,
                locality="10 km north of Wellington",
                MMI=4,
                quality="best",
            ),
            geometry=QuakeGeometry(
                type="Point",
                coordinates=[174.7633, -36.8485, 5.5],
            ),
        )

    def test_main_help(self, runner):
        """Test main help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "GeoNet Earthquake CLI" in result.stdout
        assert "Query earthquake data from GeoNet API" in result.stdout

    def test_version(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "quake-cli version" in result.stdout

    @patch("quake_cli.cli.GeoNetClient")
    def test_list_command_default(
        self, mock_client_class, runner, sample_quake_response
    ):
        """Test list command with default parameters."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "2024p123456" in result.stdout
        assert "Wellington" in result.stdout
        mock_client.search_quakes.assert_called_once_with(
            min_magnitude=None,
            max_magnitude=None,
            min_mmi=None,
            max_mmi=None,
            limit=10,
        )

    @patch("quake_cli.cli.GeoNetClient")
    def test_list_command_with_filters(
        self, mock_client_class, runner, sample_quake_response
    ):
        """Test list command with filters."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "list",
                "--limit",
                "5",
                "--min-magnitude",
                "3.0",
                "--max-magnitude",
                "5.0",
                "--min-mmi",
                "2",
                "--max-mmi",
                "6",
            ],
        )

        assert result.exit_code == 0
        mock_client.search_quakes.assert_called_once_with(
            min_magnitude=3.0,
            max_magnitude=5.0,
            min_mmi=2,
            max_mmi=6,
            limit=5,
        )

    @patch("quake_cli.cli.GeoNetClient")
    def test_list_command_with_server_mmi(
        self, mock_client_class, runner, sample_quake_response
    ):
        """Test list command with server-side MMI filter."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list", "--mmi", "4"])

        assert result.exit_code == 0
        mock_client.get_quakes.assert_called_once_with(mmi=4, limit=10)

    @patch("quake_cli.cli.GeoNetClient")
    def test_list_command_json_format(
        self, mock_client_class, runner, sample_quake_response
    ):
        """Test list command with JSON output."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list", "--format", "json"])

        assert result.exit_code == 0
        # Verify it's valid JSON
        output_data = json.loads(result.stdout)
        assert output_data["type"] == "FeatureCollection"
        assert len(output_data["features"]) == 2

    @patch("quake_cli.cli.GeoNetClient")
    def test_list_command_csv_format(
        self, mock_client_class, runner, sample_quake_response
    ):
        """Test list command with CSV output."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list", "--format", "csv"])

        assert result.exit_code == 0
        assert (
            "ID,Time,Magnitude,Depth,MMI,Quality,Location,Longitude,Latitude"
            in result.stdout
        )
        assert "2024p123456" in result.stdout

    @patch("quake_cli.cli.GeoNetClient")
    def test_list_command_empty_response(self, mock_client_class, runner):
        """Test list command with no results."""
        empty_response = QuakeResponse(type="FeatureCollection", features=[])

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = empty_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No earthquakes found" in result.stdout

    @patch("quake_cli.cli.GeoNetClient")
    def test_get_command(self, mock_client_class, runner, sample_quake_feature):
        """Test get command."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_quake.return_value = sample_quake_feature
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["get", "2024p123456"])

        assert result.exit_code == 0
        assert "2024p123456" in result.stdout
        assert "Wellington" in result.stdout
        mock_client.get_quake.assert_called_once_with("2024p123456")

    @patch("quake_cli.cli.GeoNetClient")
    def test_get_command_json_format(
        self, mock_client_class, runner, sample_quake_feature
    ):
        """Test get command with JSON output."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_quake.return_value = sample_quake_feature
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["get", "2024p123456", "--format", "json"])

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["properties"]["publicID"] == "2024p123456"

    @patch("quake_cli.cli.GeoNetClient")
    def test_history_command(self, mock_client_class, runner):
        """Test history command."""
        history_data = [
            {"version": 1, "time": "2024-01-15T10:30:00.000Z", "latitude": -36.8485},
            {"version": 2, "time": "2024-01-15T10:31:00.000Z", "latitude": -36.8486},
        ]

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_quake_history.return_value = history_data
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["history", "2024p123456"])

        assert result.exit_code == 0
        mock_client.get_quake_history.assert_called_once_with("2024p123456")

    @patch("quake_cli.cli.GeoNetClient")
    def test_stats_command(self, mock_client_class, runner):
        """Test stats command."""
        stats_data = {
            "total_count": 150,
            "period": "24 hours",
            "max_magnitude": 5.2,
            "avg_magnitude": 3.4,
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_quake_stats.return_value = stats_data
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        mock_client.get_quake_stats.assert_called_once()

    @patch("quake_cli.cli.GeoNetClient")
    def test_health_command_healthy(self, mock_client_class, runner):
        """Test health command when API is healthy."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.health_check.return_value = True
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["health"])

        assert result.exit_code == 0
        assert "✅" in result.stdout
        assert "healthy" in result.stdout

    @patch("quake_cli.cli.GeoNetClient")
    def test_health_command_unhealthy(self, mock_client_class, runner):
        """Test health command when API is unhealthy."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.health_check.return_value = False
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "❌" in result.stdout
        assert "not responding" in result.stdout

    @patch("quake_cli.cli.GeoNetClient")
    def test_output_to_file_json(
        self, mock_client_class, runner, sample_quake_response
    ):
        """Test output to file with JSON format."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = runner.invoke(
                app, ["list", "--format", "json", "--output", tmp_path]
            )

            assert result.exit_code == 0
            assert f"JSON data written to {tmp_path}" in result.stdout

            # Verify file contents
            with open(tmp_path) as f:
                data = json.load(f)
                assert data["type"] == "FeatureCollection"
        finally:
            Path(tmp_path).unlink()

    @patch("quake_cli.cli.GeoNetClient")
    def test_output_to_file_csv(self, mock_client_class, runner, sample_quake_response):
        """Test output to file with CSV format."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.return_value = sample_quake_response
        mock_client_class.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = runner.invoke(
                app, ["list", "--format", "csv", "--output", tmp_path]
            )

            assert result.exit_code == 0
            assert f"CSV data written to {tmp_path}" in result.stdout

            # Verify file contents
            with open(tmp_path) as f:
                content = f.read()
                assert (
                    "ID,Time,Magnitude,Depth,MMI,Quality,Location,Longitude,Latitude"
                    in content
                )
                assert "2024p123456" in content
        finally:
            Path(tmp_path).unlink()

    @patch("quake_cli.cli.GeoNetClient")
    def test_error_handling(self, mock_client_class, runner):
        """Test CLI error handling."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_quakes.side_effect = GeoNetError("API Error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Error: API Error" in result.stdout

    def test_verbose_flag(self, runner):
        """Test verbose flag."""
        result = runner.invoke(app, ["--verbose", "--help"])
        assert result.exit_code == 0


class TestCLIHelpers:
    """Test CLI helper functions."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        from datetime import datetime

        from quake_cli.cli import format_datetime

        dt = datetime(2024, 1, 15, 10, 30, 0)
        formatted = format_datetime(dt)
        assert formatted == "2024-01-15 10:30:00"

    def test_create_quakes_table(self):
        """Test table creation."""
        from quake_cli.cli import create_quakes_table

        feature = QuakeFeature(
            type="Feature",
            properties=QuakeProperties(
                publicID="2024p123456",
                time="2024-01-15T10:30:00.000Z",
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                MMI=4,
                quality="best",
            ),
            geometry=QuakeGeometry(
                type="Point",
                coordinates=[174.7633, -36.8485, 5.5],
            ),
        )

        table = create_quakes_table([feature], "Test Title")
        assert table.title == "Test Title"
        # Basic check that table was created
        assert table.columns[0].header == "ID"

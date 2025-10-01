"""Comprehensive CLI tests for the new gnet CLI structure."""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from logerr import Err, Ok
from typer.testing import CliRunner

from gnet.cli.main import app
from gnet.models import cap, intensity, quake, volcano
from gnet.models.common import Point


class TestGnetCLIStructure:
    """Test the hierarchical CLI structure."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    def test_main_help(self, runner):
        """Test main help command shows hierarchical structure."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Comprehensive GeoNet API client" in result.stdout
        assert "quake" in result.stdout
        assert "volcano" in result.stdout
        # Aliases are hidden from help but still functional

    def test_version_command(self, runner):
        """Test version command works."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "gnet version" in result.stdout

    def test_no_command_shows_help(self, runner):
        """Test that running gnet alone shows help."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Usage: gnet" in result.stdout

    def test_quake_subcommand_help(self, runner):
        """Test quake subcommand help."""
        result = runner.invoke(app, ["quake", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "get" in result.stdout
        assert "health" in result.stdout
        assert "stats" in result.stdout
        assert "intensity" in result.stdout

    def test_volcano_subcommand_help(self, runner):
        """Test volcano subcommand help."""
        result = runner.invoke(app, ["volcano", "--help"])
        assert result.exit_code == 0
        assert "alerts" in result.stdout
        assert "quakes" in result.stdout

    def test_quake_alias(self, runner):
        """Test quake alias 'q' works."""
        result = runner.invoke(app, ["q", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout

    def test_volcano_alias(self, runner):
        """Test volcano alias 'v' works."""
        result = runner.invoke(app, ["v", "--help"])
        assert result.exit_code == 0
        assert "alerts" in result.stdout


class TestQuakeCommands:
    """Test earthquake commands with mocked responses."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @pytest.fixture
    def mock_quake_response(self):
        """Mock quake response data."""
        properties = quake.Properties.from_legacy_api(
            publicID="2025p123456",
            time=datetime(2025, 9, 28, 10, 30, 0),
            magnitude=4.2,
            depth=15.5,
            locality="Wellington",
            MMI=None,
            quality="best",
            longitude=174.7633,
            latitude=-41.2865,
        )

        feature = quake.Feature(
            properties=properties, geometry=Point(coordinates=[174.7633, -41.2865])
        )

        return quake.Response(features=[feature])

    @patch("gnet.cli.commands.list.GeoNetClient")
    def test_quake_list_command(self, mock_client_class, runner, mock_quake_response):
        """Test quake list command."""
        # Mock the async context manager and client methods
        mock_client = AsyncMock()
        # Since no --mmi parameter is provided, the command calls search_quakes, not get_quakes
        mock_client.search_quakes.return_value = Ok(mock_quake_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "list", "--limit", "1"])
        assert result.exit_code == 0
        assert "2025p123456" in result.stdout
        assert "Wellingt" in result.stdout  # Text is truncated in table display
        mock_client.search_quakes.assert_called_once()

    @patch("gnet.cli.commands.get.GeoNetClient")
    def test_quake_get_command(self, mock_client_class, runner, mock_quake_response):
        """Test quake get command."""
        mock_client = AsyncMock()
        mock_client.get_quake.return_value = Ok(mock_quake_response.features[0])
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "get", "2025p123456"])
        assert result.exit_code == 0
        assert "2025p123456" in result.stdout
        assert "Wellingt" in result.stdout  # Text is truncated in table display
        mock_client.get_quake.assert_called_once_with("2025p123456")

    @patch("gnet.cli.commands.health.GeoNetClient")
    def test_quake_health_command(self, mock_client_class, runner):
        """Test quake health command."""
        mock_client = AsyncMock()
        mock_client.health_check.return_value = Ok(True)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "health"])
        assert result.exit_code == 0
        assert "healthy" in result.stdout.lower()
        mock_client.health_check.assert_called_once()

    @patch("gnet.cli.commands.stats.GeoNetClient")
    def test_quake_stats_command(self, mock_client_class, runner):
        """Test quake stats command."""
        mock_stats = {
            "magnitudeCount": {"days7": {"3": 10, "4": 5}},
            "rate": {"perDay": {"2025-09-28": 25}},
        }
        mock_client = AsyncMock()
        mock_client.get_quake_stats.return_value = Ok(mock_stats)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "stats", "--format", "json"])
        assert result.exit_code == 0
        assert "magnitudeCount" in result.stdout
        mock_client.get_quake_stats.assert_called_once()

    @patch("gnet.cli.commands.history.GeoNetClient")
    def test_quake_history_command(self, mock_client_class, runner):
        """Test quake history command."""
        mock_history = [{"type": "Feature", "properties": {"publicID": "2025p123456"}}]
        mock_client = AsyncMock()
        mock_client.get_quake_history.return_value = Ok(mock_history)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "history", "2025p123456"])
        assert result.exit_code == 0
        assert "2025p123456" in result.stdout
        mock_client.get_quake_history.assert_called_once_with("2025p123456")


class TestIntensityCommands:
    """Test intensity commands with mocked responses."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @pytest.fixture
    def mock_intensity_response(self):
        """Mock intensity response data."""
        properties = intensity.Properties.from_legacy(
            mmi=4,
            count=5,
            longitude=174.7633,
            latitude=-41.2865,
        )

        feature = intensity.Feature(
            properties=properties, geometry=Point(coordinates=[174.7633, -41.2865])
        )

        return intensity.Response(features=[feature], count_mmi={"4": 5, "3": 10})

    @patch("gnet.cli.commands.intensity.GeoNetClient")
    def test_intensity_reported_command(
        self, mock_client_class, runner, mock_intensity_response
    ):
        """Test intensity reported command."""
        mock_client = AsyncMock()
        mock_client.get_intensity.return_value = Ok(mock_intensity_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "intensity-reported"])
        assert result.exit_code == 0
        assert "174.7633" in result.stdout
        assert "Reports" in result.stdout  # Column header for reported data
        mock_client.get_intensity.assert_called_once()

    @patch("gnet.cli.commands.intensity.GeoNetClient")
    def test_intensity_measured_command(
        self, mock_client_class, runner, mock_intensity_response
    ):
        """Test intensity measured command."""
        mock_client = AsyncMock()
        mock_client.get_intensity.return_value = Ok(mock_intensity_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "intensity-measured"])
        assert result.exit_code == 0
        assert "174.7633" in result.stdout
        mock_client.get_intensity.assert_called_once()

    @patch("gnet.cli.commands.intensity.GeoNetClient")
    def test_intensity_general_command(
        self, mock_client_class, runner, mock_intensity_response
    ):
        """Test general intensity command."""
        mock_client = AsyncMock()
        mock_client.get_intensity.return_value = Ok(mock_intensity_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "intensity", "reported"])
        assert result.exit_code == 0
        assert "174.7633" in result.stdout
        mock_client.get_intensity.assert_called_once_with(
            intensity_type="reported", publicid=None, aggregation=None
        )


class TestVolcanoCommands:
    """Test volcano commands with mocked responses."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @pytest.fixture
    def mock_volcano_response(self):
        """Mock volcano response data."""
        properties = volcano.Properties.from_legacy_api(
            volcanoID="ruapehu",
            volcanoTitle="Ruapehu",
            level=1,
            acc="Green",
            activity="Minor volcanic unrest.",
            hazards="Volcanic unrest hazards.",
            longitude=175.563,
            latitude=-39.281,
        )

        feature = volcano.Feature(
            properties=properties, geometry=Point(coordinates=[175.563, -39.281])
        )

        return volcano.Response(features=[feature])

    @patch("gnet.cli.commands.volcano_alerts.GeoNetClient")
    def test_volcano_alerts_command(
        self, mock_client_class, runner, mock_volcano_response
    ):
        """Test volcano alerts command."""
        mock_client = AsyncMock()
        mock_client.get_volcano_alerts.return_value = Ok(mock_volcano_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["volcano", "alerts"])
        assert result.exit_code == 0
        assert "Ruapehu" in result.stdout
        assert "GREEN" in result.stdout
        mock_client.get_volcano_alerts.assert_called_once()

    @patch("gnet.cli.commands.volcano_alerts.GeoNetClient")
    def test_volcano_alerts_filtering(
        self, mock_client_class, runner, mock_volcano_response
    ):
        """Test volcano alerts with filtering."""
        mock_client = AsyncMock()
        mock_client.get_volcano_alerts.return_value = Ok(mock_volcano_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["volcano", "alerts", "--volcano", "ruapehu"])
        assert result.exit_code == 0
        assert "Ruapehu" in result.stdout
        mock_client.get_volcano_alerts.assert_called_once_with(volcano_id="ruapehu")

    @patch("gnet.cli.commands.volcano_quakes.GeoNetClient")
    def test_volcano_quakes_empty_response(self, mock_client_class, runner):
        """Test volcano quakes command returns empty when no volcano specified."""
        mock_client = AsyncMock()
        mock_client.get_volcano_quakes.return_value = Ok(
            volcano.quake.Response(features=[])
        )
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["volcano", "quakes"])
        assert result.exit_code == 0
        # Should show empty table
        mock_client.get_volcano_quakes.assert_called_once()


class TestErrorHandling:
    """Test error handling in CLI commands."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @patch("gnet.cli.commands.list.GeoNetClient")
    def test_api_error_handling(self, mock_client_class, runner):
        """Test that API errors are handled gracefully."""
        mock_client = AsyncMock()
        # Since no --mmi parameter is provided, the command calls search_quakes, not get_quakes
        mock_client.search_quakes.return_value = Err("API connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "list"])
        # The CLI should handle errors gracefully
        assert result.exit_code != 0  # Should exit with error code
        # Check if error is in stdout or stderr
        error_output = result.stdout + (result.stderr or "")
        assert "Error" in error_output

    @patch("gnet.cli.commands.get.GeoNetClient")
    def test_earthquake_not_found_error(self, mock_client_class, runner):
        """Test earthquake not found error."""
        mock_client = AsyncMock()
        mock_client.get_quake.return_value = Err("Earthquake invalid_id not found")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "get", "invalid_id"])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "not found" in result.stdout


class TestOutputFormats:
    """Test different output formats."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @pytest.fixture
    def mock_quake_response(self):
        """Mock quake response data."""
        properties = quake.Properties.from_legacy_api(
            publicID="2025p123456",
            time=datetime(2025, 9, 28, 10, 30, 0),
            magnitude=4.2,
            depth=15.5,
            locality="Wellington",
            MMI=None,
            quality="best",
            longitude=174.7633,
            latitude=-41.2865,
        )

        feature = quake.Feature(
            properties=properties, geometry=Point(coordinates=[174.7633, -41.2865])
        )

        return quake.Response(features=[feature])

    @patch("gnet.cli.commands.list.GeoNetClient")
    def test_json_output_format(self, mock_client_class, runner, mock_quake_response):
        """Test JSON output format."""
        mock_client = AsyncMock()
        mock_client.search_quakes.return_value = Ok(mock_quake_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(
            app, ["quake", "list", "--format", "json", "--limit", "1"]
        )
        assert result.exit_code == 0

        # Should be valid JSON
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    @patch("gnet.cli.commands.list.GeoNetClient")
    def test_table_output_format(self, mock_client_class, runner, mock_quake_response):
        """Test table output format (default)."""
        mock_client = AsyncMock()
        mock_client.search_quakes.return_value = Ok(mock_quake_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "list", "--limit", "1"])
        assert result.exit_code == 0
        assert "ID" in result.stdout  # Table header
        assert "Magnitude" in result.stdout  # Table header
        assert "2025p123456" in result.stdout  # Data


class TestAliases:
    """Test command aliases work correctly."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @patch("gnet.cli.commands.list.GeoNetClient")
    def test_quake_alias_q(self, mock_client_class, runner):
        """Test that 'q' alias works the same as 'quake'."""
        mock_client = AsyncMock()
        mock_response = quake.Response(features=[])
        mock_client.search_quakes.return_value = Ok(mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["q", "list", "--limit", "1"])
        assert result.exit_code == 0
        mock_client.search_quakes.assert_called_once()

    @patch("gnet.cli.commands.volcano_alerts.GeoNetClient")
    def test_volcano_alias_v(self, mock_client_class, runner):
        """Test that 'v' alias works the same as 'volcano'."""
        mock_client = AsyncMock()
        mock_response = volcano.Response(features=[])
        mock_client.get_volcano_alerts.return_value = Ok(mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["v", "alerts"])
        assert result.exit_code == 0
        mock_client.get_volcano_alerts.assert_called_once()


class TestCAPCommands:
    """Test CAP (Common Alerting Protocol) commands."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    @pytest.fixture
    def mock_cap_feed_response(self):
        """Mock CAP feed response data."""
        entry = cap.CapEntry(
            id="geonet.org.nz/quake/2025p123456",
            title="M4.2 earthquake Wellington area",
            updated=datetime(2025, 9, 28, 10, 30, 0, tzinfo=UTC),
            published=datetime(2025, 9, 28, 10, 25, 0, tzinfo=UTC),
            summary="Moderate earthquake near Wellington",
            link="https://api.geonet.org.nz/cap/1.2/GPA1.0/quake/2025p123456",
            author="GNS Science (GeoNet)",
        )

        return cap.CapFeed(
            id="https://api.geonet.org.nz/cap/1.2/GPA1.0/feed/atom1.0/quake",
            title="CAP quakes",
            updated=datetime(2025, 9, 28, 10, 30, 0, tzinfo=UTC),
            author_name="GNS Science (GeoNet)",
            author_email="info@geonet.org.nz",
            author_uri="https://geonet.org.nz",
            entries=[entry],
        )

    @patch("gnet.cli.commands.cap.GeoNetClient")
    def test_cap_feed_command(self, mock_client_class, runner, mock_cap_feed_response):
        """Test CAP feed command."""
        mock_client = AsyncMock()
        mock_client.get_cap_feed.return_value = Ok(mock_cap_feed_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "cap-feed"])
        assert result.exit_code == 0
        assert "CAP Feed: CAP quakes" in result.stdout
        assert "GNS Science (GeoNet)" in result.stdout
        mock_client.get_cap_feed.assert_called_once()

    @patch("gnet.cli.commands.cap.GeoNetClient")
    def test_cap_feed_json_format(
        self, mock_client_class, runner, mock_cap_feed_response
    ):
        """Test CAP feed command with JSON output."""
        mock_client = AsyncMock()
        mock_client.get_cap_feed.return_value = Ok(mock_cap_feed_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "cap-feed", "--format", "json"])
        assert result.exit_code == 0

        # Should be valid JSON
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

        mock_client.get_cap_feed.assert_called_once()

    @patch("gnet.cli.commands.cap.GeoNetClient")
    def test_cap_alert_command(self, mock_client_class, runner):
        """Test CAP alert command."""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
            <identifier>2025p123456</identifier>
            <sender>info@geonet.org.nz</sender>
            <sent>2025-09-28T10:30:00Z</sent>
            <status>Actual</status>
            <msgType>Alert</msgType>
            <scope>Public</scope>
        </alert>"""

        mock_client = AsyncMock()
        mock_client.get_cap_alert.return_value = Ok(mock_xml)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "cap-alert", "2025p123456"])
        assert result.exit_code == 0
        assert "CAP Alert Document for 2025p123456" in result.stdout
        assert "<?xml version" in result.stdout
        mock_client.get_cap_alert.assert_called_once_with("2025p123456")

    @patch("gnet.cli.commands.cap.GeoNetClient")
    def test_cap_feed_error_handling(self, mock_client_class, runner):
        """Test CAP feed error handling."""
        mock_client = AsyncMock()
        mock_client.get_cap_feed.return_value = Err("CAP feed unavailable")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "cap-feed"])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "CAP feed unavailable" in result.stdout

    @patch("gnet.cli.commands.cap.GeoNetClient")
    def test_cap_alert_error_handling(self, mock_client_class, runner):
        """Test CAP alert error handling."""
        mock_client = AsyncMock()
        mock_client.get_cap_alert.return_value = Err("CAP alert not found")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = runner.invoke(app, ["quake", "cap-alert", "invalid_id"])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "CAP alert not found" in result.stdout

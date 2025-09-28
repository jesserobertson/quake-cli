"""
Integration tests for CLI commands against real GeoNet API.

These tests verify that the CLI commands work correctly with the live API.
"""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from quake_cli.cli import app


@pytest.mark.integration
class TestCLIIntegration:
    """Test CLI commands with real API calls."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_cli_health_command(self, runner):
        """Test health command with real API."""
        result = runner.invoke(app, ["health"])

        assert result.exit_code == 0
        # Should indicate API is healthy or unhealthy
        output = result.stdout.lower()
        assert "api" in output or "geonet" in output

    def test_cli_list_command_basic(self, runner):
        """Test basic list command."""
        result = runner.invoke(app, ["list", "--limit", "5"])

        assert result.exit_code == 0
        # Should show some earthquake data or "No earthquakes found"
        assert "earthquake" in result.stdout.lower() or "found" in result.stdout.lower()

    def test_cli_list_command_with_magnitude_filter(self, runner):
        """Test list command with magnitude filter."""
        result = runner.invoke(app, ["list", "--min-magnitude", "4.0", "--limit", "3"])

        assert result.exit_code == 0
        # If earthquakes are found, should show them
        # If none found, should show appropriate message
        assert (
            "earthquake" in result.stdout.lower()
            or "no earthquake" in result.stdout.lower()
            or "found" in result.stdout.lower()
        )

    def test_cli_list_command_json_format(self, runner):
        """Test list command with JSON output."""
        result = runner.invoke(app, ["list", "--format", "json", "--limit", "2"])

        assert result.exit_code == 0

        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            assert "type" in data
            assert data["type"] == "FeatureCollection"
            assert "features" in data
            assert isinstance(data["features"], list)
        except json.JSONDecodeError:
            pytest.fail("CLI did not output valid JSON")

    def test_cli_list_command_csv_format(self, runner):
        """Test list command with CSV output."""
        result = runner.invoke(app, ["list", "--format", "csv", "--limit", "3"])

        assert result.exit_code == 0

        # Should contain CSV headers
        assert "ID" in result.stdout
        assert "Time" in result.stdout
        assert "Magnitude" in result.stdout

    def test_cli_list_with_output_file(self, runner):
        """Test list command with file output."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = runner.invoke(
                app, ["list", "--format", "json", "--output", tmp_path, "--limit", "2"]
            )

            assert result.exit_code == 0
            assert f"JSON data written to {tmp_path}" in result.stdout

            # Verify file was created and contains valid JSON
            output_file = Path(tmp_path)
            assert output_file.exists()

            content = output_file.read_text()
            data = json.loads(content)
            assert isinstance(data, dict)
            assert data["type"] == "FeatureCollection"

        finally:
            # Clean up
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()

    def test_cli_get_command_with_real_earthquake(self, runner):
        """Test get command with a real earthquake ID."""
        # First get a list to find a real earthquake ID
        list_result = runner.invoke(app, ["list", "--format", "json", "--limit", "1"])

        if list_result.exit_code == 0:
            try:
                data = json.loads(list_result.stdout)
                if data["features"]:
                    earthquake_id = data["features"][0]["properties"]["publicID"]

                    # Now test getting this specific earthquake
                    result = runner.invoke(app, ["get", earthquake_id])

                    assert result.exit_code == 0
                    assert earthquake_id in result.stdout
                    assert (
                        "Earthquake Details" in result.stdout
                        or "earthquake" in result.stdout.lower()
                    )
            except (json.JSONDecodeError, KeyError, IndexError):
                # If we can't parse the list result, skip this test
                pytest.skip("Could not get valid earthquake ID from list command")
        else:
            pytest.skip("List command failed, cannot test get command")

    def test_cli_stats_command(self, runner):
        """Test stats command."""
        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        # Should show some statistics
        assert len(result.stdout.strip()) > 0

    def test_cli_history_command_with_real_earthquake(self, runner):
        """Test history command with a real earthquake ID."""
        # First get a list to find a real earthquake ID
        list_result = runner.invoke(app, ["list", "--format", "json", "--limit", "1"])

        if list_result.exit_code == 0:
            try:
                data = json.loads(list_result.stdout)
                if data["features"]:
                    earthquake_id = data["features"][0]["properties"]["publicID"]

                    # Test getting history for this earthquake
                    result = runner.invoke(app, ["history", earthquake_id])

                    # History command might succeed or fail depending on whether
                    # the earthquake has history data
                    assert result.exit_code in [0, 1]  # Both are acceptable

            except (json.JSONDecodeError, KeyError, IndexError):
                pytest.skip("Could not get valid earthquake ID from list command")
        else:
            pytest.skip("List command failed, cannot test history command")

    def test_cli_error_handling_invalid_id(self, runner):
        """Test CLI error handling with invalid earthquake ID."""
        result = runner.invoke(app, ["get", "invalid_earthquake_id_12345"])

        # Should fail gracefully
        assert result.exit_code != 0
        # Should show some error message
        assert len(result.stdout.strip()) > 0 or len(result.stderr.strip()) > 0

    def test_cli_mmi_filter(self, runner):
        """Test CLI with MMI filter."""
        result = runner.invoke(app, ["list", "--mmi", "3", "--limit", "5"])

        assert result.exit_code == 0
        # Should handle MMI filter (might return empty results)
        assert "earthquake" in result.stdout.lower() or "found" in result.stdout.lower()

    def test_cli_help_commands(self, runner):
        """Test that all help commands work."""
        # Main help
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "GeoNet Earthquake CLI" in result.stdout

        # Command-specific help
        commands = ["list", "get", "history", "stats", "health"]
        for cmd in commands:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0, f"Help for {cmd} command failed"
            assert cmd in result.stdout.lower()


@pytest.mark.integration
class TestCLIRobustness:
    """Test CLI robustness and edge cases."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_cli_with_various_limits(self, runner):
        """Test CLI with different limit values."""
        # Small limit
        result = runner.invoke(app, ["list", "--limit", "1"])
        assert result.exit_code == 0

        # Larger limit
        result = runner.invoke(app, ["list", "--limit", "20"])
        assert result.exit_code == 0

        # Zero limit (should be handled gracefully)
        result = runner.invoke(app, ["list", "--limit", "0"])
        # This might succeed with empty results or fail gracefully
        assert result.exit_code in [0, 1]

    def test_cli_magnitude_boundary_values(self, runner):
        """Test CLI with edge case magnitude values."""
        # Very high magnitude (unlikely to find results)
        result = runner.invoke(app, ["list", "--min-magnitude", "9.0", "--limit", "5"])
        assert result.exit_code == 0

        # Magnitude range
        result = runner.invoke(
            app,
            [
                "list",
                "--min-magnitude",
                "2.0",
                "--max-magnitude",
                "5.0",
                "--limit",
                "5",
            ],
        )
        assert result.exit_code == 0

    def test_cli_output_formats_consistency(self, runner):
        """Test that all output formats work for the same data."""
        formats = ["table", "json", "csv"]

        for fmt in formats:
            result = runner.invoke(app, ["list", "--format", fmt, "--limit", "2"])
            assert result.exit_code == 0, f"Format {fmt} failed"
            assert len(result.stdout.strip()) > 0, f"Format {fmt} produced no output"

    def test_cli_concurrent_usage_simulation(self, runner):
        """Test CLI commands in sequence to simulate concurrent usage."""
        # Simulate multiple quick CLI calls
        commands = [
            ["health"],
            ["list", "--limit", "2"],
            ["stats"],
            ["list", "--format", "json", "--limit", "1"],
        ]

        for cmd in commands:
            result = runner.invoke(app, cmd)
            # All commands should succeed or fail gracefully
            assert result.exit_code in [0, 1], f"Command {cmd} had unexpected exit code"

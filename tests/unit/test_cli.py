"""Simplified CLI tests focusing on core functionality."""

import pytest
from typer.testing import CliRunner

from gnet.cli.main import app
from gnet.cli.output import create_quakes_table, format_datetime, output_data
from gnet.models import quake


class TestCLIBasics:
    """Test basic CLI functionality without complex mocking."""

    @pytest.fixture
    def runner(self):
        """Test runner fixture."""
        return CliRunner()

    def test_help_command(self, runner):
        """Test help command works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "GeoNet Earthquake CLI" in result.stdout

    def test_command_structure(self, runner):
        """Test that all expected commands are available."""
        result = runner.invoke(app, ["--help"])
        assert "list" in result.stdout
        assert "get" in result.stdout
        assert "health" in result.stdout
        assert "history" in result.stdout
        assert "stats" in result.stdout


class TestCLIHelpers:
    """Test CLI helper functions."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        from datetime import datetime

        dt = datetime(2024, 1, 15, 10, 30, 0)
        formatted = format_datetime(dt)
        assert formatted == "2024-01-15 10:30:00"

    def test_create_quakes_table(self):
        """Test table creation."""
        feature = quake.Feature(
            type="Feature",
            properties=quake.Properties(
                publicID="2024p123456",
                time="2024-01-15T10:30:00.000Z",
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                mmi=4,
                quality="best",
            ),
            geometry=quake.Geometry(
                type="Point",
                coordinates=[174.7633, -36.8485, 5.5],
            ),
        )

        table = create_quakes_table([feature], "Test Title")
        assert table.title == "Test Title"
        assert table.columns[0].header == "ID"

    def test_output_data_function_exists(self):
        """Test that output_data function exists and is callable."""
        assert callable(output_data)

    def test_output_data_unknown_format(self):
        """Test output with unknown format."""
        import io
        from contextlib import redirect_stdout

        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            output_data({"test": "data"}, "unknown")

        # Should handle unknown format gracefully
        # (The function prints error message via console.print)

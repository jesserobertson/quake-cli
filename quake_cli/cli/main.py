"""
Main CLI application entry point.

This module sets up the Typer app and registers all commands.
"""

import typer

from quake_cli.cli.base import configure_logging
from quake_cli.cli.commands.get import get_quake
from quake_cli.cli.commands.health import health_check
from quake_cli.cli.commands.history import get_history
from quake_cli.cli.commands.list import list_quakes
from quake_cli.cli.commands.stats import get_stats

# Initialize Typer app
app = typer.Typer(
    name="quake",
    help="GeoNet Earthquake CLI - Query earthquake data from GeoNet API",
    add_completion=False,
)

# Register commands
app.command("list")(list_quakes)
app.command("get")(get_quake)
app.command("history")(get_history)
app.command("stats")(get_stats)
app.command("health")(health_check)


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    """
    GeoNet Earthquake CLI - Query earthquake data from GeoNet API.

    Use 'quake --help' to see available commands.
    """
    if version:
        from quake_cli import __version__

        print(f"quake-cli version {__version__}")
        raise typer.Exit(0)

    # Configure logging based on verbose flag
    configure_logging(verbose)


if __name__ == "__main__":
    app()

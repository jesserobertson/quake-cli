"""
Main CLI application entry point for GeoNet comprehensive monitoring.

This module sets up the main Typer app with subcommands for earthquakes and volcanoes.
"""

import typer

from gnet.cli.base import configure_logging
from gnet.cli.quake import quake_app
from gnet.cli.volcano import volcano_app

# Initialize main Typer app
app = typer.Typer(
    name="gnet",
    help="Comprehensive GeoNet API client for earthquakes, volcanoes, and geohazard monitoring",
    add_completion=False,
)

# Add subcommands
app.add_typer(quake_app, name="quake", help="Earthquake monitoring and data")
app.add_typer(quake_app, name="q", help="Earthquake monitoring and data", hidden=True)
app.add_typer(volcano_app, name="volcano", help="Volcano monitoring and alerts")
app.add_typer(volcano_app, name="v", help="Volcano monitoring and alerts", hidden=True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    """
    Comprehensive GeoNet API client for earthquakes, volcanoes, and geohazard monitoring.

    Commands:
    - gnet quake (or gnet q) - Earthquake data and monitoring
    - gnet volcano (or gnet v) - Volcano alerts and monitoring

    Use 'gnet COMMAND --help' to see available subcommands.
    """
    if version:
        from gnet import __version__

        print(f"gnet version {__version__}")
        raise typer.Exit(0)

    # Configure logging based on verbose flag
    configure_logging(verbose)

    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None and not version:
        print(ctx.get_help())
        ctx.exit()


if __name__ == "__main__":
    app()

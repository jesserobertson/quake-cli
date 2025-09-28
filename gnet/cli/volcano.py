"""
Volcano monitoring CLI commands.

This module contains all volcano-related commands for the GeoNet CLI.
"""

import typer

from gnet.cli.commands.volcano_alerts import get_volcano_alerts
from gnet.cli.commands.volcano_quakes import get_volcano_quakes

# Initialize volcano Typer app
volcano_app = typer.Typer(
    name="volcano",
    help="Volcano monitoring and alert commands",
    add_completion=False,
)

# Register volcano commands
volcano_app.command("alerts", help="Get current volcanic alert levels")(get_volcano_alerts)
volcano_app.command("quakes", help="Get earthquakes near volcanoes")(get_volcano_quakes)

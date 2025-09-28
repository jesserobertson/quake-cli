"""
Earthquake monitoring CLI commands.

This module contains all earthquake-related commands for the GeoNet CLI.
"""

import typer

from gnet.cli.commands.cap import cap_alert, cap_feed
from gnet.cli.commands.get import get_quake
from gnet.cli.commands.health import health_check
from gnet.cli.commands.history import get_history
from gnet.cli.commands.intensity import (
    get_intensity,
    get_intensity_measured,
    get_intensity_reported,
)
from gnet.cli.commands.list import list_quakes
from gnet.cli.commands.stats import get_stats
from gnet.cli.commands.strong_motion import get_strong_motion

# Initialize earthquake Typer app
quake_app = typer.Typer(
    name="quake",
    help="Earthquake monitoring and data analysis commands",
    add_completion=False,
)

# Register core earthquake commands
quake_app.command("list", help="List recent earthquakes with optional filtering")(
    list_quakes
)
quake_app.command("get", help="Get details for a specific earthquake")(get_quake)
quake_app.command("history", help="Get location history for a specific earthquake")(
    get_history
)
quake_app.command("stats", help="Get earthquake statistics")(get_stats)
quake_app.command("health", help="Check GeoNet API health status")(health_check)

# Register intensity commands
quake_app.command("intensity", help="Get shaking intensity data for earthquakes")(
    get_intensity
)
quake_app.command("intensity-reported", help="Get reported shaking intensity data")(
    get_intensity_reported
)
quake_app.command("intensity-measured", help="Get measured shaking intensity data")(
    get_intensity_measured
)

# Register CAP (Common Alerting Protocol) commands
quake_app.command("cap-feed", help="Get CAP feed of recent significant earthquakes")(
    cap_feed
)
quake_app.command("cap-alert", help="Get individual CAP alert document")(cap_alert)

# Register strong motion commands
quake_app.command(
    "strong-motion", help="Get strong motion/accelerometer data for an earthquake"
)(get_strong_motion)

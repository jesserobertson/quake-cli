"""
Volcano alert commands for monitoring volcanic activity.

This module contains commands to retrieve and display volcanic alert levels
for New Zealand volcanoes.
"""

import asyncio
from typing import Annotated

import typer
from rich.console import Console

from gnet.cli.base import handle_result
from gnet.cli.output import format_volcano_alerts_output
from gnet.client import GeoNetClient

console = Console()


def get_volcano_alerts(
    volcano_id: Annotated[
        str | None, typer.Option("--volcano", "-v", help="Specific volcano ID")
    ] = None,
    format_type: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
) -> None:
    """
    Get current volcanic alert levels for New Zealand volcanoes.

    Shows the current alert status for all monitored volcanoes, including
    alert levels, color codes, and activity descriptions.

    Alert Levels:
    - Level 0 (Green): No volcanic unrest
    - Level 1 (Yellow): Minor volcanic unrest
    - Level 2 (Yellow): Moderate to heightened volcanic unrest
    - Level 3 (Orange): Minor eruption activity
    - Level 4 (Orange): Moderate eruption activity
    - Level 5 (Red): Major eruption activity

    Examples:
        gnet volcano alerts
        gnet v alerts --format json
        gnet volcano alerts --volcano WHITE_ISLAND
    """
    asyncio.run(async_get_volcano_alerts(volcano_id, format_type))


async def async_get_volcano_alerts(
    volcano_id: str | None,
    format_type: str,
) -> None:
    """Async implementation for volcano alerts command."""
    async with GeoNetClient() as client:
        result = await client.get_volcano_alerts(volcano_id=volcano_id)

        data = handle_result(result)
        format_volcano_alerts_output(data, format_type)

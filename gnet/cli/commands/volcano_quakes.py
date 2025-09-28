"""
Volcano earthquake commands for monitoring seismic activity near volcanoes.

This module contains commands to retrieve and display earthquakes
that occur near volcanic regions.
"""

import asyncio
from typing import Annotated

import typer
from rich.console import Console

from gnet.cli.base import handle_result
from gnet.cli.output import format_volcano_quakes_output
from gnet.client import GeoNetClient

console = Console()


def get_volcano_quakes(
    volcano_id: Annotated[
        str | None, typer.Option("--volcano", "-v", help="Specific volcano ID")
    ] = None,
    limit: Annotated[
        int | None, typer.Option("--limit", "-l", help="Maximum number of results")
    ] = 10,
    min_magnitude: Annotated[
        float | None, typer.Option("--min-magnitude", "-m", help="Minimum magnitude")
    ] = None,
    format_type: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
) -> None:
    """
    Get earthquakes near volcanoes.

    Shows seismic activity in volcanic regions, which can be an indicator
    of volcanic unrest or eruption activity.

    Examples:
        gnet volcano quakes
        gnet v quakes --volcano WHITE_ISLAND
        gnet volcano quakes --min-magnitude 2.0 --limit 20
        gnet v quakes --format json
    """
    asyncio.run(
        async_get_volcano_quakes(volcano_id, limit, min_magnitude, format_type)
    )


async def async_get_volcano_quakes(
    volcano_id: str | None,
    limit: int | None,
    min_magnitude: float | None,
    format_type: str,
) -> None:
    """Async implementation for volcano quakes command."""
    async with GeoNetClient() as client:
        result = await client.get_volcano_quakes(
            volcano_id=volcano_id,
            limit=limit,
            min_magnitude=min_magnitude,
        )

        data = handle_result(result)
        format_volcano_quakes_output(data, format_type)
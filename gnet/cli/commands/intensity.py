"""
Intensity commands for earthquake shaking data.

This module contains commands to retrieve and display earthquake intensity data,
both from user reports and instrumental measurements.
"""

import asyncio
from typing import Annotated

import typer
from rich.console import Console

from gnet.cli.base import handle_result
from gnet.cli.output import format_intensity_output
from gnet.client import GeoNetClient

console = Console()


def get_intensity(
    intensity_type: Annotated[
        str, typer.Argument(help="Type of intensity data: 'reported' or 'measured'")
    ] = "reported",
    publicid: Annotated[
        str | None, typer.Option("--publicid", "-p", help="Earthquake public ID")
    ] = None,
    aggregation: Annotated[
        str | None,
        typer.Option(
            "--aggregation",
            "-a",
            help="Aggregation method for reported data: 'max' or 'median'",
        ),
    ] = None,
    format_type: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
) -> None:
    """
    Get shaking intensity data for earthquakes.

    Retrieves intensity data from either user reports or instrumental measurements.

    Examples:
        gnet quake intensity reported
        gnet quake intensity measured --publicid 2025p730586
        gnet quake intensity reported --aggregation median --format json
    """
    asyncio.run(
        async_get_intensity(intensity_type, publicid, aggregation, format_type)
    )


def get_intensity_reported(
    publicid: Annotated[
        str | None, typer.Option("--publicid", "-p", help="Earthquake public ID")
    ] = None,
    aggregation: Annotated[
        str | None,
        typer.Option(
            "--aggregation",
            "-a",
            help="Aggregation method: 'max' or 'median'",
        ),
    ] = None,
    format_type: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
) -> None:
    """
    Get reported shaking intensity data from user experiences.

    Shows where earthquakes were felt based on user reports.
    If no publicID specified, shows reports from the last 60 minutes.

    Examples:
        gnet quake intensity-reported
        gnet quake intensity-reported --publicid 2025p730586
        gnet quake intensity-reported --aggregation median
    """
    asyncio.run(async_get_intensity("reported", publicid, aggregation, format_type))


def get_intensity_measured(
    publicid: Annotated[
        str | None, typer.Option("--publicid", "-p", help="Earthquake public ID")
    ] = None,
    format_type: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
) -> None:
    """
    Get measured shaking intensity data from instruments.

    Shows instrumental measurements of ground shaking intensity.

    Examples:
        gnet quake intensity-measured
        gnet quake intensity-measured --publicid 2025p730586 --format json
    """
    asyncio.run(async_get_intensity("measured", publicid, None, format_type))


async def async_get_intensity(
    intensity_type: str,
    publicid: str | None,
    aggregation: str | None,
    format_type: str,
) -> None:
    """Async implementation for intensity commands."""
    # Validate intensity type
    if intensity_type not in ["reported", "measured"]:
        console.print(
            "[red]Error:[/red] intensity_type must be 'reported' or 'measured'"
        )
        raise typer.Exit(1)

    # Validate aggregation (only for reported)
    if aggregation and intensity_type != "reported":
        console.print(
            "[red]Error:[/red] aggregation is only available for reported intensity"
        )
        raise typer.Exit(1)

    if aggregation and aggregation not in ["max", "median"]:
        console.print(
            "[red]Error:[/red] aggregation must be 'max' or 'median'"
        )
        raise typer.Exit(1)

    async with GeoNetClient() as client:
        result = await client.get_intensity(
            intensity_type=intensity_type,
            publicid=publicid,
            aggregation=aggregation,
        )

        data = handle_result(result)
        format_intensity_output(data, format_type, intensity_type)
"""
Get command implementation.

This module provides the 'get' command for fetching specific earthquake details.
"""

from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gnet.cli.base import (
    async_command,
    configure_logging,
    console,
    get_progress_console,
    handle_errors,
    handle_result,
)
from gnet.cli.output import OutputFormat, output_data
from gnet.client import GeoNetClient


@async_command
@handle_errors
async def get_quake(
    earthquake_id: str = typer.Argument(..., help="Earthquake public ID"),
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Get details for a specific earthquake."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task(f"Fetching earthquake {earthquake_id}...", total=None)

        async with GeoNetClient() as client:
            result = await client.get_quake(earthquake_id)
            feature = handle_result(result)

        progress.update(task, completed=True, description="Earthquake retrieved")

    output_data(feature, format, output)

    if format.lower() == "table":
        # Show additional details for single earthquake
        _ = feature.properties  # Access properties for potential future use
        geom = feature.geometry

        details_table = Table(
            title="Location Details", show_header=True, header_style="bold blue"
        )
        details_table.add_column("Property", style="cyan")
        details_table.add_column("Value", style="white")

        details_table.add_row("Longitude", f"{geom.longitude:.4f}°")
        details_table.add_row("Latitude", f"{geom.latitude:.4f}°")
        if feature.properties.location.elevation is not None:
            depth = abs(feature.properties.location.elevation)
            details_table.add_row("Depth", f"{depth:.1f} km")

        console.print(details_table)

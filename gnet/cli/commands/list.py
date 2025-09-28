"""
List command implementation.

This module provides the 'list' command for listing recent earthquakes.
"""

from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

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
async def list_quakes(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of earthquakes to return"
    ),
    min_magnitude: float = typer.Option(
        None, "--min-magnitude", help="Minimum magnitude filter"
    ),
    max_magnitude: float = typer.Option(
        None, "--max-magnitude", help="Maximum magnitude filter"
    ),
    min_mmi: int = typer.Option(
        None, "--min-mmi", help="Minimum Modified Mercalli Intensity"
    ),
    max_mmi: int = typer.Option(
        None, "--max-mmi", help="Maximum Modified Mercalli Intensity"
    ),
    mmi: int = typer.Option(
        None,
        "--mmi",
        help="Specific Modified Mercalli Intensity (-1 to 8, server-side filter)",
    ),
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """List recent earthquakes with optional filtering."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task("Fetching earthquakes...", total=None)

        async with GeoNetClient() as client:
            if mmi is not None:
                # Use server-side MMI filtering
                result = await client.get_quakes(mmi=mmi, limit=limit)
                response = handle_result(result)
            else:
                # Use client-side filtering
                result = await client.search_quakes(  # type: ignore[unreachable]
                    min_magnitude=min_magnitude,
                    max_magnitude=max_magnitude,
                    min_mmi=min_mmi,
                    max_mmi=max_mmi,
                    limit=limit,
                )
                response = handle_result(result)

        progress.update(
            task, completed=True, description=f"Found {response.count} earthquakes"
        )

    if response.is_empty:
        console.print("[yellow]No earthquakes found matching the criteria[/yellow]")
        return

    output_data(response, format, output)

    if format.lower() == "table":
        console.print(
            f"\n[dim]Showing {len(response.features)} of {response.count} earthquakes[/dim]"
        )

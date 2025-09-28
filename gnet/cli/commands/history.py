"""
History command implementation.

This module provides the 'history' command for fetching earthquake location history.
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
async def get_history(
    earthquake_id: str = typer.Argument(..., help="Earthquake public ID"),
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Get location history for a specific earthquake."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task(f"Fetching history for {earthquake_id}...", total=None)

        async with GeoNetClient() as client:
            result = await client.get_quake_history(earthquake_id)
            history_data = handle_result(result)

        progress.update(task, completed=True, description="History retrieved")

    output_data(history_data, format, output)

    if format.lower() == "table":
        console.print(
            "[dim]History data returned as raw format. Use --format json for detailed view.[/dim]"
        )

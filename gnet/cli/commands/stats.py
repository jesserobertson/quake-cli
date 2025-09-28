"""
Stats command implementation.

This module provides the 'stats' command for fetching earthquake statistics.
"""

from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from gnet.cli.base import (
    async_command,
    configure_logging,
    get_progress_console,
    handle_errors,
    handle_result,
)
from gnet.cli.output import OutputFormat, output_data
from gnet.client import GeoNetClient


@async_command
@handle_errors
async def get_stats(
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Get earthquake statistics."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task("Fetching earthquake statistics...", total=None)

        async with GeoNetClient() as client:
            result = await client.get_quake_stats()
            stats_data = handle_result(result)

        progress.update(task, completed=True, description="Statistics retrieved")

    output_data(stats_data, format, output)

"""
Health command implementation.

This module provides the 'health' command for checking API status.
"""

import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from quake_cli.cli.base import (
    async_command,
    configure_logging,
    console,
    handle_errors,
    handle_result,
)
from quake_cli.client import GeoNetClient


@async_command
@handle_errors
async def health_check(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Check GeoNet API health status."""

    # Configure logging for this command
    configure_logging(verbose)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking API health...", total=None)

        async with GeoNetClient() as client:
            result = await client.health_check()
            is_healthy = handle_result(result)

        progress.update(task, completed=True)

    if is_healthy:
        console.print(Panel("✅ GeoNet API is healthy", style="green"))
    else:
        console.print(Panel("❌ GeoNet API is not responding", style="red"))
        raise typer.Exit(1)

"""
CAP (Common Alerting Protocol) command implementations.

This module provides commands for fetching CAP alerts from the GeoNet API.
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
async def cap_feed(
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Get CAP feed of recent significant earthquakes."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task("Fetching CAP feed...", total=None)

        async with GeoNetClient() as client:
            result = await client.get_cap_feed()
            feed = handle_result(result)

        progress.update(task, completed=True, description="CAP feed retrieved")

    output_data(feed, format, output)

    if format.lower() == "table":
        # Show feed summary
        table = Table(
            title=f"CAP Feed: {feed.title}", show_header=True, header_style="bold blue"
        )
        table.add_column("Entry ID", style="cyan", width=20)
        table.add_column("Title", style="white")
        table.add_column("Published", style="green", width=20)
        table.add_column("Updated", style="yellow", width=20)

        for entry in feed.entries:
            published_str = entry.published.strftime("%Y-%m-%d %H:%M")
            updated_str = entry.updated.strftime("%Y-%m-%d %H:%M")

            # Truncate title if too long
            title = entry.title
            if len(title) > 50:
                title = title[:47] + "..."

            table.add_row(
                entry.id,
                title,
                published_str,
                updated_str,
            )

        console.print(table)

        # Show feed metadata
        if feed.author_name or feed.author_email:
            metadata_table = Table(
                title="Feed Metadata", show_header=True, header_style="bold blue"
            )
            metadata_table.add_column("Property", style="cyan")
            metadata_table.add_column("Value", style="white")

            if feed.author_name:
                metadata_table.add_row("Author", feed.author_name)
            if feed.author_email:
                metadata_table.add_row("Email", feed.author_email)
            if feed.author_uri:
                metadata_table.add_row("Website", feed.author_uri)

            metadata_table.add_row("Last Updated", feed.updated.strftime("%Y-%m-%d %H:%M:%S UTC"))
            metadata_table.add_row("Total Entries", str(feed.count))

            console.print(metadata_table)


@async_command
@handle_errors
async def cap_alert(
    cap_id: str = typer.Argument(..., help="CAP alert identifier"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Get individual CAP alert document."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task(f"Fetching CAP alert {cap_id}...", total=None)

        async with GeoNetClient() as client:
            result = await client.get_cap_alert(cap_id)
            xml_content = handle_result(result)

        progress.update(task, completed=True, description="CAP alert retrieved")

    if output:
        # Write XML to file
        output.write_text(xml_content, encoding="utf-8")
        console.print(f"[green]CAP alert saved to {output}[/green]")
    else:
        # Display XML content
        console.print(f"[bold blue]CAP Alert Document for {cap_id}[/bold blue]")
        console.print(xml_content)

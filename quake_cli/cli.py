"""
Typer CLI for GeoNet earthquake data.

This module provides the command-line interface for querying earthquake data
from the GeoNet API using async operations and rich console output.
"""

import asyncio
import csv
import json
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from logerr import Result

from quake_cli.client import GeoNetClient, GeoNetError
import quake_cli.models
from quake_cli.models import QuakeFeature, QuakeResponse

# Initialize Typer app and Rich console
app = typer.Typer(
    name="quake",
    help="GeoNet Earthquake CLI - Query earthquake data from GeoNet API",
    add_completion=False,
)
console = Console()

# Global verbose flag
_verbose_logging = False


def configure_logging(verbose: bool) -> None:
    """Configure logging levels based on verbose flag."""
    global _verbose_logging
    _verbose_logging = verbose

    if verbose:
        # Enable detailed logging with timestamps and levels
        logger.remove()  # Remove default handler
        logger.add(
            console.file,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG"
        )
        console.print("[dim]Verbose logging enabled[/dim]")
    else:
        # Remove all handlers to suppress logerr automatic logging
        logger.remove()
        # Add a minimal handler that only shows critical errors to stderr
        import sys
        logger.add(
            sys.stderr,
            format="<red>{message}</red>",
            level="CRITICAL",
            filter=lambda record: record["level"].name == "CRITICAL"
        )

# Output format options
OutputFormat = typer.Option(
    "table",
    "--format",
    "-f",
    help="Output format",
    case_sensitive=False,
    show_choices=True,
)


def handle_result(result: Result) -> Any:
    """Handle Result types and convert errors to CLI exits."""
    if result.is_ok():
        return result.unwrap()
    else:
        error_msg = result.unwrap_err()
        if _verbose_logging:
            # In verbose mode, the error is already logged by logerr
            console.print(f"[red]Error:[/red] {error_msg}")
        else:
            # In non-verbose mode, show a clean error message
            console.print(f"[red]Error:[/red] {error_msg}")
        raise typer.Exit(1)


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle common CLI errors."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except typer.Exit:
            # Re-raise typer.Exit to allow proper CLI exit
            raise
        except GeoNetError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            raise typer.Exit(130)
        except Exception as e:
            console.print(f"[red]Unexpected error:[/red] {e}")
            raise typer.Exit(1)

    return wrapper


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def create_quakes_table(
    features: list[QuakeFeature], title: str = "Earthquakes"
) -> Table:
    """Create a rich table for earthquake data."""
    table = Table(title=title, show_header=True, header_style="bold magenta")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Time", style="green")
    table.add_column("Magnitude", justify="right", style="yellow")
    table.add_column("Depth (km)", justify="right", style="blue")
    table.add_column("MMI", justify="right", style="red")
    table.add_column("Quality", style="dim")
    table.add_column("Location", style="white")

    for feature in features:
        props = feature.properties
        table.add_row(
            props.publicID,
            format_datetime(props.time),
            f"{props.magnitude:.1f}",
            f"{props.depth:.1f}",
            str(props.MMI) if props.MMI is not None else "-",
            props.quality,
            props.locality,
        )

    return table


def output_data(data: Any, format_type: str, output_file: Path | None = None) -> None:
    """Output data in the specified format."""
    match format_type.lower():
        case "json":
            # Handle JSON output
            if hasattr(data, "model_dump"):
                json_data = data.model_dump()
            elif isinstance(data, list):
                json_data: Any = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in data
                ]
            else:
                json_data = data

            json_str = json.dumps(json_data, indent=2, default=str)

            if output_file:
                output_file.write_text(json_str)
                print(f"JSON data written to {str(output_file)}")
            else:
                console.print(json_str)

        case "csv":
            # Handle CSV output
            if hasattr(data, "features"):
                features = data.features
            elif hasattr(data, "properties"):
                features = [data]
            elif isinstance(data, list) and data:
                features = data
            else:
                console.print("[red]CSV format only supported for earthquake data[/red]")
                return

            if output_file:
                with open(output_file, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        [
                            "ID",
                            "Time",
                            "Magnitude",
                            "Depth",
                            "MMI",
                            "Quality",
                            "Location",
                            "Longitude",
                            "Latitude",
                        ]
                    )
                    for feature in features:
                        props = feature.properties
                        geom = feature.geometry
                        writer.writerow(
                            [
                                props.publicID,
                                props.time.isoformat(),
                                props.magnitude,
                                props.depth,
                                props.MMI,
                                props.quality,
                                props.locality,
                                geom.longitude,
                                geom.latitude,
                            ]
                        )
                print(f"CSV data written to {str(output_file)}")
            else:
                # Output CSV to console
                import io

                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(
                    [
                        "ID",
                        "Time",
                        "Magnitude",
                        "Depth",
                        "MMI",
                        "Quality",
                        "Location",
                        "Longitude",
                        "Latitude",
                    ]
                )
                for feature in features:
                    props = feature.properties
                    geom = feature.geometry
                    writer.writerow(
                        [
                            props.publicID,
                            props.time.isoformat(),
                            props.magnitude,
                            props.depth,
                            props.MMI,
                            props.quality,
                            props.locality,
                            geom.longitude,
                            geom.latitude,
                        ]
                    )
                console.print(output.getvalue())

        case "table":
            # Handle table output using match statements
            match data:
                case data if isinstance(data, QuakeResponse):
                    table = create_quakes_table(data.features)
                    console.print(table)
                case data if isinstance(data, QuakeFeature):
                    table = create_quakes_table([data], "Earthquake Details")
                    console.print(table)
                case data if isinstance(data, (list, tuple)) and data:
                    table = create_quakes_table(data)
                    console.print(table)
                case _:
                    # For other data types, show as JSON-like format
                    console.print(data)

        case _:
            console.print(f"[red]Unknown format: {format_type}[/red]")


@app.command()
@handle_errors
def list(
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
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """List recent earthquakes with optional filtering."""

    # Configure logging for this command
    configure_logging(verbose)

    async def async_list() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching earthquakes...", total=None)

            async with GeoNetClient() as client:
                if mmi is not None:
                    # Use server-side MMI filtering
                    result = await client.get_quakes(mmi=mmi, limit=limit)
                    response = handle_result(result)
                else:
                    # Use client-side filtering
                    result = await client.search_quakes(
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

    asyncio.run(async_list())


@app.command()
@handle_errors
def get(
    earthquake_id: str = typer.Argument(..., help="Earthquake public ID"),
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Get details for a specific earthquake."""

    # Configure logging for this command
    configure_logging(verbose)

    async def async_get() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Fetching earthquake {earthquake_id}...", total=None
            )

            async with GeoNetClient() as client:
                result = await client.get_quake(earthquake_id)
                feature = handle_result(result)

            progress.update(task, completed=True, description="Earthquake retrieved")

        output_data(feature, format, output)

        if format.lower() == "table":
            # Show additional details for single earthquake
            props = feature.properties
            geom = feature.geometry

            details_table = Table(
                title="Location Details", show_header=True, header_style="bold blue"
            )
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="white")

            details_table.add_row("Longitude", f"{geom.longitude:.4f}°")
            details_table.add_row("Latitude", f"{geom.latitude:.4f}°")
            if geom.depth is not None:
                details_table.add_row("Depth (geometry)", f"{geom.depth:.1f} km")

            console.print(details_table)

    asyncio.run(async_get())


@app.command()
@handle_errors
def history(
    earthquake_id: str = typer.Argument(..., help="Earthquake public ID"),
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Get location history for a specific earthquake."""

    # Configure logging for this command
    configure_logging(verbose)

    async def async_history() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Fetching history for {earthquake_id}...", total=None
            )

            async with GeoNetClient() as client:
                result = await client.get_quake_history(earthquake_id)
                history_data = handle_result(result)

            progress.update(task, completed=True, description="History retrieved")

        output_data(history_data, format, output)

        if format.lower() == "table":
            console.print(
                "[dim]History data returned as raw format. Use --format json for detailed view.[/dim]"
            )

    asyncio.run(async_history())


@app.command()
@handle_errors
def stats(
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Get earthquake statistics."""

    # Configure logging for this command
    configure_logging(verbose)

    async def async_stats() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching earthquake statistics...", total=None)

            async with GeoNetClient() as client:
                result = await client.get_quake_stats()
                stats_data = handle_result(result)

            progress.update(task, completed=True, description="Statistics retrieved")

        output_data(stats_data, format, output)

    asyncio.run(async_stats())


@app.command()
@handle_errors
def health(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Check GeoNet API health status."""

    # Configure logging for this command
    configure_logging(verbose)

    async def async_health() -> None:
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

    asyncio.run(async_health())


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    """
    GeoNet Earthquake CLI - Query earthquake data from GeoNet API.

    Use 'quake --help' to see available commands.
    """
    if version:
        from quake_cli import __version__

        print(f"quake-cli version {__version__}")
        raise typer.Exit(0)

    # Configure logging based on verbose flag
    configure_logging(verbose)


if __name__ == "__main__":
    app()

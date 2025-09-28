"""
Output formatting utilities for CLI commands.

This module handles different output formats (table, JSON, CSV) for CLI commands.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from quake_cli.models import QuakeFeature, QuakeResponse

# Initialize Rich console
console = Console()

# Output format options
OutputFormat = typer.Option(
    "table",
    "--format",
    "-f",
    help="Output format",
    case_sensitive=False,
    show_choices=True,
)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display.

    Args:
        dt: The datetime object to format

    Returns:
        Formatted datetime string in YYYY-MM-DD HH:MM:SS format

    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2023, 12, 25, 14, 30, 45)
        >>> format_datetime(dt)
        '2023-12-25 14:30:45'

        >>> dt2 = datetime(2024, 1, 1, 0, 0, 0)
        >>> format_datetime(dt2)
        '2024-01-01 00:00:00'
    """
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
            json_output: Any
            if hasattr(data, "model_dump"):
                json_output = data.model_dump()
            elif isinstance(data, list):
                json_output = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in data
                ]
            else:
                json_output = data

            json_str = json.dumps(json_output, indent=2, default=str)

            if output_file:
                output_file.write_text(json_str)
                print(f"JSON data written to {output_file!s}")
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
                console.print(
                    "[red]CSV format only supported for earthquake data[/red]"
                )
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
                print(f"CSV data written to {output_file!s}")
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
                    # Ensure data is a list of QuakeFeature objects
                    if all(isinstance(item, QuakeFeature) for item in data):
                        table = create_quakes_table(list(data))
                        console.print(table)
                    else:
                        console.print(data)
                case _:
                    # For other data types, show as JSON-like format
                    console.print(data)

        case _:
            console.print(f"[red]Unknown format: {format_type}[/red]")

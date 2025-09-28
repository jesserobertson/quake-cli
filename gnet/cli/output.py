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

from gnet.models import cap, intensity, quake, strong_motion, volcano

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
    features: list[quake.Feature], title: str = "Earthquakes"
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
            format_datetime(props.time.origin),
            f"{props.magnitude.value:.1f}",
            f"{abs(props.location.elevation or 0):.1f}",  # Convert elevation back to depth
            str(props.intensity.mmi) if props.intensity else "-",
            props.quality.level,
            props.location.locality or "Unknown",
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
                                props.time.origin.isoformat(),
                                props.magnitude.value,
                                abs(
                                    props.location.elevation or 0
                                ),  # Convert elevation back to depth
                                props.intensity.mmi if props.intensity else None,
                                props.quality.level,
                                props.location.locality or "Unknown",
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
                            props.time.origin.isoformat(),
                            props.magnitude.value,
                            abs(
                                props.location.elevation or 0
                            ),  # Convert elevation back to depth
                            props.intensity.mmi if props.intensity else None,
                            props.quality.level,
                            props.location.locality or "Unknown",
                            geom.longitude,
                            geom.latitude,
                        ]
                    )
                console.print(output.getvalue())

        case "table":
            # Handle table output using direct type matching
            match data:
                case quake.Response():
                    table = create_quakes_table(data.features)
                    console.print(table)
                case quake.Feature():
                    table = create_quakes_table([data], "Earthquake Details")
                    console.print(table)
                case cap.CapFeed():
                    # CAP feeds are handled directly in the cap command
                    return
                case strong_motion.Response():
                    # Strong motion data is handled directly in the strong motion command
                    return
                case list() | tuple() if data and all(
                    isinstance(item, quake.Feature) for item in data
                ):
                    table = create_quakes_table(list(data))
                    console.print(table)
                case list() | tuple() if data:
                    console.print(data)
                case _:
                    # For other data types (like stats), output as JSON for readability
                    json_str = json.dumps(data, indent=2, default=str)
                    console.print(json_str)

        case _:
            console.print(f"[red]Unknown format: {format_type}[/red]")


def create_intensity_table(response: intensity.Response, intensity_type: str) -> Table:
    """Create a rich table for intensity data."""
    title = f"Intensity Data ({intensity_type.title()})"
    if response.count_mmi:
        total_reports = sum(response.count_mmi.values())
        title += f" - {total_reports} total reports"

    table = Table(title=title, show_header=True, header_style="bold magenta")

    table.add_column("Longitude", justify="right", style="cyan")
    table.add_column("Latitude", justify="right", style="cyan")
    table.add_column("MMI", justify="right", style="red")

    if intensity_type == "reported":
        table.add_column("Reports", justify="right", style="yellow")

    for feature in response.features:
        geom = feature.geometry
        props = feature.properties

        row = [
            f"{geom.coordinates[0]:.4f}",
            f"{geom.coordinates[1]:.4f}",
            str(props.intensity.mmi),
        ]

        if intensity_type == "reported" and props.intensity.count is not None:
            row.append(str(props.intensity.count))

        table.add_row(*row)

    return table


def create_volcano_alerts_table(response: volcano.Response) -> Table:
    """Create a rich table for volcano alert data."""
    table = Table(
        title="Volcano Alert Levels", show_header=True, header_style="bold magenta"
    )

    table.add_column("Volcano", style="cyan")
    table.add_column("Level", justify="center", style="red")
    table.add_column("Color", justify="center", style="yellow")
    table.add_column("Activity", style="white")
    table.add_column("Location", style="dim")

    for feature in response.features:
        props = feature.properties
        geom = feature.geometry

        # Color the alert level based on the color code
        level_color = "green"
        if props.alert.color.lower() in ["yellow", "orange"]:
            level_color = "yellow"
        elif props.alert.color.lower() == "red":
            level_color = "red"

        table.add_row(
            props.title,
            f"[{level_color}]{props.alert.level}[/{level_color}]",
            f"[{level_color}]{props.alert.color.upper()}[/{level_color}]",
            props.alert.activity,
            f"{geom.coordinates[1]:.2f}, {geom.coordinates[0]:.2f}",
        )

    return table


def create_volcano_quakes_table(response: volcano.quake.Response) -> Table:
    """Create a rich table for volcano earthquake data."""
    table = Table(
        title="Volcano Earthquakes", show_header=True, header_style="bold magenta"
    )

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Time", style="green")
    table.add_column("Magnitude", justify="right", style="yellow")
    table.add_column("Depth (km)", justify="right", style="blue")
    table.add_column("Volcano", style="red")
    table.add_column("Location", style="white")

    for feature in response.features:
        props = feature.properties

        table.add_row(
            props.publicID,
            format_datetime(props.time.origin),
            f"{props.magnitude.value:.1f}",
            f"{abs(props.location.elevation or 0.0):.1f}",  # Convert elevation back to depth
            getattr(props, "volcanoID", None) or "-",
            props.location.locality,
        )

    return table


def format_intensity_output(
    data: intensity.Response, format_type: str, intensity_type: str
) -> None:
    """Format and output intensity data."""
    match format_type.lower():
        case "table":
            table = create_intensity_table(data, intensity_type)
            console.print(table)
        case "json":
            output_data(data, "json")
        case "csv":
            console.print(
                "[yellow]CSV format not yet supported for intensity data[/yellow]"
            )
            output_data(data, "json")
        case _:
            console.print(f"[red]Unknown format: {format_type}[/red]")


def format_volcano_alerts_output(data: volcano.Response, format_type: str) -> None:
    """Format and output volcano alert data."""
    match format_type.lower():
        case "table":
            table = create_volcano_alerts_table(data)
            console.print(table)
        case "json":
            output_data(data, "json")
        case "csv":
            console.print(
                "[yellow]CSV format not yet supported for volcano alerts[/yellow]"
            )
            output_data(data, "json")
        case _:
            console.print(f"[red]Unknown format: {format_type}[/red]")


def format_volcano_quakes_output(
    data: volcano.quake.Response, format_type: str
) -> None:
    """Format and output volcano earthquake data."""
    match format_type.lower():
        case "table":
            table = create_volcano_quakes_table(data)
            console.print(table)
        case "json":
            output_data(data, "json")
        case "csv":
            console.print(
                "[yellow]CSV format not yet supported for volcano earthquakes[/yellow]"
            )
            output_data(data, "json")
        case _:
            console.print(f"[red]Unknown format: {format_type}[/red]")

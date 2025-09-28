"""
Strong motion command implementation.

This module provides the 'strong-motion' command for fetching accelerometer
and ground motion data for specific earthquakes.
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
async def get_strong_motion(
    earthquake_id: str = typer.Argument(..., help="Earthquake public ID"),
    format: str = OutputFormat,
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    network: str = typer.Option(None, "--network", "-n", help="Filter by network"),
    min_mmi: float = typer.Option(None, "--min-mmi", help="Minimum MMI threshold"),
    max_distance: float = typer.Option(
        None, "--max-distance", help="Maximum distance from epicenter (km)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Get strong motion data for a specific earthquake."""

    # Configure logging for this command
    configure_logging(verbose)

    # Use stderr console for progress to avoid interfering with any output
    progress_console = get_progress_console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=progress_console,
    ) as progress:
        task = progress.add_task(
            f"Fetching strong motion data for {earthquake_id}...", total=None
        )

        async with GeoNetClient() as client:
            result = await client.get_strong_motion(earthquake_id)
            response = handle_result(result)

        progress.update(
            task, completed=True, description="Strong motion data retrieved"
        )

    # Apply filters
    filtered_features = response.features

    if network:
        filtered_features = [
            f
            for f in filtered_features
            if f.properties.network.lower() == network.lower()
        ]

    if min_mmi is not None:
        filtered_features = [
            f
            for f in filtered_features
            if f.properties.mmi is not None and f.properties.mmi >= min_mmi
        ]

    if max_distance is not None:
        filtered_features = [
            f
            for f in filtered_features
            if f.properties.distance is not None
            and f.properties.distance <= max_distance
        ]

    # Create filtered response for output
    filtered_response = response.model_copy()
    filtered_response.features = filtered_features

    output_data(filtered_response, format, output)

    if format.lower() == "table":
        # Show earthquake metadata
        metadata_table = Table(
            title=f"Earthquake Information - {earthquake_id}",
            show_header=True,
            header_style="bold blue",
        )
        metadata_table.add_column("Property", style="cyan")
        metadata_table.add_column("Value", style="white")

        if response.metadata.magnitude:
            metadata_table.add_row("Magnitude", f"{response.metadata.magnitude:.1f}")
        if response.metadata.depth:
            metadata_table.add_row("Depth", f"{response.metadata.depth:.1f} km")
        if response.metadata.description:
            metadata_table.add_row("Description", response.metadata.description)
        if response.metadata.latitude and response.metadata.longitude:
            metadata_table.add_row(
                "Location",
                f"{response.metadata.latitude:.4f}°, {response.metadata.longitude:.4f}°",
            )

        console.print(metadata_table)

        # Show station data
        stations_table = Table(
            title=f"Strong Motion Stations ({len(filtered_features)} stations)",
            show_header=True,
            header_style="bold magenta",
        )
        stations_table.add_column("Station", style="cyan", width=12)
        stations_table.add_column("Network", style="blue", width=8)
        stations_table.add_column(
            "Distance (km)", justify="right", style="green", width=12
        )
        stations_table.add_column("MMI", justify="right", style="red", width=6)
        stations_table.add_column(
            "PGA-H (g)", justify="right", style="yellow", width=10
        )
        stations_table.add_column(
            "PGA-V (g)", justify="right", style="yellow", width=10
        )
        stations_table.add_column("Location", style="white")

        for feature in filtered_features:
            props = feature.properties

            distance_str = (
                f"{props.distance:.1f}" if props.distance is not None else "-"
            )
            mmi_str = f"{props.mmi:.1f}" if props.mmi is not None else "-"
            pga_h_str = (
                f"{props.pga_horizontal:.3f}"
                if props.pga_horizontal is not None
                else "-"
            )
            pga_v_str = (
                f"{props.pga_vertical:.3f}" if props.pga_vertical is not None else "-"
            )

            stations_table.add_row(
                props.station,
                props.network,
                distance_str,
                mmi_str,
                pga_h_str,
                pga_v_str,
                props.location,
            )

        console.print(stations_table)

        # Show summary statistics
        if filtered_features:
            stats_table = Table(
                title="Summary Statistics", show_header=True, header_style="bold blue"
            )
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="white")

            # Calculate stats
            distances = [
                f.properties.distance
                for f in filtered_features
                if f.properties.distance is not None
            ]
            mmis = [
                f.properties.mmi
                for f in filtered_features
                if f.properties.mmi is not None
            ]
            pga_h_values = [
                f.properties.pga_horizontal
                for f in filtered_features
                if f.properties.pga_horizontal is not None
            ]

            stats_table.add_row("Total Stations", str(len(filtered_features)))

            if distances:
                stats_table.add_row("Closest Station", f"{min(distances):.1f} km")
                stats_table.add_row("Farthest Station", f"{max(distances):.1f} km")

            if mmis:
                stats_table.add_row("Max MMI", f"{max(mmis):.1f}")

            if pga_h_values:
                stats_table.add_row("Max PGA-H", f"{max(pga_h_values):.3f} g")

            # Network breakdown
            networks: dict[str, int] = {}
            for feature in filtered_features:
                net = feature.properties.network
                networks[net] = networks.get(net, 0) + 1

            for network_name, count in sorted(networks.items()):
                stats_table.add_row(f"Network {network_name}", f"{count} stations")

            console.print(stats_table)

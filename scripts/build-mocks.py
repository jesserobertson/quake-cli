#!/usr/bin/env python3
"""
Script to fetch real GeoNet API data and generate mock responses for testing.

This script connects to the actual GeoNet API to gather real response data,
then saves it as JSON files that can be used for offline testing.

Usage:
    python scripts/build-mocks.py [--verbose] [--output-dir DIR]
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gnet.client import GeoNetClient

console = Console()


class MockDataGenerator:
    """Generates mock data from real GeoNet API responses."""

    def __init__(self, output_dir: Path = Path("tests/mocks/data")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_mocks = []

    async def generate_all_mocks(self, verbose: bool = False) -> None:
        """Generate all mock data files."""
        console.print("🌐 [bold blue]Connecting to GeoNet API to generate mock data[/bold blue]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            async with GeoNetClient() as client:
                # Test basic connectivity first
                health_task = progress.add_task("Testing API connectivity...", total=None)
                try:
                    health_result = await client.health_check()
                    if health_result.is_err():
                        console.print(f"[red]❌ API health check failed: {health_result.unwrap_err()}[/red]")
                        return
                    progress.update(health_task, completed=True, description="✅ API connectivity verified")
                except Exception as e:
                    console.print(f"[red]❌ Failed to connect to API: {e}[/red]")
                    return

                # Generate all mock data
                tasks = [
                    ("quakes_all", "Fetching recent earthquakes (all)"),
                    ("quakes_mmi4", "Fetching significant earthquakes (MMI≥4)"),
                    ("quake_stats", "Fetching earthquake statistics"),
                    ("intensity_reported", "Fetching reported intensity data"),
                    ("intensity_measured", "Fetching measured intensity data"),
                    ("volcano_alerts", "Fetching volcano alert levels"),
                    ("cap_feed", "Fetching CAP alert feed"),
                    ("strong_motion", "Fetching strong motion data"),
                ]

                for task_name, description in tasks:
                    task = progress.add_task(description, total=None)
                    try:
                        await self._generate_mock(client, task_name, verbose)
                        progress.update(task, completed=True, description=f"✅ {description.replace('Fetching', 'Generated')}")
                    except Exception as e:
                        progress.update(task, completed=True, description=f"❌ {description} failed")
                        if verbose:
                            console.print(f"[red]Error generating {task_name}: {e}[/red]")

        # Generate summary
        self._generate_summary()
        console.print(f"\n🎉 [bold green]Generated {len(self.generated_mocks)} mock data files[/bold green]")
        console.print(f"📁 Mock data saved to: {self.output_dir}")

    async def _generate_mock(self, client: GeoNetClient, mock_type: str, verbose: bool) -> None:
        """Generate a specific type of mock data."""
        data = None
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "source": "GeoNet API",
            "mock_type": mock_type,
        }

        try:
            match mock_type:
                case "quakes_all":
                    result = await client.get_quakes(limit=10)
                    if result.is_ok():
                        data = result.unwrap().model_dump()
                        metadata["description"] = "Recent earthquakes (up to 10)"
                        metadata["endpoint"] = "/quake?MMI=-1"

                case "quakes_mmi4":
                    result = await client.get_quakes(mmi=4, limit=5)
                    if result.is_ok():
                        data = result.unwrap().model_dump()
                        metadata["description"] = "Significant earthquakes (MMI≥4, up to 5)"
                        metadata["endpoint"] = "/quake?MMI=4"

                case "quake_stats":
                    result = await client.get_quake_stats()
                    if result.is_ok():
                        data = result.unwrap()
                        metadata["description"] = "Earthquake statistics and counts"
                        metadata["endpoint"] = "/quake/stats"

                case "intensity_reported":
                    result = await client.get_intensity("reported")
                    if result.is_ok():
                        data = result.unwrap().model_dump()
                        metadata["description"] = "Reported intensity data from user experiences"
                        metadata["endpoint"] = "/intensity?type=reported"

                case "intensity_measured":
                    result = await client.get_intensity("measured")
                    if result.is_ok():
                        data = result.unwrap().model_dump()
                        metadata["description"] = "Measured intensity data from instruments"
                        metadata["endpoint"] = "/intensity?type=measured"

                case "volcano_alerts":
                    result = await client.get_volcano_alerts()
                    if result.is_ok():
                        data = result.unwrap().model_dump()
                        metadata["description"] = "Current volcano alert levels"
                        metadata["endpoint"] = "/volcano/val"

                case "cap_feed":
                    result = await client.get_cap_feed()
                    if result.is_ok():
                        data = result.unwrap().model_dump()
                        metadata["description"] = "CAP alert feed for significant earthquakes"
                        metadata["endpoint"] = "/cap/1.2/GPA1.0/feed/atom1.0/quake"

                case "strong_motion":
                    # For strong motion, we need an earthquake ID, so let's get one first
                    quakes_result = await client.get_quakes(mmi=4, limit=1)
                    if quakes_result.is_ok() and quakes_result.unwrap().features:
                        earthquake_id = quakes_result.unwrap().features[0].properties.publicID
                        result = await client.get_strong_motion(earthquake_id)
                        if result.is_ok():
                            data = result.unwrap().model_dump()
                            metadata["description"] = f"Strong motion data for earthquake {earthquake_id}"
                            metadata["endpoint"] = f"/intensity/strong/processed/{earthquake_id}"
                            metadata["earthquake_id"] = earthquake_id

            if data is not None:
                # Save the mock data
                mock_file = {
                    "metadata": metadata,
                    "data": data,
                }

                file_path = self.output_dir / f"{mock_type}.json"
                with open(file_path, "w") as f:
                    json.dump(mock_file, f, indent=2, default=str)

                self.generated_mocks.append({
                    "type": mock_type,
                    "file": str(file_path),
                    "description": metadata.get("description", ""),
                })

                if verbose:
                    console.print(f"✅ Generated {mock_type}: {len(str(data))} chars")
            else:
                if verbose:
                    console.print(f"❌ No data returned for {mock_type}")

        except Exception as e:
            if verbose:
                console.print(f"❌ Error generating {mock_type}: {e}")
            raise

    def _generate_summary(self) -> None:
        """Generate a summary file of all generated mocks."""
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_mocks": len(self.generated_mocks),
            "mocks": self.generated_mocks,
            "usage": {
                "description": "Mock data generated from real GeoNet API responses",
                "usage": "Import these files in integration tests to simulate API responses",
                "regeneration": "Run 'python scripts/build-mocks.py' to regenerate with fresh data",
            },
        }

        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate mock data from GeoNet API for testing"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tests/mocks/data"),
        help="Output directory for mock data files"
    )

    args = parser.parse_args()

    generator = MockDataGenerator(args.output_dir)
    await generator.generate_all_mocks(args.verbose)


if __name__ == "__main__":
    asyncio.run(main())
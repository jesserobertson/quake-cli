# gnet

[![CI](https://github.com/jesserobertson/quake-cli/workflows/CI/badge.svg)](https://github.com/jesserobertson/quake-cli/actions)
[![codecov](https://codecov.io/gh/jesserobertson/quake-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/jesserobertson/quake-cli)
[![PyPI version](https://badge.fury.io/py/gnet.svg)](https://badge.fury.io/py/gnet)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jesserobertson.github.io/quake-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Python library and CLI tool for accessing GeoNet's complete suite of geological hazard monitoring APIs, including earthquakes, volcanoes, tsunami alerts, and strong motion data.

## Features

### 🌍 Comprehensive GeoNet API Coverage
- **Earthquakes** - Real-time earthquake data, history, and statistics
- **Volcano Monitoring** - Volcanic alert levels and earthquake activity
- **Intensity Data** - Reported and measured shaking intensity (MMI)
- **CAP Alerts** - Common Alerting Protocol feeds for emergency systems
- **Strong Motion** - Accelerometer and ground motion data from seismic stations
- **90%+ API Coverage** - Access to nearly all GeoNet API endpoints

### ⚡ Modern Architecture & Performance
- **Async Performance** - Fast async HTTP client with automatic retries and error handling
- **Result-Based Error Handling** - Functional error handling with composable Result types
- **Type-Safe Data Models** - Clean hierarchical Pydantic models (quake.Magnitude, volcano.quake.Properties)
- **Modern Python 3.12+** - Uses latest Python features with comprehensive type hints
- **Pattern Matching** - Clean match/case syntax for type-safe data handling

### 💻 Powerful CLI Interface
- **Hierarchical Commands** - Intuitive command structure: `gnet quake`, `gnet volcano`
- **Multiple Output Formats** - JSON, CSV, and rich formatted table output
- **Advanced Filtering** - Filter by magnitude, MMI, distance, network, time ranges
- **Smart Progress Indicators** - Progress bars for table output, silent for structured data
- **File Export** - Save results directly to files with `--output`

### 🛠️ Developer Experience
- **Lightweight Dependencies** - Core dependencies only for production use
- **Comprehensive Testing** - 100+ tests with full CLI and API coverage
- **100% Quality Compliance** - Full ruff and mypy compliance with automated checks
- **Tested Documentation** - All examples are automatically tested for accuracy

## Quick Start

### Installation

```bash
# Install the comprehensive GeoNet CLI
pip install gnet
```

### Basic Usage

```bash
# List recent earthquakes
gnet quake list --limit 10

# Get volcano alert levels
gnet volcano alerts

# Get strong motion data for an earthquake
gnet quake strong-motion 2020p666015

# Get CAP emergency alert feeds
gnet quake cap-feed
```

## CLI Commands

### Earthquake Commands (`gnet quake` or `gnet q`)

```bash
# Core earthquake data
gnet quake list --min-magnitude 4.0 --limit 10
gnet quake get 2024p123456
gnet quake history 2024p123456
gnet quake stats
gnet quake health

# Intensity and shaking data
gnet quake intensity reported --publicid 2024p123456
gnet quake intensity-reported --aggregation max
gnet quake intensity-measured

# Emergency alerting
gnet quake cap-feed --format json
gnet quake cap-alert 2024p123456

# Strong motion/accelerometer data
gnet quake strong-motion 2020p666015 --min-mmi 3 --max-distance 100
gnet quake strong-motion 2020p666015 --network NZ --format json
```

### Volcano Commands (`gnet volcano` or `gnet v`)

```bash
# Volcano monitoring
gnet volcano alerts
gnet volcano alerts --volcano ruapehu
gnet volcano quakes --volcano ruapehu --limit 10
```

### Advanced CLI Examples

```bash
# Export earthquake data for analysis
gnet quake list --min-magnitude 5.0 --format csv --output large_quakes.csv

# Monitor volcano activity with JSON output for processing
gnet volcano alerts --format json | jq '.features[] | {volcano: .properties.title, level: .properties.alert.level, color: .properties.alert.color}'

# Get strong motion stations near epicenter
gnet quake strong-motion 2020p666015 --max-distance 50 --min-mmi 4

# Export CAP alerts for emergency systems
gnet quake cap-feed --format json --output emergency_alerts.json

# Combined earthquake and intensity analysis
gnet quake get 2024p123456 --format json && gnet quake intensity reported --publicid 2024p123456
```

### Working with jq for Data Processing

```bash
# Get earthquake count by magnitude for last 7 days
gnet quake stats | jq '.magnitudeCount.days7'

# Find strongest recent earthquakes
gnet quake list --format json --limit 100 | jq '.features | sort_by(.properties.magnitude) | reverse | .[0:5]'

# Extract volcano alert levels
gnet volcano alerts --format json | jq '.features[] | {volcano: .properties.title, level: .properties.alert.level}'

# Analyze strong motion data
gnet quake strong-motion 2020p666015 --format json | jq '.features[] | select(.properties.mmi >= 4) | {station: .properties.station, mmi: .properties.mmi, distance: .properties.distance}'

# Monitor CAP feed for significant events
gnet quake cap-feed --format json | jq '.entries[] | {title: .title, published: .published}'
```

## Python Library Usage

### Basic Library Usage

```python
import asyncio
from gnet.client import GeoNetClient
from logerr import Ok, Err

async def get_geological_data():
    async with GeoNetClient() as client:
        # Get recent earthquakes
        result = await client.get_quakes(limit=5)
        match result:
            case Ok(response):
                for quake in response.features:
                    props = quake.properties
                    print(f"M{props.magnitude.value:.1f} at {props.location.locality}")
            case Err(error):
                print(f"Error: {error}")

        # Get volcano alerts
        volcano_result = await client.get_volcano_alerts()
        match volcano_result:
            case Ok(response):
                for volcano in response.features:
                    props = volcano.properties
                    print(f"{props.title}: {props.alert.color} alert level {props.alert.level}")
            case Err(error):
                print(f"Volcano error: {error}")

asyncio.run(get_geological_data())
```

### Advanced Library Usage

```python
import asyncio
from gnet.client import GeoNetClient
from logerr import Ok, Err

async def comprehensive_monitoring():
    async with GeoNetClient() as client:
        # Get strong motion data
        strong_motion_result = await client.get_strong_motion("2020p666015")
        match strong_motion_result:
            case Ok(response):
                print(f"Earthquake: M{response.metadata.magnitude} at {response.metadata.description}")
                high_intensity = response.get_high_intensity_stations(min_mmi=4.0)
                print(f"High intensity stations: {len(high_intensity)}")
            case Err(error):
                print(f"Strong motion error: {error}")

        # Get intensity data
        intensity_result = await client.get_intensity("reported", aggregation="max")
        match intensity_result:
            case Ok(response):
                print(f"Intensity reports: {response.count} stations")
                if response.count_mmi:
                    total_reports = sum(response.count_mmi.values())
                    print(f"Total reports: {total_reports}")
            case Err(error):
                print(f"Intensity error: {error}")

        # Get CAP alerts
        cap_result = await client.get_cap_feed()
        match cap_result:
            case Ok(feed):
                print(f"CAP Feed: {feed.title}")
                print(f"Recent alerts: {feed.count}")
            case Err(error):
                print(f"CAP error: {error}")

asyncio.run(comprehensive_monitoring())
```

## Core API Reference

### GeoNet Client

The `GeoNetClient` provides access to all GeoNet APIs:

```python
from gnet.client import GeoNetClient

async with GeoNetClient() as client:
    # Earthquake data
    earthquakes = await client.get_quakes(limit=20, mmi=-1)
    specific_quake = await client.get_quake("2024p123456")
    quake_history = await client.get_quake_history("2024p123456")
    earthquake_stats = await client.get_quake_stats()

    # Volcano monitoring
    volcano_alerts = await client.get_volcano_alerts(volcano_id="ruapehu")
    volcano_quakes = await client.get_volcano_quakes(volcano_id="ruapehu", limit=10)

    # Intensity data
    reported_intensity = await client.get_intensity("reported", aggregation="max")
    measured_intensity = await client.get_intensity("measured")

    # Strong motion data
    strong_motion = await client.get_strong_motion("2020p666015")

    # CAP emergency alerts
    cap_feed = await client.get_cap_feed()
    cap_alert = await client.get_cap_alert("2024p123456")

    # Health check
    health = await client.health_check()
```

### Data Models

Access structured data through clean hierarchical models:

```python
# Earthquake data
for quake in response.features:
    props = quake.properties
    print(f"Magnitude: {props.magnitude.value} ({props.magnitude.type})")
    print(f"Location: {props.location.locality}")
    print(f"Coordinates: {props.location.latitude}, {props.location.longitude}")
    print(f"Depth: {abs(props.location.elevation)} km")
    print(f"Quality: {props.quality.level}")
    if props.intensity:
        print(f"MMI: {props.intensity.mmi}")

# Volcano data
for volcano in volcano_response.features:
    props = volcano.properties
    print(f"Volcano: {props.title}")
    print(f"Alert Level: {props.alert.level}")
    print(f"Alert Color: {props.alert.color}")
    print(f"Activity: {props.alert.activity}")

# Strong motion data
for station in strong_motion_response.features:
    props = station.properties
    print(f"Station: {props.station} ({props.network})")
    print(f"Distance: {props.distance} km")
    print(f"MMI: {props.mmi}")
    if props.pga_horizontal:
        print(f"PGA-H: {props.pga_horizontal} g")
```

### Error Handling

The library uses Result types for predictable error handling:

```python
from logerr import Ok, Err

result = await client.get_quake("invalid_id")
match result:
    case Ok(earthquake):
        print(f"Found: {earthquake.properties.location.locality}")
    case Err(error):
        print(f"Error: {error}")

# Functional composition
result = (await client.get_quakes())
    .then(lambda resp: resp.filter_by_magnitude(4.0, 6.0))
    .map(lambda resp: resp.features[:10])
```

## Installation Options

### Basic Installation

```bash
pip install gnet
```

### Development Installation

```bash
git clone https://github.com/jesserobertson/quake-cli.git
cd quake-cli
pixi install
```

## Data Sources & Attribution

This tool accesses geological hazard data from:

- **[GeoNet](https://www.geonet.org.nz/)** - New Zealand's geological hazard monitoring system
- **Real-time earthquake monitoring** across New Zealand and surrounding regions
- **Volcano monitoring networks** for active volcanic systems
- **Strong motion accelerometer networks** for ground shaking analysis
- **Emergency alerting systems** via Common Alerting Protocol (CAP)

**Data Attribution**: Geological hazard data provided by GeoNet (https://www.geonet.org.nz/)

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Documentation

- **[API Documentation](https://www.geonet.org.nz/data/supplementary/webapi)** - GeoNet API reference
- **[Installation Guide](docs/content/installation.md)** - Detailed setup instructions
- **[Examples](docs/content/examples.md)** - Comprehensive usage examples
- **[Development Guide](docs/content/development.md)** - Contributing guidelines

## Requirements

- **Python 3.12+** - Uses modern Python features including pattern matching

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: https://github.com/jesserobertson/quake-cli/issues
- **Discussions**: https://github.com/jesserobertson/quake-cli/discussions
- **GeoNet API**: https://www.geonet.org.nz/data/supplementary/webapi

## Acknowledgments

- **Data Source**: [GeoNet](https://www.geonet.org.nz/) - New Zealand's geological hazard monitoring system
- **HTTP Client**: [httpx](https://www.python-httpx.org/) for async performance
- **Data Models**: [Pydantic](https://docs.pydantic.dev/) for type safety
- **Error Handling**: [logerr](https://pypi.org/project/logerr/) for Result types
- **CLI Framework**: [Typer](https://typer.tiangolo.com/) for command-line interface
- **Rich Output**: [Rich](https://rich.readthedocs.io/) for beautiful terminal output

---

Made with ❤️ by [Jess Robertson](https://github.com/jesserobertson) for the New Zealand geological monitoring community.
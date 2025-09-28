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

The CLI outputs valid JSON, making it perfect for use with `jq` for advanced data processing:

#### Basic Statistics and Filtering

```bash
# Get earthquake count by magnitude for last 7 days
gnet quake stats | jq '.magnitudeCount.days7'

# Find total earthquakes in the last 365 days
gnet quake stats | jq '.magnitudeCount.days365 | map(.) | add'

# Get the largest earthquake magnitude from recent data
gnet quake list --format json --limit 100 | jq '[.features[].properties.magnitude.value] | max'

# Count earthquakes above magnitude 4.0
gnet quake list --format json --min-magnitude 4.0 | jq '.features | length'

# Find strongest recent earthquakes
gnet quake list --format json --limit 100 | jq '[.features | sort_by(.properties.magnitude.value) | reverse | .[0:5]]'
```

#### Location and Coordinate Analysis

```bash
# Extract earthquake locations and magnitudes
gnet quake list --format json --limit 10 | jq '.features[] | {magnitude: .properties.magnitude.value, location: .properties.location.locality}'

# Get coordinates of recent large earthquakes
gnet quake list --format json --min-magnitude 5.0 | jq '.features[] | {magnitude: .properties.magnitude.value, lat: .properties.location.latitude, lon: .properties.location.longitude, depth: .properties.location.elevation}'

# Monitor recent earthquake activity with formatted output
gnet quake list --limit 5 --format json | jq '.features[] | "\(.properties.time.origin): M\(.properties.magnitude.value) at \(.properties.location.locality)"'

# Get detailed earthquake information with coordinates
gnet quake list --format json --limit 1 | jq '.features[0] | {id: .properties.publicID, magnitude: .properties.magnitude.value, depth: .properties.location.elevation, location: .properties.location.locality, coordinates: [.properties.location.longitude, .properties.location.latitude]}'
```

#### Time-Based Analysis

```bash
# Daily earthquake rates for the last week
gnet quake stats | jq '.rate.perDay | to_entries | sort_by(.key) | reverse | .[0:7] | map({date: .key, count: .value})'

# Group earthquakes by date
gnet quake list --format json --limit 50 | jq '.features | group_by(.properties.time.origin[0:10]) | map({date: .[0].properties.time.origin[0:10], count: length, max_magnitude: [.[] | .properties.magnitude.value] | max})'

# Find earthquakes from the last 24 hours (Linux)
gnet quake list --format json --limit 100 | jq --argjson yesterday $(date -d "1 day ago" +%s) '.features[] | select((.properties.time.origin | strptime("%Y-%m-%d %H:%M:%S.%f+00:00") | mktime) > $yesterday)'

# Find earthquakes from the last 24 hours (macOS)
gnet quake list --format json --limit 100 | jq --argjson yesterday $(date -v-1d +%s) '.features[] | select((.properties.time.origin | strptime("%Y-%m-%d %H:%M:%S.%f+00:00") | mktime) > $yesterday)'
```

#### Volcano Monitoring

```bash
# Extract volcano alert levels
gnet volcano alerts --format json | jq '.features[] | {volcano: .properties.title, level: .properties.alert.level, color: .properties.alert.color}'

# Find volcanoes with elevated alert levels
gnet volcano alerts --format json | jq '.features[] | select(.properties.alert.level > 1) | {volcano: .properties.title, level: .properties.alert.level, activity: .properties.alert.activity}'

# Monitor volcano earthquake activity
gnet volcano quakes --volcano ruapehu --format json | jq '.features[] | {time: .properties.time.origin, magnitude: .properties.magnitude.value, depth: .properties.location.elevation}'
```

#### Strong Motion and Intensity Analysis

```bash
# Analyze strong motion data for high intensity stations
gnet quake strong-motion 2020p666015 --format json | jq '.features[] | select(.properties.mmi >= 4) | {station: .properties.station, mmi: .properties.mmi, distance: .properties.distance, network: .properties.network}'

# Find stations with significant ground acceleration
gnet quake strong-motion 2020p666015 --format json | jq '.features[] | select(.properties.pga_horizontal > 0.1) | {station: .properties.station, pga: .properties.pga_horizontal, mmi: .properties.mmi}'

# Get intensity reports summary
gnet quake intensity-reported --format json | jq 'if .count_mmi then {total_reports: (.count_mmi | map(.) | add), intensity_distribution: .count_mmi} else {message: "No intensity data available"} end'
```

#### Emergency Alerting and CAP Feeds

```bash
# Monitor CAP feed for significant events
gnet quake cap-feed --format json | jq '.entries[] | {title: .title, published: .published, summary: .summary}'

# Extract recent CAP alerts with details
gnet quake cap-feed --format json | jq '.entries[0:5] | map({title: .title, published: .published, id: .id})'

# Get specific CAP alert information
gnet quake cap-alert 2024p123456 --format json | jq '{title: .title, published: .published, content: .content}'
```

#### Advanced Processing Workflows

```bash
# Create earthquake summary report
gnet quake list --format json --limit 20 | jq '{report_date: now | strftime("%Y-%m-%d"), total_earthquakes: (.features | length), magnitude_range: {min: (.features | map(.properties.magnitude.value) | min), max: (.features | map(.properties.magnitude.value) | max)}, locations: [.features[] | .properties.location.locality] | unique}'

# Find earthquakes near specific coordinates (example: Wellington area)
gnet quake list --format json --limit 100 | jq '.features[] | select((.properties.location.latitude > -41.5 and .properties.location.latitude < -41.0) and (.properties.location.longitude > 174.5 and .properties.location.longitude < 175.0)) | {magnitude: .properties.magnitude.value, location: .properties.location.locality, time: .properties.time.origin}'

# Compare earthquake activity across different time periods
gnet quake stats | jq '{recent: .magnitudeCount.days7, monthly: .magnitudeCount.days30, yearly: .magnitudeCount.days365} | {recent_rate: (.recent | map(.) | add), monthly_avg: ((.monthly | map(.) | add) / 30), yearly_avg: ((.yearly | map(.) | add) / 365)}'

# Extract earthquake depths and analyze distribution
gnet quake list --format json --limit 50 | jq '.features | map(.properties.location.elevation) | group_by(. > -50) | {shallow: (.[1] // []) | length, deep: (.[0] // []) | length}'

# Find earthquakes with specific quality ratings
gnet quake list --format json --limit 100 | jq '.features[] | select(.properties.quality.level == "best") | {id: .properties.publicID, magnitude: .properties.magnitude.value, quality: .properties.quality.level}'

# Monitor earthquake swarm activity (multiple events in same area)
gnet quake list --format json --limit 50 | jq '.features | group_by(.properties.location.locality) | map(select(length > 1)) | map({location: .[0].properties.location.locality, count: length, magnitudes: [.[] | .properties.magnitude.value]})'

# Generate a quick earthquake alert summary
gnet quake list --format json --limit 10 | jq '.features | map(select(.properties.magnitude.value >= 4.0)) | map("ALERT: M\(.properties.magnitude.value) earthquake at \(.properties.location.locality) - \(.properties.time.origin)")'
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
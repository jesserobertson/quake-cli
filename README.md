# quake-cli

[![CI](https://github.com/jesserobertson/quake-cli/workflows/CI/badge.svg)](https://github.com/jesserobertson/quake-cli/actions)
[![codecov](https://codecov.io/gh/jesserobertson/quake-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/jesserobertson/quake-cli)
[![PyPI version](https://badge.fury.io/py/quake_cli.svg)](https://badge.fury.io/py/quake_cli)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jesserobertson.github.io/quake-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern Python library and CLI tool for querying earthquake data from the GeoNet API with lightweight dependencies and modular architecture.

## Features

### Core Library
- 🌍 **GeoNet API Integration** - Query real-time earthquake data from New Zealand's GeoNet service
- ⚡ **Async Performance** - Fast async HTTP client with automatic retries and error handling
- 🔍 **Flexible Filtering** - Filter earthquakes by magnitude, MMI, location, and time
- 📊 **Type-Safe Data Models** - Modular Pydantic models for reliable earthquake data structures
- 🔄 **Result-Based Error Handling** - Functional error handling with composable Result types
- 🚀 **Modern Python 3.12+** - Uses latest Python features with comprehensive type hints
- 📖 **Tested Examples** - All documentation examples are automatically tested for accuracy

### CLI Tool
- 💻 **Command-Line Interface** - Full-featured CLI for interactive earthquake data queries
- 📋 **Multiple Output Formats** - JSON, CSV, and formatted table output
- 🎯 **Smart Progress Indicators** - Progress bars for table output, silent for structured data
- 📂 **File Export** - Save results directly to files
- 🔧 **Modular Architecture** - Clean separation of commands, output handling, and business logic

### Development & Distribution
- 📦 **Lightweight Base Install** - Core dependencies only (5 packages vs 15+)
- 🛠️ **Optional Dependency Groups** - Separate `dev` and `docs` installs for development
- 🧪 **Comprehensive Testing** - 90+ tests including integration tests with real API
- ✅ **100% Quality Compliance** - Full ruff and mypy compliance with automated checks

## Quick Start

### Installation

**Basic Installation (Lightweight)**
```bash
pip install quake_cli
```

**With Optional Dependencies**
```bash
# For development
pip install quake_cli[dev]

# For documentation
pip install quake_cli[docs]

# Everything
pip install quake_cli[dev,docs]
```

## CLI Usage

### Basic Commands

```bash
# List recent earthquakes
quake list --limit 10

# Filter by magnitude
quake list --min-magnitude 4.0 --limit 5

# Get specific earthquake details
quake get 2024p123456

# Export to JSON
quake list --format json --output earthquakes.json

# Check API status
quake health

# Get earthquake statistics
quake stats
```

### Working with jq

The CLI outputs valid JSON by default for stats and when using `--format json`, making it perfect for use with `jq`:

```bash
# Get earthquake count by magnitude for the last 7 days
quake stats | jq '.magnitudeCount.days7'

# Find total earthquakes in the last 365 days
quake stats | jq '.magnitudeCount.days365 | map(.) | add'

# Get the largest earthquake magnitude from recent data
quake list --format json --limit 100 | jq '.features[].properties.magnitude | max'

# Count earthquakes above magnitude 4.0
quake list --format json --min-magnitude 4.0 | jq '.features | length'

# Extract earthquake locations and magnitudes
quake list --format json --limit 10 | jq '.features[] | {magnitude: .properties.magnitude, location: .properties.locality}'

# Get coordinates of recent large earthquakes
quake list --format json --min-magnitude 5.0 | jq '.features[] | {magnitude: .properties.magnitude, lat: .geometry.coordinates[1], lon: .geometry.coordinates[0]}'

# Daily earthquake rates for the last week
quake stats | jq '.rate.perDay | to_entries | sort_by(.key) | reverse | .[0:7] | map({date: .key, count: .value})'
```

### Advanced CLI Examples

```bash
# Export large earthquakes to CSV for analysis
quake list --min-magnitude 5.0 --format csv --output large_quakes.csv

# Monitor recent earthquake activity (JSON format for processing)
quake list --limit 5 --format json | jq '.features[] | "\(.properties.time): M\(.properties.magnitude) at \(.properties.locality)"'

# Get detailed earthquake information with coordinates
quake list --format json --limit 1 | jq '.features[0] | {id: .properties.publicID, magnitude: .properties.magnitude, depth: .properties.depth, location: .properties.locality, coordinates: .geometry.coordinates}'

# Check API health with verbose output
quake health --verbose
```

### CLI Commands Reference

```bash
# List earthquakes with options
quake list [--limit N] [--min-magnitude M] [--max-magnitude M]
          [--min-mmi I] [--max-mmi I] [--mmi I]
          [--format table|json|csv] [--output FILE] [--verbose]

# Get specific earthquake
quake get EARTHQUAKE_ID [--format table|json|csv] [--output FILE] [--verbose]

# Get earthquake history
quake history EARTHQUAKE_ID [--format table|json|csv] [--output FILE] [--verbose]

# Get earthquake statistics
quake stats [--format table|json|csv] [--output FILE] [--verbose]

# Check API health
quake health [--verbose]

# Show help
quake --help
quake COMMAND --help
```

## Python Library Usage

### Basic Library Usage

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def get_earthquakes():
    async with GeoNetClient() as client:
        # Get recent earthquakes
        result = await client.get_quakes(limit=5)

        match result:
            case Ok(response):
                for quake in response.features:
                    props = quake.properties
                    print(f"M{props.magnitude:.1f} at {props.locality}")
            case Err(error):
                print(f"Error: {error}")

asyncio.run(get_earthquakes())
```

### Advanced Library Usage

```python
import asyncio
from quake_cli.client import GeoNetClient
from quake_cli.models import QuakeStatsResponse
from logerr import Ok, Err

async def advanced_usage():
    async with GeoNetClient() as client:
        # Filter by magnitude
        result = await client.search_quakes(min_magnitude=4.0, limit=10)

        match result:
            case Ok(response):
                print(f"Found {response.count} large earthquakes")
                # Access modular data models
                for quake in response.features:
                    props = quake.properties
                    geom = quake.geometry
                    print(f"M{props.magnitude:.1f} at {geom.latitude:.3f}, {geom.longitude:.3f}")
            case Err(error):
                print(f"Error: {error}")

        # Get earthquake statistics with structured models
        stats_result = await client.get_quake_stats()
        match stats_result:
            case Ok(raw_data):
                stats = QuakeStatsResponse.model_validate(raw_data)
                print(f"Last 7 days: {sum(stats.magnitudeCount.days7.values())} earthquakes")
            case Err(error):
                print(f"Stats error: {error}")

asyncio.run(advanced_usage())
```

## Core API

### GeoNet Client

The `GeoNetClient` is the main interface for accessing earthquake data:

```python
from quake_cli.client import GeoNetClient

async with GeoNetClient() as client:
    # Get recent earthquakes
    result = await client.get_quakes(limit=20)

    # Search with filters
    result = await client.search_quakes(
        min_magnitude=3.0,
        max_magnitude=6.0,
        limit=50
    )

    # Get specific earthquake
    result = await client.get_quake("2024p123456")

    # Get earthquake statistics
    result = await client.get_quake_stats()

    # Get earthquake history
    result = await client.get_quake_history("2024p123456")

    # Check API health
    result = await client.health_check()
```

### Earthquake Data

Access earthquake properties and geometry:

```python
# Each earthquake has properties and geometry
for quake in response.features:
    props = quake.properties
    geom = quake.geometry

    print(f"Magnitude: {props.magnitude}")
    print(f"Location: {props.locality}")
    print(f"Depth: {props.depth} km")
    print(f"Coordinates: {geom.latitude}, {geom.longitude}")
    if props.MMI:
        print(f"MMI: {props.MMI}")
```

### Error Handling

The library uses Result types for safe error handling:

```python
from logerr import Ok, Err

result = await client.get_quake("invalid_id")
match result:
    case Ok(earthquake):
        print(f"Found: {earthquake.properties.locality}")
    case Err(error):
        print(f"Error: {error}")
```

## Installation Options

### Basic Installation (Lightweight)

The base installation includes only essential dependencies (5 packages):

```bash
pip install quake_cli
```

### Optional Dependencies

Install additional features as needed:

```bash
# Development tools (testing, linting, building)
pip install quake_cli[dev]

# Documentation tools (mkdocs, mkdocs-material)
pip install quake_cli[docs]

# Everything
pip install quake_cli[all]
```

### Development Installation

```bash
git clone https://github.com/jesserobertson/quake-cli.git
cd quake-cli
pixi install
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Documentation
- **[Full Documentation](https://jesserobertson.github.io/quake-cli)** - Comprehensive guides and API reference
- **[Installation Guide](docs/content/installation.md)** - Detailed installation instructions
- **[Quick Start](docs/content/quickstart.md)** - Get up and running quickly
- **[Live Examples](docs/content/examples.md)** - Automatically tested code examples
- **[API Reference](docs/content/api/)** - Complete API documentation with docstring examples

### Tested Documentation Examples

All code examples in our documentation are automatically tested to ensure they remain functional and accurate.

## Requirements

- **Python 3.12+**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## GeoNet API

This tool queries earthquake data from [GeoNet](https://www.geonet.org.nz/), New Zealand's geological hazard information system. GeoNet provides real-time earthquake monitoring and data for New Zealand and surrounding areas.

**Data Attribution**: Earthquake data provided by GeoNet (https://www.geonet.org.nz/)

## Support

- **Documentation**: https://jesserobertson.github.io/quake-cli
- **API Examples**: https://jesserobertson.github.io/quake-cli/examples/
- **Issues**: https://github.com/jesserobertson/quake-cli/issues
- **Discussions**: https://github.com/jesserobertson/quake-cli/discussions
- **GeoNet API**: https://www.geonet.org.nz/data/supplementary/webapi

## Acknowledgments

- **Data Source**: [GeoNet](https://www.geonet.org.nz/) - New Zealand's geological hazard monitoring system
- Async HTTP client using [httpx](https://www.python-httpx.org/)
- Type safety with [Pydantic](https://docs.pydantic.dev/) models
- Tested with [pytest](https://pytest.org)

---

Made with ❤️ by [Jess Robertson](https://github.com/jesserobertson)
# quake-cli

[![CI](https://github.com/jesserobertson/quake-cli/workflows/CI/badge.svg)](https://github.com/jesserobertson/quake-cli/actions)
[![codecov](https://codecov.io/gh/jesserobertson/quake-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/jesserobertson/quake-cli)
[![PyPI version](https://badge.fury.io/py/quake_cli.svg)](https://badge.fury.io/py/quake_cli)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jesserobertson.github.io/quake-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern Python library for querying earthquake data from the GeoNet API

## Features

- 🌍 **GeoNet API Integration** - Query real-time earthquake data from New Zealand's GeoNet service
- ⚡ **Async Performance** - Fast async HTTP client with automatic retries and error handling
- 🔍 **Flexible Filtering** - Filter earthquakes by magnitude, MMI, location, and time
- 📊 **Type-Safe Data Models** - Pydantic models for reliable earthquake data structures
- 🔄 **Result-Based Error Handling** - Functional error handling with composable Result types
- 🚀 **Modern Python 3.12+** - Uses latest Python features with comprehensive type hints
- 📖 **Tested Examples** - All documentation examples are automatically tested for accuracy

## Quick Start

### Installation

```bash
pip install quake_cli
```

### Basic Usage

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

### Filtering and Search

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def filter_earthquakes():
    async with GeoNetClient() as client:
        # Filter by magnitude
        result = await client.search_quakes(min_magnitude=4.0, limit=10)

        match result:
            case Ok(response):
                print(f"Found {response.count} large earthquakes")
            case Err(error):
                print(f"Error: {error}")

        # Get earthquakes by MMI intensity
        result = await client.get_quakes(mmi=4)
        # Process result...

asyncio.run(filter_earthquakes())
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

### Basic Installation

```bash
pip install quake_cli
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
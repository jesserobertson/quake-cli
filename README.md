# quake-cli

[![CI](https://github.com/jesserobertson/quake-cli/workflows/CI/badge.svg)](https://github.com/jesserobertson/quake-cli/actions)
[![codecov](https://codecov.io/gh/jesserobertson/quake-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/jesserobertson/quake-cli)
[![PyPI version](https://badge.fury.io/py/quake_cli.svg)](https://badge.fury.io/py/quake_cli)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jesserobertson.github.io/quake-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern Python CLI for querying earthquake data from the GeoNet API

## Features

- 🌍 **GeoNet API Integration** - Query real-time earthquake data from New Zealand's GeoNet service
- 🖥️ **Rich CLI Interface** - Beautiful command-line interface with progress indicators and formatted output
- 📊 **Multiple Output Formats** - Export data as JSON, CSV, or formatted tables
- ⚡ **Async Performance** - Fast async HTTP client for efficient API calls
- 🔍 **Flexible Filtering** - Filter earthquakes by magnitude, MMI, and other criteria
- 🚀 **Modern Python 3.12+** with comprehensive type hints
- 📦 **Unified Development Experience** with pixi task management
- 🧪 **Comprehensive Testing** with pytest
- 🔍 **Code Quality Enforcement** with ruff and mypy (100% compliance)
- 📚 **Beautiful Documentation** with MkDocs Material
- 🔒 **Security Scanning** and dependency management
- 🤖 **Automated CI/CD** with GitHub Actions

## Quick Start

### Installation

```bash
pip install quake_cli
```

### CLI Usage

```bash
# List recent earthquakes
quake list

# Get earthquakes with magnitude >= 4.0
quake list --min-magnitude 4.0

# Get a specific earthquake by ID
quake get 2024p123456

# Export to JSON
quake list --format json --output earthquakes.json

# Check API health
quake health
```

### Python API Usage

```python
import asyncio
from quake_cli import GeoNetClient

async def main():
    async with GeoNetClient() as client:
        # Get recent earthquakes
        response = await client.get_quakes(limit=10)
        print(f"Found {response.count} earthquakes")

        # Get specific earthquake
        quake = await client.get_quake("2024p123456")
        print(f"Magnitude: {quake.properties.magnitude}")

asyncio.run(main())
```

## Python API

### Core Classes

#### GeoNetClient

Async HTTP client for the GeoNet API:

```python
from quake_cli import GeoNetClient, GeoNetError

async with GeoNetClient() as client:
    # List earthquakes with optional filtering
    response = await client.get_quakes(limit=50, mmi=4)

    # Search with magnitude/MMI filters
    response = await client.search_quakes(
        min_magnitude=3.0,
        max_magnitude=6.0,
        limit=100
    )

    # Get specific earthquake details
    earthquake = await client.get_quake("2024p123456")

    # Get earthquake location history
    history = await client.get_quake_history("2024p123456")

    # Get earthquake statistics
    stats = await client.get_quake_stats()

    # Health check
    is_healthy = await client.health_check()
```

#### Data Models

Type-safe Pydantic models for earthquake data:

```python
from quake_cli import QuakeResponse, QuakeFeature

# QuakeResponse contains multiple earthquake features
response: QuakeResponse = await client.get_quakes()
for feature in response.features:
    props = feature.properties
    geom = feature.geometry

    print(f"ID: {props.publicID}")
    print(f"Magnitude: {props.magnitude}")
    print(f"Depth: {props.depth} km")
    print(f"Location: {props.locality}")
    print(f"Coordinates: {geom.latitude}, {geom.longitude}")
```

### Error Handling

```python
from quake_cli import GeoNetClient, GeoNetError

try:
    async with GeoNetClient() as client:
        earthquake = await client.get_quake("invalid_id")
except GeoNetError as e:
    print(f"API error: {e}")
```

## Installation Options

### Basic Installation

```bash
pip install quake_cli
```

### Development Installation

For contributors and developers:

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Clone and set up the project
git clone https://github.com/jesserobertson/quake-cli.git
cd quake-cli

# Install dependencies and set up development environment
pixi install
pixi run dev setup

# Run tests to verify installation
pixi run test unit
```

## Development

This project uses modern Python development practices with comprehensive tooling:

### CLI Commands

```bash
# List earthquakes with filtering options
quake list [OPTIONS]
  --limit, -l INTEGER             Maximum number of earthquakes [default: 10]
  --min-magnitude FLOAT           Minimum magnitude filter
  --max-magnitude FLOAT           Maximum magnitude filter
  --min-mmi INTEGER              Minimum Modified Mercalli Intensity
  --max-mmi INTEGER              Maximum Modified Mercalli Intensity
  --mmi INTEGER                  Specific MMI (-1 to 8, server-side filter)
  --format, -f [table|json|csv]  Output format [default: table]
  --output, -o PATH              Output file path

# Get specific earthquake details
quake get EARTHQUAKE_ID [OPTIONS]
  --format, -f [table|json|csv]  Output format [default: table]
  --output, -o PATH              Output file path

# Get earthquake location history
quake history EARTHQUAKE_ID [OPTIONS]
  --format, -f [table|json|csv]  Output format [default: table]
  --output, -o PATH              Output file path

# Get earthquake statistics
quake stats [OPTIONS]
  --format, -f [table|json|csv]  Output format [default: table]
  --output, -o PATH              Output file path

# Check GeoNet API health
quake health

# Show version
quake --version
```

### Development Commands

```bash
# Testing
pixi run test unit                 # Run unit tests

# Code Quality
pixi run quality check             # Run all quality checks
pixi run quality fix               # Auto-fix issues

# Documentation
pixi run docs serve                # Serve docs locally
pixi run docs build                # Build documentation

# Build & Distribution
pixi run build package             # Build package
pixi run build check               # Check package

# Development Environment
pixi run dev setup                 # Set up dev environment
pixi run dev status                # Show environment status
```

### Code Quality Standards

This project maintains **100% ruff compliance** and comprehensive type coverage:

- **Formatting**: Automated with ruff
- **Linting**: Strict ruff configuration with modern Python rules
- **Type Checking**: Full mypy coverage with strict settings
- **Testing**: Comprehensive test suite with coverage reporting

### Contributing

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/quake-cli.git
   cd quake-cli
   ```
3. **Set up development environment**:
   ```bash
   pixi install
   pixi run dev setup
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
5. **Make your changes** and ensure all tests pass:
   ```bash
   pixi run check-all
   ```
6. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Create a Pull Request** on GitHub

## Documentation
- **[Full Documentation](https://jesserobertson.github.io/quake-cli)** - Comprehensive guides and API reference
- **[Installation Guide](docs/content/installation.md)** - Detailed installation instructions
- **[Quick Start](docs/content/quickstart.md)** - Get up and running quickly
- **[API Reference](docs/content/api/)** - Complete API documentation

### Building Documentation Locally

```bash
# Serve documentation with live reload
pixi run docs serve

# Build static documentation
pixi run docs build
```

## Requirements

- **Python 3.12+**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## GeoNet API

This tool queries earthquake data from [GeoNet](https://www.geonet.org.nz/), New Zealand's geological hazard information system. GeoNet provides real-time earthquake monitoring and data for New Zealand and surrounding areas.

**Data Attribution**: Earthquake data provided by GeoNet (https://www.geonet.org.nz/)

## Support

- **Documentation**: https://jesserobertson.github.io/quake-cli
- **Issues**: https://github.com/jesserobertson/quake-cli/issues
- **Discussions**: https://github.com/jesserobertson/quake-cli/discussions
- **GeoNet API**: https://www.geonet.org.nz/data/supplementary/webapi

## Acknowledgments

- **Data Source**: [GeoNet](https://www.geonet.org.nz/) - New Zealand's geological hazard monitoring system
- Built with [pixi](https://pixi.sh) for modern Python dependency management
- CLI powered by [Typer](https://typer.tiangolo.com/) with [Rich](https://rich.readthedocs.io/) formatting
- Async HTTP client using [httpx](https://www.python-httpx.org/)
- Type safety with [Pydantic](https://docs.pydantic.dev/) models
- Tested with [pytest](https://pytest.org)
- Documentation powered by [MkDocs](https://mkdocs.org) with [Material theme](https://squidfunk.github.io/mkdocs-material/)
- Code quality enforced by [ruff](https://docs.astral.sh/ruff/) and [mypy](https://mypy.readthedocs.io)

---

Made with ❤️ by [Jess Robertson](https://github.com/jesserobertson)
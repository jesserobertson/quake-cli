# quake-cli

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
- 🧪 **Comprehensive Testing** - 50+ tests including mock-based integration tests for offline testing
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
pip install quake_cli[all]
```

### CLI Usage

```bash
# List recent earthquakes
quake list --limit 10

# Filter by magnitude
quake list --min-magnitude 4.0 --limit 5

# Export to JSON
quake list --format json --output earthquakes.json

# Get earthquake statistics
quake stats --format json

# Check API health
quake health
```

### Library Usage

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

**Example Output:**
```
M5.2 at 20 km north-east of Seddon
M4.8 at 15 km south of Kaikoura
M3.9 at 25 km west of Wellington
M4.1 at 10 km east of Christchurch
M3.7 at 30 km north of Dunedin
```

### Filtering and Search

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def filter_earthquakes():
    async with GeoNetClient() as client:
        # Filter by magnitude
        result = await client.search_quakes(min_magnitude=4.0, limit=3)

        match result:
            case Ok(response):
                print(f"Found {response.count} large earthquakes")
                for quake in response.features:
                    props = quake.properties
                    print(f"M{props.magnitude:.1f} - {props.locality}")
            case Err(error):
                print(f"Error: {error}")

asyncio.run(filter_earthquakes())
```

**Example Output:**
```
Found 15 large earthquakes
M5.2 - 20 km north-east of Seddon
M4.8 - 15 km south of Kaikoura
M4.1 - 10 km east of Christchurch
```

## Next Steps

- **[Quick Start Guide](quickstart.md)** - Get up and running in minutes
- **[API Reference](api/index.md)** - Complete documentation with examples
- **[Data Models](api/models.md)** - Understanding earthquake data structures
- **[Testing Documentation](testing.md)** - Mock generation and integration testing workflow

## GeoNet API

This tool queries earthquake data from [GeoNet](https://www.geonet.org.nz/), New Zealand's geological hazard information system. GeoNet provides real-time earthquake monitoring and data for New Zealand and surrounding areas.

**Data Attribution**: Earthquake data provided by GeoNet (https://www.geonet.org.nz/)

## Support

- **GitHub Repository**: [jesserobertson/quake-cli](https://github.com/jesserobertson/quake-cli)
- **Issues**: [GitHub Issues](https://github.com/jesserobertson/quake-cli/issues)
- **PyPI Package**: [quake_cli](https://pypi.org/project/quake_cli)

## License

This project is licensed under the MIT License.
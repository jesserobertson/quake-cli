# Quick Start

Get up and running with the quake-cli Python library in minutes. This guide focuses on using quake-cli as a library in your Python applications.

## Installation

```bash
pip install quake_cli
```

## Your First Earthquake Query

Let's start with a simple example to fetch recent earthquakes:

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def get_recent_earthquakes():
    """Fetch and display recent earthquakes."""
    async with GeoNetClient() as client:
        # Get recent earthquakes
        result = await client.get_quakes(limit=5)

        match result:
            case Ok(response):
                print(f"Found {response.count} earthquakes:")
                for quake in response.features:
                    props = quake.properties
                    print(f"  • M{props.magnitude:.1f} at {props.locality}")
                    print(f"    Time: {props.time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"    Depth: {props.depth:.1f} km")
                    print()
            case Err(error):
                print(f"Error fetching earthquakes: {error}")

# Run the example
asyncio.run(get_recent_earthquakes())
```

## Working with Earthquake Data

The library provides rich Pydantic models for type-safe earthquake data:

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def explore_earthquake_data():
    """Explore the structure of earthquake data."""
    async with GeoNetClient() as client:
        result = await client.get_quakes(limit=1)

        match result:
            case Ok(response):
                if not response.is_empty:
                    quake = response.features[0]

                    # Access earthquake properties
                    props = quake.properties
                    print(f"Earthquake ID: {props.publicID}")
                    print(f"Magnitude: {props.magnitude}")
                    print(f"Depth: {props.depth} km")
                    print(f"Location: {props.locality}")
                    print(f"Quality: {props.quality}")
                    if props.MMI:
                        print(f"MMI: {props.MMI}")

                    # Access geometry data
                    geom = quake.geometry
                    print(f"Coordinates: {geom.latitude:.4f}, {geom.longitude:.4f}")
                    if geom.depth:
                        print(f"Geometry depth: {geom.depth} km")

            case Err(error):
                print(f"Error: {error}")

asyncio.run(explore_earthquake_data())
```

## Filtering Earthquakes

Filter earthquakes by magnitude, MMI, or other criteria:

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def filter_earthquakes():
    """Filter earthquakes by various criteria."""
    async with GeoNetClient() as client:
        # Server-side MMI filtering
        print("=== Significant earthquakes (MMI >= 4) ===")
        result = await client.get_quakes(mmi=4, limit=3)

        match result:
            case Ok(response):
                for quake in response.features:
                    props = quake.properties
                    print(f"M{props.magnitude:.1f} - {props.locality} (MMI: {props.MMI})")
            case Err(error):
                print(f"Error: {error}")

        # Client-side magnitude filtering
        print("\n=== Large earthquakes (magnitude >= 5.0) ===")
        result = await client.search_quakes(min_magnitude=5.0, limit=3)

        match result:
            case Ok(response):
                for quake in response.features:
                    props = quake.properties
                    print(f"M{props.magnitude:.1f} - {props.locality}")
            case Err(error):
                print(f"Error: {error}")

asyncio.run(filter_earthquakes())
```

## Getting Specific Earthquake Details

Retrieve detailed information about a specific earthquake:

```python
import asyncio
from quake_cli.client import GeoNetClient
from logerr import Ok, Err

async def get_earthquake_details():
    """Get details for a specific earthquake."""
    async with GeoNetClient() as client:
        # First, get a recent earthquake ID
        recent_result = await client.get_quakes(limit=1)

        match recent_result:
            case Ok(response):
                if not response.is_empty:
                    earthquake_id = response.features[0].properties.publicID
                    print(f"Getting details for earthquake: {earthquake_id}")

                    # Get detailed information
                    detail_result = await client.get_quake(earthquake_id)

                    match detail_result:
                        case Ok(quake):
                            props = quake.properties
                            print(f"Detailed info:")
                            print(f"  Time: {props.time}")
                            print(f"  Magnitude: {props.magnitude}")
                            print(f"  Location: {props.locality}")
                            print(f"  Coordinates: {quake.geometry.latitude:.4f}, {quake.geometry.longitude:.4f}")
                        case Err(error):
                            print(f"Error getting details: {error}")
                else:
                    print("No recent earthquakes found")
            case Err(error):
                print(f"Error: {error}")

asyncio.run(get_earthquake_details())
```

## Error Handling Patterns

The library uses Result types for robust error handling:

```python
import asyncio
from quake_cli.client import GeoNetClient, GeoNetError
from logerr import Ok, Err

async def error_handling_examples():
    """Demonstrate different error handling patterns."""

    # Pattern 1: Using match statements (recommended)
    async with GeoNetClient() as client:
        result = await client.get_quake("invalid-id")

        match result:
            case Ok(quake):
                print(f"Found earthquake: {quake.properties.locality}")
            case Err(error):
                print(f"Expected error for invalid ID: {error}")

    # Pattern 2: Using Result methods
    async with GeoNetClient() as client:
        result = await client.get_quakes(limit=1)

        if result.is_ok():
            response = result.unwrap()
            print(f"Success: {response.count} earthquakes")
        else:
            error = result.unwrap_err()
            print(f"Error: {error}")

    # Pattern 3: Chaining operations functionally
    async with GeoNetClient() as client:
        result = await client.get_quakes(limit=10)

        # Chain operations with .then()
        large_quakes = result.then(lambda response:
            Ok(response.filter_by_magnitude(min_mag=4.0))
        )

        match large_quakes:
            case Ok(filtered):
                print(f"Found {len(filtered)} large earthquakes")
            case Err(error):
                print(f"Error: {error}")

asyncio.run(error_handling_examples())
```

## Configuration Options

Customize the client for your needs:

```python
import asyncio
from quake_cli.client import GeoNetClient

async def custom_configuration():
    """Example of custom client configuration."""

    # Custom timeout and retry settings
    custom_client = GeoNetClient(
        timeout=60.0,           # 60 second timeout
        retries=5,              # 5 retry attempts
        retry_min_wait=2.0,     # Minimum 2s between retries
        retry_max_wait=30.0     # Maximum 30s between retries
    )

    async with custom_client as client:
        # Use the custom-configured client
        result = await client.health_check()

        match result:
            case Ok(healthy):
                print("API is healthy!" if healthy else "API has issues")
            case Err(error):
                print(f"Health check failed: {error}")

asyncio.run(custom_configuration())
```

## Next Steps

Now that you've got the basics:

1. **[Explore Examples](examples.md)** - See more comprehensive, tested examples
2. **[API Reference](api/index.md)** - Detailed documentation of all classes and methods
3. **[Data Models](api/models.md)** - Understanding the earthquake data structures
4. **[HTTP Client](api/client.md)** - Complete client documentation with all methods


## Getting Help

- **Issues**: [GitHub Issues](https://github.com/jesserobertson/quake-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jesserobertson/quake-cli/discussions)
- **Documentation**: You're reading it! All examples are tested automatically.

Ready to build amazing earthquake monitoring applications! 🌍✨
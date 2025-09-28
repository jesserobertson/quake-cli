# HTTP Client

The GeoNet API client provides async HTTP operations with comprehensive error handling, retry logic, and Result-based return types.

## Main Client

::: quake_cli.client.GeoNetClient
    options:
      members:
        - get_quakes
        - get_quake
        - get_quake_history
        - get_quake_stats
        - search_quakes
        - health_check

## Exception Classes

::: quake_cli.client.GeoNetError

::: quake_cli.client.GeoNetConnectionError

::: quake_cli.client.GeoNetTimeoutError

## Type Aliases

The client module exports several Result type aliases for type safety:

::: quake_cli.client.QuakeResult
::: quake_cli.client.FeatureResult
::: quake_cli.client.DataResult
::: quake_cli.client.StatsResult
::: quake_cli.client.HistoryResult

## Usage Examples

### Basic Usage

```python
import asyncio
from quake_cli.client import GeoNetClient

async def example():
    async with GeoNetClient() as client:
        # Get recent earthquakes
        result = await client.get_quakes(limit=10)

        match result:
            case Ok(response):
                print(f"Found {response.count} earthquakes")
            case Err(error):
                print(f"Error: {error}")

asyncio.run(example())
```

### Custom Configuration

```python
# Configure client with custom settings
client = GeoNetClient(
    base_url="https://api.geonet.org.nz/",
    timeout=60.0,
    retries=5,
    retry_min_wait=2.0,
    retry_max_wait=30.0
)
```

### Error Handling

The client uses functional error handling with Result types:

```python
async def handle_errors():
    async with GeoNetClient() as client:
        result = await client.get_quake("invalid-id")

        # Pattern matching for clean error handling
        match result:
            case Ok(quake):
                print(f"Quake: {quake.properties.locality}")
            case Err(error):
                print(f"Failed to get quake: {error}")

        # Or use the Result API
        if result.is_ok():
            quake = result.unwrap()
            print(f"Success: {quake.properties.magnitude}")
        else:
            print(f"Error: {result.unwrap_err()}")
```
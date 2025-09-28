# API Reference

This section provides comprehensive documentation for all public APIs in quake-cli, including detailed examples that are automatically tested as part of our test suite.

## Core Components

- **[Models](models.md)** - Pydantic data models for earthquake data
- **[Client](client.md)** - Async HTTP client for GeoNet API
- **[CLI](cli.md)** - Command-line interface utilities
- **[Result Types](result.md)** - Functional error handling utilities

## Features

- **Comprehensive Examples**: All code examples in the documentation are automatically tested
- **Type Safety**: Full mypy compatibility with modern Python typing
- **Async Support**: Complete async/await support throughout the API
- **Functional Error Handling**: Uses Result types for composable error handling

## Quick Example

Here's a quick example of using the async client:

```python
import asyncio
from quake_cli.client import GeoNetClient

async def get_recent_quakes():
    async with GeoNetClient() as client:
        result = await client.get_quakes(limit=5)
        match result:
            case Ok(response):
                print(f"Found {response.count} earthquakes")
                for quake in response.features:
                    props = quake.properties
                    print(f"  {props.publicID}: M{props.magnitude} at {props.locality}")
            case Err(error):
                print(f"Error: {error}")

# Run the example
asyncio.run(get_recent_quakes())
```

All examples in this documentation are live code that gets tested automatically to ensure they remain current and functional.
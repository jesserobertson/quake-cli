# Result Types

The result module provides functional error handling utilities using the `logerr` library's Result types.

## Error Handling Functions

::: quake_cli.result.handle_api_error

## Type Aliases

The module exports several type aliases for common Result patterns:

::: quake_cli.result.QuakeResult
::: quake_cli.result.FeatureResult
::: quake_cli.result.DataResult

## Functional Error Handling

The quake-cli package uses Result types throughout for composable, functional error handling:

```python
from quake_cli.result import handle_api_error

# Convert exceptions to Result types
try:
    # Some operation that might fail
    data = risky_operation()
except Exception as e:
    result = handle_api_error(e)
    # result is now a Result[T, str] that can be chained
```

## Benefits

- **Composable**: Chain operations without nested try/catch blocks
- **Type Safe**: Errors are part of the type signature
- **Functional**: Use map, then, and other combinators
- **Explicit**: Errors must be handled or explicitly ignored

## Integration with Client

All client methods return Result types:

```python
from quake_cli.client import GeoNetClient

async def example():
    async with GeoNetClient() as client:
        # Returns QuakeResult = Result[QuakeResponse, str]
        result = await client.get_quakes()

        # Chain operations functionally
        processed = result.then(lambda response:
            Ok(response.filter_by_magnitude(min_mag=4.0))
        ).then(lambda filtered:
            Ok(f"Found {len(filtered)} large earthquakes")
        )

        # Handle final result
        match processed:
            case Ok(message):
                print(message)
            case Err(error):
                print(f"Error: {error}")
```
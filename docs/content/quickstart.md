# Quick Start

Get up and running with quake-cli in minutes.

## Installation

```bash
pip install quake_cli
```

## Basic Usage

Here's a simple example to get you started:

```python
import quake_cli

# Basic example
def main():
    print("Hello from quake-cli!")

if __name__ == "__main__":
    main()
```

## Async Usage

quake-cli supports both synchronous and asynchronous operations:

```python
import asyncio
import quake_cli

async def async_example():
    """Example of asynchronous usage."""
    print("Async hello from quake-cli!")

async def main():
    await async_example()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

quake-cli can be configured through environment variables or direct parameters:

```python
import os
import quake_cli

# Environment-based configuration

# Use configuration in your application
def configured_example():
    # Your configured code here
    pass
```

## Error Handling

quake-cli uses modern Python error handling patterns:

```python
import quake_cli

def error_handling_example():
    try:
        # Your code that might raise exceptions
        pass
    except quake_cli.Quake_CliError as e:
        print(f"quake-cli error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    error_handling_example()
```

## Next Steps

Now that you have the basics working:

1. **Read the [User Guide](concepts.md)** - Learn about core concepts and advanced features
2. **Check out [Examples](examples.md)** - See more comprehensive examples
3. **Browse the [API Reference](api/index.md)** - Detailed documentation of all functions and classes

## Getting Help

- **Documentation**: Continue reading the documentation for detailed guides
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/jesserobertson/quake-cli/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/jesserobertson/quake-cli/discussions)

Happy coding with quake-cli! 🚀
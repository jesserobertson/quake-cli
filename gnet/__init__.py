"""
gnet - Comprehensive GeoNet API client for earthquakes, volcanoes, and geohazard monitoring

gnet is a modern Python 3.12+ library that provides complete access to New Zealand's
GeoNet API, featuring functional error handling with Result types, async operations,
and beautiful CLI tools.

Example:
    Basic earthquake data:

    ```python
    import asyncio
    from gnet import GeoNetClient

    async def main():
        async with GeoNetClient() as client:
            result = await client.get_quakes(limit=10)
            match result:
                case Ok(quakes):
                    print(f"Found {len(quakes.features)} earthquakes")
                case Err(error):
                    print(f"Error: {error}")

    asyncio.run(main())
    ```

    Volcano monitoring:

    ```python
    import asyncio
    from gnet import GeoNetClient

    async def main():
        async with GeoNetClient() as client:
            result = await client.get_volcano_alerts()
            match result:
                case Ok(alerts):
                    print(f"Monitoring {len(alerts.features)} volcanoes")
                case Err(error):
                    print(f"Error: {error}")

    asyncio.run(main())
    ```
"""

__version__ = "0.1.0"
__author__ = "Jess Robertson"
__email__ = "jess.robertson@niwa.co.nz"

# Define public API
__all__ = [
    "__author__",
    "__email__",
    "__version__",
]


class GNetError(Exception):
    """Base exception class for gnet."""

    pass


class GNetConfigError(GNetError):
    """Raised when there's a configuration error."""

    pass


# Add exception classes to public API
__all__.extend(
    [
        "GNetConfigError",
        "GNetError",
    ]
)


# Add exported classes to __all__ (they will be imported later if needed)
__all__.extend(
    [
        "GeoNetClient",
        "GeoNetError",
    ]
)

# Import main functionality (exclude CLI to avoid circular imports)
from .client import GeoNetClient, GeoNetError  # noqa: E402, F401


# Lazy imports for optional dependencies
def _get_version() -> str:
    """Get the package version."""
    return __version__


# Package initialization
def _initialize_package() -> None:
    """Initialize the gnet package with any necessary setup."""
    # TODO: Add any package initialization logic here
    pass


# Initialize the package when imported
_initialize_package()

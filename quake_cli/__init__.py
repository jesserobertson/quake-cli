"""
quake-cli - Pull data from GeoNet API

quake-cli is a modern Python 3.12+ library that follows
best practices for code quality, testing, and maintainability.

Example:
    Basic usage example:

    ```python
    import quake_cli

    # Your code here
    ```

    Async usage example:

    ```python
    import asyncio
    import quake_cli

    async def main():
        # Your async code here
        pass

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


class QuakeCliError(Exception):
    """Base exception class for quake-cli."""

    pass


class QuakeCliConfigError(QuakeCliError):
    """Raised when there's a configuration error."""

    pass


# Add exception classes to public API
__all__.extend(
    [
        "QuakeCliConfigError",
        "QuakeCliError",
    ]
)


# Add exported classes to __all__ (they will be imported later if needed)
__all__.extend(
    [
        "GeoNetClient",
        "GeoNetError",
        "QuakeFeature",
        "QuakeResponse",
    ]
)

# Import main functionality (exclude CLI to avoid circular imports)
from .client import GeoNetClient, GeoNetError  # noqa: E402, F401
from .models import QuakeFeature, QuakeResponse  # noqa: E402, F401


# Lazy imports for optional dependencies
def _get_version() -> str:
    """Get the package version."""
    return __version__


# Package initialization
def _initialize_package() -> None:
    """Initialize the package with any necessary setup."""
    # TODO: Add any package initialization logic here
    pass


# Initialize the package when imported
_initialize_package()

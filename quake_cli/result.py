"""
Result type wrapper for GeoNet API operations using logerr.

This module provides Result-based error handling for API operations,
making errors explicit and composable.
"""

from typing import TypeVar

from logerr import Err, Result
from loguru import logger

from quake_cli.models import QuakeFeature, QuakeResponse

# Type aliases for common Result types
T = TypeVar("T")
QuakeResult = Result[QuakeResponse, str]
FeatureResult = Result[QuakeFeature, str]
DataResult = Result[dict, str]


def handle_api_error(error: Exception) -> Result[T, str]:
    """
    Convert exceptions to Result types with automatic logging.

    Args:
        error: The exception to handle

    Returns:
        An err Result with error message

    Examples:
        >>> error = ValueError("Invalid input")
        >>> result = handle_api_error(error)
        >>> result.is_err()
        True
        >>> result.unwrap_err()
        'Invalid input'
    """
    error_msg = str(error)
    logger.error(f"API error occurred: {error_msg}")
    return Err(error_msg)


# Note: validate_response function removed as it was unused and redundant
# The type system provides sufficient validation for our use cases

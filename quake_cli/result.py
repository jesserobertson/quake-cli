"""
Result type wrapper for GeoNet API operations using logerr.

This module provides Result-based error handling for API operations,
making errors explicit and composable.
"""

from typing import TypeVar

from logerr import Err, Ok, Result
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
    """
    error_msg = str(error)
    logger.error(f"API error occurred: {error_msg}")
    return Err(error_msg)


def validate_response(data: dict) -> DataResult:
    """
    Validate API response data structure.

    Args:
        data: Raw API response data

    Returns:
        Result containing validated data or error message
    """
    if not isinstance(data, dict):
        return Err(f"Invalid response type: expected dict, got {type(data).__name__}")

    if "type" not in data:
        return Err("Missing required field 'type' in response")

    if data.get("type") != "FeatureCollection" and data.get("type") != "Feature":
        return Err(f"Invalid response type: {data.get('type')}")

    return Ok(data)

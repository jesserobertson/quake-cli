"""
Pydantic models for GeoNet API data structures.

This module defines the data models used to parse and validate responses
from the GeoNet API, following modern Python 3.12+ typing patterns.
"""

from .feature import QuakeFeature
from .geometry import QuakeGeometry
from .properties import QuakeProperties, QualityType
from .response import MagnitudeCounts, QuakeResponse, QuakeStatsResponse, RateData

# Export all models in the public API
__all__ = [
    "MagnitudeCounts",
    "QuakeFeature",
    "QuakeGeometry",
    "QuakeProperties",
    "QuakeResponse",
    "QuakeStatsResponse",
    "QualityType",
    "RateData",
]

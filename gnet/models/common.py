"""
Common/shared models for GeoNet data.

This module contains base types and shared models used across different data types.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Point(BaseModel):
    """GeoJSON Point geometry."""

    type: Literal["Point"] = "Point"
    coordinates: list[float]

    @property
    def longitude(self) -> float:
        """Get longitude coordinate."""
        return self.coordinates[0]

    @property
    def latitude(self) -> float:
        """Get latitude coordinate."""
        return self.coordinates[1]

    @property
    def elevation(self) -> float | None:
        """Get elevation coordinate if present."""
        return self.coordinates[2] if len(self.coordinates) > 2 else None


class Location(BaseModel):
    """Geographic location information."""

    longitude: float
    latitude: float
    elevation: float | None = None
    locality: str | None = None
    """Human-readable locality description."""

    @classmethod
    def from_point(cls, point: Point, locality: str | None = None) -> "Location":
        """Create Location from Point geometry."""
        return cls(
            longitude=point.longitude,
            latitude=point.latitude,
            elevation=point.elevation,
            locality=locality,
        )


class Magnitude(BaseModel):
    """Earthquake magnitude information."""

    value: float
    """Magnitude value."""

    type: str | None = None
    """Magnitude type (e.g., Mw, ML, etc.)."""

    uncertainty: float | None = None
    """Magnitude uncertainty."""


class Intensity(BaseModel):
    """Intensity/shaking information."""

    mmi: int | float
    """Modified Mercalli Intensity value."""

    count: int | None = None
    """Number of reports (for user-reported data)."""


class Quality(BaseModel):
    """Data quality information."""

    level: str
    """Quality level: 'best', 'preliminary', 'automatic', 'deleted'."""

    source: str | None = None
    """Data source or provider."""

    confidence: float | None = None
    """Confidence score (0.0 to 1.0)."""


class TimeInfo(BaseModel):
    """Temporal information."""

    origin: datetime
    """Origin time of the event."""

    created: datetime | None = None
    """Time when the record was created."""

    updated: datetime | None = None
    """Time when the record was last updated."""

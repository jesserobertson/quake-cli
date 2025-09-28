"""
Intensity models for GeoNet shaking data.

This module contains models for both reported and measured intensity data.
"""

from pydantic import BaseModel

from .common import Intensity, Location, Point


class Properties(BaseModel):
    """Intensity measurement properties."""

    intensity: Intensity
    location: Location

    @classmethod
    def from_legacy(
        cls,
        mmi: int | float,
        count: int | None,
        longitude: float,
        latitude: float,
    ) -> "Properties":
        """Create from legacy API format."""
        return cls(
            intensity=Intensity(mmi=mmi, count=count),
            location=Location(longitude=longitude, latitude=latitude),
        )


class Feature(BaseModel):
    """A single intensity measurement point."""

    type: str = "Feature"
    properties: Properties
    geometry: Point


class Response(BaseModel):
    """Response from the GeoNet intensity API."""

    type: str = "FeatureCollection"
    features: list[Feature]

    # Summary properties for reported intensity
    count_mmi: dict[str, int] | None = None
    """Total count of reports by MMI level."""
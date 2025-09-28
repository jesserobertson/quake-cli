"""
Earthquake models for GeoNet data.

This module contains all earthquake-related data models organized in a clean hierarchy.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from .common import Intensity, Location, Magnitude, Point, Quality, TimeInfo


class Properties(BaseModel):
    """Core earthquake properties."""

    publicID: str
    """Unique earthquake identifier."""

    time: TimeInfo
    magnitude: Magnitude
    location: Location
    quality: Quality
    intensity: Intensity | None = None

    @classmethod
    def from_legacy_api(
        cls,
        publicID: str,
        time: datetime,
        magnitude: float,
        depth: float,
        locality: str,
        MMI: int | None,
        quality: str,
        longitude: float,
        latitude: float,
    ) -> "Properties":
        """Create Properties from legacy API response format."""
        return cls(
            publicID=publicID,
            time=TimeInfo(origin=time),
            magnitude=Magnitude(value=magnitude),
            location=Location(
                longitude=longitude,
                latitude=latitude,
                elevation=-depth if depth > 0 else depth,  # Convert depth to elevation
                locality=locality,
            ),
            quality=Quality(level=quality),
            intensity=Intensity(mmi=MMI) if MMI is not None else None,
        )


class Feature(BaseModel):
    """A single earthquake feature in GeoJSON format."""

    type: str = "Feature"
    properties: Properties
    geometry: Point


class Response(BaseModel):
    """Response from the GeoNet earthquake API."""

    type: str = "FeatureCollection"
    features: list[Feature]

    @property
    def is_empty(self) -> bool:
        """Check if the response contains no earthquakes."""
        return len(self.features) == 0

    @property
    def count(self) -> int:
        """Total number of earthquakes in the response."""
        return len(self.features)

    def filter_by_magnitude(
        self, min_mag: float | None = None, max_mag: float | None = None
    ) -> list[Feature]:
        """Filter earthquakes by magnitude range."""
        filtered = self.features

        if min_mag is not None:
            filtered = [f for f in filtered if f.properties.magnitude.value >= min_mag]

        if max_mag is not None:
            filtered = [f for f in filtered if f.properties.magnitude.value <= max_mag]

        return filtered

    def filter_by_mmi(
        self, min_mmi: int | None = None, max_mmi: int | None = None
    ) -> list[Feature]:
        """Filter earthquakes by Modified Mercalli Intensity range."""
        filtered = []

        for feature in self.features:
            if feature.properties.intensity is None:
                continue

            mmi = feature.properties.intensity.mmi

            if min_mmi is not None and mmi < min_mmi:
                continue

            if max_mmi is not None and mmi > max_mmi:
                continue

            filtered.append(feature)

        return filtered


class Stats(BaseModel):
    """Earthquake statistics data."""

    magnitudeCount: dict[str, dict[str, int]]
    """Count of earthquakes by magnitude and time period."""

    rate: dict[str, dict[str, int]]
    """Earthquake rate data over time."""
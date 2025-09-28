"""
Volcano models for GeoNet data.

This module contains all volcano-related data models with earthquake submodels.
"""

from datetime import datetime

from pydantic import BaseModel

from .common import Location, Magnitude, Point, Quality, TimeInfo


class Alert(BaseModel):
    """Volcanic alert information."""

    level: int
    """Numeric alert level (0-5)."""

    color: str
    """Alert color code (green, yellow, orange, red)."""

    activity: str
    """Description of volcanic activity."""

    hazards: str | None = None
    """Description of potential hazards."""


class Properties(BaseModel):
    """Volcano properties."""

    id: str
    """Unique volcano identifier."""

    title: str
    """Human-readable volcano name."""

    location: Location
    alert: Alert

    @classmethod
    def from_legacy_api(
        cls,
        volcanoID: str,
        volcanoTitle: str,
        level: int,
        acc: str,
        activity: str,
        hazards: str,
        longitude: float,
        latitude: float,
    ) -> "Properties":
        """Create Properties from legacy API response format."""
        return cls(
            id=volcanoID,
            title=volcanoTitle,
            location=Location(longitude=longitude, latitude=latitude),
            alert=Alert(level=level, color=acc, activity=activity, hazards=hazards),
        )


class Feature(BaseModel):
    """A single volcano feature in GeoJSON format."""

    type: str = "Feature"
    properties: Properties
    geometry: Point


class Response(BaseModel):
    """Response from the GeoNet volcano alerts API."""

    type: str = "FeatureCollection"
    features: list[Feature]


# Volcano earthquake models (nested under volcano namespace)
class quake:
    """Earthquake models specific to volcano monitoring."""

    class Properties(BaseModel):
        """Properties for volcano-related earthquakes."""

        publicID: str
        """Unique earthquake identifier."""

        time: TimeInfo
        magnitude: Magnitude
        location: Location
        quality: Quality
        volcano_id: str | None = None
        """Associated volcano identifier."""

        @classmethod
        def from_legacy(
            cls,
            publicID: str,
            time: datetime,
            magnitude: float,
            depth: float,
            locality: str,
            quality: str,
            volcanoID: str | None,
            longitude: float,
            latitude: float,
        ) -> "quake.Properties":
            """Create from legacy API format."""
            return cls(
                publicID=publicID,
                time=TimeInfo(origin=time),
                magnitude=Magnitude(value=magnitude),
                location=Location(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=-depth if depth > 0 else depth,
                    locality=locality,
                ),
                quality=Quality(level=quality),
                volcano_id=volcanoID,
            )

    class Feature(BaseModel):
        """A volcano-related earthquake feature."""

        type: str = "Feature"
        properties: "quake.Properties"
        geometry: Point

    class Response(BaseModel):
        """Response from volcano earthquake API."""

        type: str = "FeatureCollection"
        features: list["quake.Feature"]
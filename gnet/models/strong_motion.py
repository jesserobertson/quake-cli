"""
Strong motion models for GeoNet API responses.

This module provides Pydantic models for parsing strong motion data from the GeoNet API,
including accelerometer measurements and station-based ground motion data.
"""

from typing import Any

from pydantic import BaseModel

from gnet.models.common import Point


class StationProperties(BaseModel):
    """Strong motion station properties."""

    station: str
    network: str
    location: str
    distance: float | None = None
    mmi: float | None = None
    pga_horizontal: float | None = None
    pga_vertical: float | None = None
    pgv_horizontal: float | None = None
    pgv_vertical: float | None = None

    @classmethod
    def from_legacy_api(
        cls,
        station: str,
        network: str,
        location: str,
        distance: float | None = None,
        mmi: float | None = None,
        pga_horizontal: float | None = None,
        pga_vertical: float | None = None,
        pgv_horizontal: float | None = None,
        pgv_vertical: float | None = None,
        **kwargs: Any,
    ) -> "StationProperties":
        """Create StationProperties from legacy API response."""
        return cls(
            station=station,
            network=network,
            location=location,
            distance=distance,
            mmi=mmi,
            pga_horizontal=pga_horizontal,
            pga_vertical=pga_vertical,
            pgv_horizontal=pgv_horizontal,
            pgv_vertical=pgv_vertical,
        )


class StationFeature(BaseModel):
    """A single strong motion station feature."""

    id: str
    type: str = "Feature"
    properties: StationProperties
    geometry: Point


class Metadata(BaseModel):
    """Strong motion response metadata."""

    author: str | None = None
    depth: float | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    magnitude: float | None = None
    version: str | None = None

    @classmethod
    def from_legacy_api(
        cls,
        author: str | None = None,
        depth: float | None = None,
        description: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        magnitude: float | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> "Metadata":
        """Create Metadata from legacy API response."""
        return cls(
            author=author,
            depth=depth,
            description=description,
            latitude=latitude,
            longitude=longitude,
            magnitude=magnitude,
            version=version,
        )


class Response(BaseModel):
    """Strong motion response containing station data."""

    type: str = "FeatureCollection"
    metadata: Metadata
    features: list[StationFeature]

    @property
    def count(self) -> int:
        """Total number of stations in the response."""
        return len(self.features)

    def get_stations_by_network(self, network: str) -> list[StationFeature]:
        """Filter stations by network."""
        return [f for f in self.features if f.properties.network.lower() == network.lower()]

    def get_high_intensity_stations(self, min_mmi: float = 4.0) -> list[StationFeature]:
        """Get stations with MMI above threshold."""
        return [
            f for f in self.features
            if f.properties.mmi is not None and f.properties.mmi >= min_mmi
        ]

    def get_stations_within_distance(self, max_distance: float) -> list[StationFeature]:
        """Get stations within distance of epicenter (km)."""
        return [
            f for f in self.features
            if f.properties.distance is not None and f.properties.distance <= max_distance
        ]

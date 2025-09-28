"""
Geometry models for earthquake location data.

This module defines GeoJSON geometry models for earthquake location information.
"""

from typing import Literal

from pydantic import BaseModel, Field


class QuakeGeometry(BaseModel):
    """Geometry information for a quake (GeoJSON Point)."""

    type: Literal["Point"] = Field(description="Geometry type, always 'Point'")
    coordinates: list[float] = Field(
        description="Coordinates as [longitude, latitude] or [longitude, latitude, depth]",
        min_length=2,
        max_length=3,
    )

    @property
    def longitude(self) -> float:
        """Longitude coordinate.

        Examples:
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
            >>> geom.longitude
            174.123
        """
        return self.coordinates[0]

    @property
    def latitude(self) -> float:
        """Latitude coordinate.

        Examples:
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
            >>> geom.latitude
            -41.456
        """
        return self.coordinates[1]

    @property
    def depth(self) -> float | None:
        """Depth coordinate if available (should match properties.depth).

        Examples:
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456, 5.2])
            >>> geom.depth
            5.2

            >>> geom_2d = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
            >>> geom_2d.depth is None
            True
        """
        return self.coordinates[2] if len(self.coordinates) > 2 else None

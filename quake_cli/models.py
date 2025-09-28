"""
Pydantic models for GeoNet API data structures.

This module defines the data models used to parse and validate responses
from the GeoNet API, following modern Python 3.12+ typing patterns.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator


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


type QualityType = Literal["best", "preliminary", "automatic", "deleted"]


class QuakeProperties(BaseModel):
    """Properties of a quake event."""

    publicID: str = Field(description="Unique quake identifier")
    time: datetime = Field(description="Origin time of the earthquake")
    depth: float = Field(description="Depth in kilometers", ge=0)
    magnitude: float = Field(description="Summary magnitude")
    locality: str = Field(description="Nearest locality description")
    MMI: int | None = Field(
        alias="mmi",
        description="Modified Mercalli Intensity (-1 to 12)",
        ge=-1,
        le=12,
        default=None,
    )
    quality: QualityType = Field(description="Data quality indicator")

    @field_validator("publicID")
    @classmethod
    def validate_public_id(cls, v: str) -> str:
        """Validate publicID format."""
        if not v.strip():
            raise ValueError("publicID cannot be empty")
        return v.strip()

    @field_validator("locality")
    @classmethod
    def validate_locality(cls, v: str) -> str:
        """Validate locality is not empty."""
        if not v.strip():
            raise ValueError("locality cannot be empty")
        return v.strip()


class QuakeFeature(BaseModel):
    """A single earthquake feature (GeoJSON Feature)."""

    type: Literal["Feature"] = Field(description="Feature type, always 'Feature'")
    properties: QuakeProperties = Field(description="Quake properties")
    geometry: QuakeGeometry = Field(description="Quake geometry")

    @field_validator("geometry")
    @classmethod
    def validate_geometry_depth_matches(
        cls, v: QuakeGeometry, info: ValidationInfo
    ) -> QuakeGeometry:
        """Ensure geometry depth matches properties depth if available."""
        if hasattr(info, "data") and "properties" in info.data and v.depth is not None:
            properties_depth = info.data["properties"].depth
            if (
                abs(v.depth - properties_depth) > 0.001
            ):  # Allow for floating point precision
                raise ValueError(
                    f"Geometry depth ({v.depth}) must match properties depth ({properties_depth})"
                )
        return v


class QuakeResponse(BaseModel):
    """Response from GeoNet quake API endpoints."""

    type: Literal["FeatureCollection"] = Field(
        description="Collection type, always 'FeatureCollection'"
    )
    features: list[QuakeFeature] = Field(
        description="List of earthquake features", default_factory=list
    )

    @property
    def count(self) -> int:
        """Number of quakes in the response.

        Examples:
            >>> response = QuakeResponse(type="FeatureCollection", features=[])
            >>> response.count
            0

            >>> from datetime import datetime
            >>> props = QuakeProperties(
            ...     publicID="2023geonet001",
            ...     time=datetime(2023, 1, 1, 12, 0, 0),
            ...     depth=5.0,
            ...     magnitude=4.5,
            ...     locality="Wellington",
            ...     quality="best"
            ... )
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
            >>> feature = QuakeFeature(type="Feature", properties=props, geometry=geom)
            >>> response_with_data = QuakeResponse(type="FeatureCollection", features=[feature])
            >>> response_with_data.count
            1
        """
        return len(self.features)

    @property
    def is_empty(self) -> bool:
        """Whether the response contains no quakes.

        Examples:
            >>> response = QuakeResponse(type="FeatureCollection", features=[])
            >>> response.is_empty
            True

            >>> from datetime import datetime
            >>> props = QuakeProperties(
            ...     publicID="2023geonet001",
            ...     time=datetime(2023, 1, 1, 12, 0, 0),
            ...     depth=5.0,
            ...     magnitude=4.5,
            ...     locality="Wellington",
            ...     quality="best"
            ... )
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
            >>> feature = QuakeFeature(type="Feature", properties=props, geometry=geom)
            >>> response_with_data = QuakeResponse(type="FeatureCollection", features=[feature])
            >>> response_with_data.is_empty
            False
        """
        return len(self.features) == 0

    def get_by_id(self, public_id: str) -> QuakeFeature | None:
        """Get a quake by its publicID.

        Args:
            public_id: The unique earthquake identifier to search for

        Returns:
            The matching QuakeFeature or None if not found

        Examples:
            >>> from datetime import datetime
            >>> props = QuakeProperties(
            ...     publicID="2023geonet001",
            ...     time=datetime(2023, 1, 1, 12, 0, 0),
            ...     depth=5.0,
            ...     magnitude=4.5,
            ...     locality="Wellington",
            ...     quality="best"
            ... )
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
            >>> feature = QuakeFeature(type="Feature", properties=props, geometry=geom)
            >>> response = QuakeResponse(type="FeatureCollection", features=[feature])
            >>> found = response.get_by_id("2023geonet001")
            >>> found is not None
            True
            >>> found.properties.publicID
            '2023geonet001'

            >>> not_found = response.get_by_id("nonexistent")
            >>> not_found is None
            True
        """
        for feature in self.features:
            if feature.properties.publicID == public_id:
                return feature
        return None

    def filter_by_magnitude(
        self, min_mag: float | None = None, max_mag: float | None = None
    ) -> list[QuakeFeature]:
        """Filter quakes by magnitude range.

        Args:
            min_mag: Minimum magnitude (inclusive), or None for no minimum
            max_mag: Maximum magnitude (inclusive), or None for no maximum

        Returns:
            List of QuakeFeatures within the magnitude range

        Examples:
            >>> from datetime import datetime
            >>> props1 = QuakeProperties(
            ...     publicID="quake1", time=datetime(2023, 1, 1),
            ...     depth=5.0, magnitude=3.0, locality="Place1", quality="best"
            ... )
            >>> props2 = QuakeProperties(
            ...     publicID="quake2", time=datetime(2023, 1, 2),
            ...     depth=10.0, magnitude=5.0, locality="Place2", quality="best"
            ... )
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.0, -41.0])
            >>> features = [
            ...     QuakeFeature(type="Feature", properties=props1, geometry=geom),
            ...     QuakeFeature(type="Feature", properties=props2, geometry=geom)
            ... ]
            >>> response = QuakeResponse(type="FeatureCollection", features=features)
            >>> filtered = response.filter_by_magnitude(min_mag=4.0)
            >>> len(filtered)
            1
            >>> filtered[0].properties.magnitude
            5.0
        """
        filtered = self.features

        if min_mag is not None:
            filtered = [f for f in filtered if f.properties.magnitude >= min_mag]

        if max_mag is not None:
            filtered = [f for f in filtered if f.properties.magnitude <= max_mag]

        return filtered

    def filter_by_mmi(
        self, min_mmi: int | None = None, max_mmi: int | None = None
    ) -> list[QuakeFeature]:
        """Filter quakes by Modified Mercalli Intensity range.

        Args:
            min_mmi: Minimum MMI (inclusive), or None for no minimum
            max_mmi: Maximum MMI (inclusive), or None for no maximum

        Returns:
            List of QuakeFeatures within the MMI range (excludes features with MMI=None)

        Examples:
            >>> from datetime import datetime
            >>> props1 = QuakeProperties(
            ...     publicID="quake1", time=datetime(2023, 1, 1),
            ...     depth=5.0, magnitude=3.0, locality="Place1", quality="best", mmi=2
            ... )
            >>> props2 = QuakeProperties(
            ...     publicID="quake2", time=datetime(2023, 1, 2),
            ...     depth=10.0, magnitude=5.0, locality="Place2", quality="best", mmi=5
            ... )
            >>> geom = QuakeGeometry(type="Point", coordinates=[174.0, -41.0])
            >>> features = [
            ...     QuakeFeature(type="Feature", properties=props1, geometry=geom),
            ...     QuakeFeature(type="Feature", properties=props2, geometry=geom)
            ... ]
            >>> response = QuakeResponse(type="FeatureCollection", features=features)
            >>> filtered = response.filter_by_mmi(min_mmi=3)
            >>> len(filtered)
            1
            >>> filtered[0].properties.MMI
            5
        """
        filtered = [f for f in self.features if f.properties.MMI is not None]

        if min_mmi is not None:
            filtered = [
                f
                for f in filtered
                if f.properties.MMI is not None and min_mmi <= f.properties.MMI
            ]

        if max_mmi is not None:
            filtered = [
                f
                for f in filtered
                if f.properties.MMI is not None and max_mmi >= f.properties.MMI
            ]

        return filtered


class QuakeStatsResponse(BaseModel):
    """Response from the quake stats endpoint."""

    # Note: The actual structure would depend on the API response
    # This is a placeholder based on typical stats endpoints
    total_count: int = Field(description="Total number of quakes")
    period: str = Field(description="Time period for statistics")
    max_magnitude: float | None = Field(
        description="Maximum magnitude in period", default=None
    )
    min_magnitude: float | None = Field(
        description="Minimum magnitude in period", default=None
    )
    avg_magnitude: float | None = Field(
        description="Average magnitude in period", default=None
    )


# Export all models in the public API
__all__ = [
    "QuakeFeature",
    "QuakeGeometry",
    "QuakeProperties",
    "QuakeResponse",
    "QuakeStatsResponse",
    "QualityType",
]

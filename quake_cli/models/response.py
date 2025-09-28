"""
Response models for API endpoints.

This module defines models for API response structures and collection types.
"""

from typing import Literal

from pydantic import BaseModel, Field

from .feature import QuakeFeature


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
            >>> from quake_cli.models.properties import QuakeProperties
            >>> from quake_cli.models.geometry import QuakeGeometry
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
            >>> from quake_cli.models.properties import QuakeProperties
            >>> from quake_cli.models.geometry import QuakeGeometry
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
            >>> from quake_cli.models.properties import QuakeProperties
            >>> from quake_cli.models.geometry import QuakeGeometry
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
            >>> from quake_cli.models.properties import QuakeProperties
            >>> from quake_cli.models.geometry import QuakeGeometry
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
            >>> from quake_cli.models.properties import QuakeProperties
            >>> from quake_cli.models.geometry import QuakeGeometry
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


class MagnitudeCounts(BaseModel):
    """Earthquake counts by magnitude for different time periods."""

    days7: dict[str, int] = Field(
        description="Earthquake counts by magnitude for the last 7 days",
        default_factory=dict,
    )
    days28: dict[str, int] = Field(
        description="Earthquake counts by magnitude for the last 28 days",
        default_factory=dict,
    )
    days365: dict[str, int] = Field(
        description="Earthquake counts by magnitude for the last 365 days",
        default_factory=dict,
    )


class RateData(BaseModel):
    """Daily earthquake rate data."""

    perDay: dict[str, int] = Field(
        description="Number of earthquakes per day (ISO date string -> count)",
        default_factory=dict,
    )


class QuakeStatsResponse(BaseModel):
    """Response from the quake stats endpoint.

    The actual API returns magnitude counts and daily rates, providing
    statistical insights into earthquake activity patterns.
    """

    magnitudeCount: MagnitudeCounts = Field(
        description="Earthquake counts by magnitude for different time periods",
        default_factory=MagnitudeCounts,
    )
    rate: RateData = Field(
        description="Daily earthquake rate statistics", default_factory=RateData
    )

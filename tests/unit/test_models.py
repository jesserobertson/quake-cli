"""Test Pydantic models for GeoNet API data structures."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from gnet.models import quake, common


class TestQuakeGeometry:
    """Test common.Point model (used as geometry)."""

    def test_valid_geometry(self):
        """Test creating valid geometry."""
        geometry = common.Point(type="Point", coordinates=[174.7633, -36.8485, 5.0])

        assert geometry.type == "Point"
        assert geometry.coordinates == [174.7633, -36.8485, 5.0]
        assert geometry.longitude == 174.7633
        assert geometry.latitude == -36.8485
        assert geometry.elevation == 5.0

    def test_geometry_properties(self):
        """Test geometry coordinate properties."""
        geometry = common.Point(type="Point", coordinates=[175.1234, -37.5678, 12.5])

        assert geometry.longitude == 175.1234
        assert geometry.latitude == -37.5678
        assert geometry.elevation == 12.5

    def test_coordinates_without_elevation(self):
        """Test coordinates without elevation."""
        geometry = common.Point(type="Point", coordinates=[174.7633, -36.8485])
        assert geometry.elevation is None

    def test_invalid_geometry_type(self):
        """Test validation of geometry type."""
        with pytest.raises(ValidationError) as exc_info:
            common.Point(type="Polygon", coordinates=[174.7633, -36.8485, 5.0])

        assert "Input should be 'Point'" in str(exc_info.value)


class TestQuakeProperties:
    """Test quake.Properties model."""

    def test_valid_properties(self):
        """Test creating valid properties."""
        properties = quake.Properties(
            publicID="2024p123456",
            time=common.TimeInfo(origin=datetime(2024, 1, 15, 10, 30, 0)),
            magnitude=common.Magnitude(value=4.2),
            location=common.Location(
                longitude=174.7633,
                latitude=-36.8485,
                elevation=-5.5,  # depth converted to elevation
                locality="10 km north of Wellington"
            ),
            quality=common.Quality(level="best"),
            intensity=common.Intensity(mmi=4),
        )

        assert properties.publicID == "2024p123456"
        assert properties.time.origin == datetime(2024, 1, 15, 10, 30, 0)
        assert properties.magnitude.value == 4.2
        assert properties.location.locality == "10 km north of Wellington"
        assert properties.intensity.mmi == 4
        assert properties.quality.level == "best"

    def test_optional_intensity(self):
        """Test that intensity can be None."""
        properties = quake.Properties(
            publicID="2024p123456",
            time=common.TimeInfo(origin=datetime(2024, 1, 15, 10, 30, 0)),
            magnitude=common.Magnitude(value=4.2),
            location=common.Location(
                longitude=174.7633,
                latitude=-36.8485,
                elevation=-5.5,
                locality="10 km north of Wellington"
            ),
            quality=common.Quality(level="preliminary"),
        )

        assert properties.intensity is None

    def test_from_legacy_api_method(self):
        """Test the from_legacy_api class method."""
        properties = quake.Properties.from_legacy_api(
            publicID="2024p123456",
            time=datetime(2024, 1, 15, 10, 30, 0),
            magnitude=4.2,
            depth=5.5,
            locality="10 km north of Wellington",
            MMI=4,
            quality="best",
            longitude=174.7633,
            latitude=-36.8485,
        )

        assert properties.publicID == "2024p123456"
        assert properties.time.origin == datetime(2024, 1, 15, 10, 30, 0)
        assert properties.magnitude.value == 4.2
        assert properties.location.locality == "10 km north of Wellington"
        assert properties.intensity.mmi == 4
        assert properties.quality.level == "best"
        assert properties.location.longitude == 174.7633
        assert properties.location.latitude == -36.8485
        assert properties.location.elevation == -5.5  # depth converted to negative elevation


class TestQuakeFeature:
    """Test quake.Feature model."""

    def test_valid_feature(self):
        """Test creating a valid feature."""
        feature = quake.Feature(
            type="Feature",
            properties=quake.Properties(
                publicID="2024p123456",
                time=common.TimeInfo(origin=datetime(2024, 1, 15, 10, 30, 0)),
                magnitude=common.Magnitude(value=4.2),
                location=common.Location(
                    longitude=174.7633,
                    latitude=-36.8485,
                    elevation=-5.5,
                    locality="10 km north of Wellington"
                ),
                quality=common.Quality(level="best"),
                intensity=common.Intensity(mmi=4),
            ),
            geometry=common.Point(
                type="Point", coordinates=[174.7633, -36.8485, 5.5]
            ),
        )

        assert feature.type == "Feature"
        assert feature.properties.publicID == "2024p123456"
        assert feature.geometry.longitude == 174.7633

    def test_feature_with_legacy_properties(self):
        """Test creating feature with from_legacy_api method."""
        feature = quake.Feature(
            type="Feature",
            properties=quake.Properties.from_legacy_api(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                magnitude=4.2,
                depth=5.5,
                locality="Wellington",
                MMI=None,
                quality="best",
                longitude=174.7633,
                latitude=-36.8485,
            ),
            geometry=common.Point(
                type="Point", coordinates=[174.7633, -36.8485, 5.5]
            ),
        )

        assert feature.properties.intensity is None


class TestQuakeResponse:
    """Test quake.Response model."""

    def test_empty_response(self):
        """Test empty response."""
        response = quake.Response(type="FeatureCollection", features=[])

        assert response.type == "FeatureCollection"
        assert response.features == []
        assert response.count == 0
        assert response.is_empty is True

    def test_response_with_features(self):
        """Test response with features."""
        feature1 = quake.Feature(
            type="Feature",
            properties=quake.Properties.from_legacy_api(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                magnitude=4.2,
                depth=5.5,
                locality="Wellington",
                MMI=4,
                quality="best",
                longitude=174.7633,
                latitude=-36.8485,
            ),
            geometry=common.Point(
                type="Point", coordinates=[174.7633, -36.8485, 5.5]
            ),
        )

        feature2 = quake.Feature(
            type="Feature",
            properties=quake.Properties.from_legacy_api(
                publicID="2024p789012",
                time=datetime(2024, 1, 16, 14, 45, 0),
                magnitude=3.8,
                depth=8.2,
                locality="Auckland",
                MMI=None,
                quality="preliminary",
                longitude=174.7645,
                latitude=-36.8500,
            ),
            geometry=common.Point(
                type="Point", coordinates=[174.7645, -36.8500, 8.2]
            ),
        )

        response = quake.Response(
            type="FeatureCollection", features=[feature1, feature2]
        )

        assert response.count == 2
        assert response.is_empty is False

    def test_filter_by_magnitude(self):
        """Test filtering by magnitude."""
        features = []
        for i, magnitude in enumerate([3.5, 4.2, 5.1, 2.8], 1):
            feature = quake.Feature(
                type="Feature",
                properties=quake.Properties.from_legacy_api(
                    publicID=f"2024p{i:06d}",
                    time=datetime(2024, 1, 15, 10, 30, 0),
                    magnitude=magnitude,
                    depth=5.5,
                    locality="Wellington",
                    MMI=None,
                    quality="best",
                    longitude=174.7633,
                    latitude=-36.8485,
                ),
                geometry=common.Point(
                    type="Point", coordinates=[174.7633, -36.8485, 5.5]
                ),
            )
            features.append(feature)

        response = quake.Response(type="FeatureCollection", features=features)

        # Test minimum magnitude filter
        filtered = response.filter_by_magnitude(min_mag=4.0)
        assert len(filtered) == 2
        assert all(f.properties.magnitude.value >= 4.0 for f in filtered)

        # Test maximum magnitude filter
        filtered = response.filter_by_magnitude(max_mag=4.0)
        assert len(filtered) == 2
        assert all(f.properties.magnitude.value <= 4.0 for f in filtered)

        # Test range filter
        filtered = response.filter_by_magnitude(min_mag=3.0, max_mag=4.5)
        assert len(filtered) == 2  # Should include 3.5 and 4.2, exclude 5.1 and 2.8

    def test_filter_by_mmi(self):
        """Test filtering by MMI."""
        features = []
        for i, mmi in enumerate([2, 4, 6, None], 1):
            feature = quake.Feature(
                type="Feature",
                properties=quake.Properties.from_legacy_api(
                    publicID=f"2024p{i:06d}",
                    time=datetime(2024, 1, 15, 10, 30, 0),
                    magnitude=4.0,
                    depth=5.5,
                    locality="Wellington",
                    MMI=mmi,
                    quality="best",
                    longitude=174.7633,
                    latitude=-36.8485,
                ),
                geometry=common.Point(
                    type="Point", coordinates=[174.7633, -36.8485, 5.5]
                ),
            )
            features.append(feature)

        response = quake.Response(type="FeatureCollection", features=features)

        # Test minimum MMI filter (should exclude None values)
        filtered = response.filter_by_mmi(min_mmi=3)
        assert len(filtered) == 2
        assert all(f.properties.intensity.mmi >= 3 for f in filtered)

        # Test maximum MMI filter
        filtered = response.filter_by_mmi(max_mmi=5)
        assert len(filtered) == 2
        assert all(f.properties.intensity.mmi <= 5 for f in filtered)


class TestQuakeStatsResponse:
    """Test quake.Stats model."""

    def test_valid_stats_response(self):
        """Test creating valid stats response."""
        stats = quake.Stats(
            magnitudeCount={
                "days7": {"0": 6, "1": 147, "2": 144, "3": 37, "4": 4, "5": 1},
                "days28": {"0": 59, "1": 527, "2": 537, "3": 117, "4": 32, "5": 5},
                "days365": {
                    "0": 1614,
                    "1": 10031,
                    "2": 7844,
                    "3": 1892,
                    "4": 529,
                    "5": 64,
                    "6": 7,
                },
            },
            rate={
                "perDay": {
                    "2024-09-28T00:00:00+00:00": 49,
                    "2024-09-29T00:00:00+00:00": 73,
                }
            },
        )

        assert stats.magnitudeCount["days7"]["1"] == 147
        assert stats.magnitudeCount["days28"]["2"] == 537
        assert stats.magnitudeCount["days365"]["1"] == 10031
        assert stats.rate["perDay"]["2024-09-28T00:00:00+00:00"] == 49

    def test_optional_magnitude_fields(self):
        """Test that fields can be empty dicts."""
        stats = quake.Stats(magnitudeCount={}, rate={})

        assert stats.magnitudeCount == {}
        assert stats.rate == {}
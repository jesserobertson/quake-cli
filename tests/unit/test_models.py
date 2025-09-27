"""Test Pydantic models for GeoNet API data structures."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from quake_cli.models import (
    QuakeFeature,
    QuakeGeometry,
    QuakeProperties,
    QuakeResponse,
    QuakeStatsResponse,
)


class TestQuakeGeometry:
    """Test QuakeGeometry model."""

    def test_valid_geometry(self):
        """Test creating valid geometry."""
        geometry = QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485, 5.0])

        assert geometry.type == "Point"
        assert geometry.coordinates == [174.7633, -36.8485, 5.0]
        assert geometry.longitude == 174.7633
        assert geometry.latitude == -36.8485
        assert geometry.depth == 5.0

    def test_geometry_properties(self):
        """Test geometry coordinate properties."""
        geometry = QuakeGeometry(type="Point", coordinates=[175.1234, -37.5678, 12.5])

        assert geometry.longitude == 175.1234
        assert geometry.latitude == -37.5678
        assert geometry.depth == 12.5

    def test_invalid_coordinates_length(self):
        """Test validation of coordinate length."""
        # Too few coordinates (less than 2)
        with pytest.raises(ValidationError):
            QuakeGeometry(type="Point", coordinates=[174.7633])

        # Too many coordinates (more than 3)
        with pytest.raises(ValidationError):
            QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485, 5.0, 1.0])

        # Valid coordinates (2 or 3 items should work)
        geom2 = QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485])
        assert geom2.depth is None

        geom3 = QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485, 5.0])
        assert geom3.depth == 5.0

    def test_invalid_geometry_type(self):
        """Test validation of geometry type."""
        with pytest.raises(ValidationError) as exc_info:
            QuakeGeometry(type="Polygon", coordinates=[174.7633, -36.8485, 5.0])

        assert "Input should be 'Point'" in str(exc_info.value)


class TestQuakeProperties:
    """Test QuakeProperties model."""

    def test_valid_properties(self):
        """Test creating valid properties."""
        properties = QuakeProperties(
            publicID="2024p123456",
            time=datetime(2024, 1, 15, 10, 30, 0),
            depth=5.5,
            magnitude=4.2,
            locality="10 km north of Wellington",
            mmi=4,
            quality="best",
        )

        assert properties.publicID == "2024p123456"
        assert properties.time == datetime(2024, 1, 15, 10, 30, 0)
        assert properties.depth == 5.5
        assert properties.magnitude == 4.2
        assert properties.locality == "10 km north of Wellington"
        assert properties.MMI == 4
        assert properties.quality == "best"

    def test_optional_mmi(self):
        """Test that MMI can be None."""
        properties = QuakeProperties(
            publicID="2024p123456",
            time=datetime(2024, 1, 15, 10, 30, 0),
            depth=5.5,
            magnitude=4.2,
            locality="10 km north of Wellington",
            quality="preliminary",
        )

        assert properties.MMI is None

    def test_validate_public_id(self):
        """Test publicID validation."""
        # Empty string should fail
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                quality="best",
            )

        assert "publicID cannot be empty" in str(exc_info.value)

        # Whitespace-only should fail
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="   ",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                quality="best",
            )

        assert "publicID cannot be empty" in str(exc_info.value)

    def test_validate_locality(self):
        """Test locality validation."""
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="",
                quality="best",
            )

        assert "locality cannot be empty" in str(exc_info.value)

    def test_depth_validation(self):
        """Test depth must be non-negative."""
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=-1.0,
                magnitude=4.2,
                locality="Wellington",
                quality="best",
            )

        assert "greater than or equal to 0" in str(exc_info.value)

    def test_mmi_bounds(self):
        """Test MMI bounds validation."""
        # Too low
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                mmi=-2,
                quality="best",
            )

        assert "greater than or equal to -1" in str(exc_info.value)

        # Too high
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                mmi=13,
                quality="best",
            )

        assert "less than or equal to 12" in str(exc_info.value)

    def test_quality_validation(self):
        """Test quality must be one of the allowed values."""
        with pytest.raises(ValidationError) as exc_info:
            QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                quality="invalid",
            )

        assert "Input should be" in str(exc_info.value)


class TestQuakeFeature:
    """Test QuakeFeature model."""

    def test_valid_feature(self):
        """Test creating a valid feature."""
        feature = QuakeFeature(
            type="Feature",
            properties=QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="10 km north of Wellington",
                mmi=4,
                quality="best",
            ),
            geometry=QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485, 5.5]),
        )

        assert feature.type == "Feature"
        assert feature.properties.publicID == "2024p123456"
        assert feature.geometry.longitude == 174.7633

    def test_invalid_feature_type(self):
        """Test feature type validation."""
        with pytest.raises(ValidationError) as exc_info:
            QuakeFeature(
                type="Point",
                properties=QuakeProperties(
                    publicID="2024p123456",
                    time=datetime(2024, 1, 15, 10, 30, 0),
                    depth=5.5,
                    magnitude=4.2,
                    locality="Wellington",
                    quality="best",
                ),
                geometry=QuakeGeometry(
                    type="Point", coordinates=[174.7633, -36.8485, 5.5]
                ),
            )

        assert "Input should be 'Feature'" in str(exc_info.value)


class TestQuakeResponse:
    """Test QuakeResponse model."""

    def test_empty_response(self):
        """Test empty response."""
        response = QuakeResponse(type="FeatureCollection", features=[])

        assert response.type == "FeatureCollection"
        assert response.features == []
        assert response.count == 0
        assert response.is_empty is True

    def test_response_with_features(self):
        """Test response with features."""
        feature1 = QuakeFeature(
            type="Feature",
            properties=QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                quality="best",
            ),
            geometry=QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485, 5.5]),
        )

        feature2 = QuakeFeature(
            type="Feature",
            properties=QuakeProperties(
                publicID="2024p789012",
                time=datetime(2024, 1, 16, 14, 45, 0),
                depth=8.2,
                magnitude=3.8,
                locality="Auckland",
                quality="preliminary",
            ),
            geometry=QuakeGeometry(type="Point", coordinates=[174.7645, -36.8500, 8.2]),
        )

        response = QuakeResponse(
            type="FeatureCollection", features=[feature1, feature2]
        )

        assert response.count == 2
        assert response.is_empty is False

    def test_get_by_id(self):
        """Test getting feature by publicID."""
        feature = QuakeFeature(
            type="Feature",
            properties=QuakeProperties(
                publicID="2024p123456",
                time=datetime(2024, 1, 15, 10, 30, 0),
                depth=5.5,
                magnitude=4.2,
                locality="Wellington",
                quality="best",
            ),
            geometry=QuakeGeometry(type="Point", coordinates=[174.7633, -36.8485, 5.5]),
        )

        response = QuakeResponse(type="FeatureCollection", features=[feature])

        found = response.get_by_id("2024p123456")
        assert found is not None
        assert found.properties.publicID == "2024p123456"

        not_found = response.get_by_id("nonexistent")
        assert not_found is None

    def test_filter_by_magnitude(self):
        """Test filtering by magnitude."""
        features = [
            QuakeFeature(
                type="Feature",
                properties=QuakeProperties(
                    publicID=f"2024p{i:06d}",
                    time=datetime(2024, 1, 15, 10, 30, 0),
                    depth=5.5,
                    magnitude=magnitude,
                    locality="Wellington",
                    quality="best",
                ),
                geometry=QuakeGeometry(
                    type="Point", coordinates=[174.7633, -36.8485, 5.5]
                ),
            )
            for i, magnitude in enumerate([3.5, 4.2, 5.1, 2.8], 1)
        ]

        response = QuakeResponse(type="FeatureCollection", features=features)

        # Test minimum magnitude filter
        filtered = response.filter_by_magnitude(min_mag=4.0)
        assert len(filtered) == 2
        assert all(f.properties.magnitude >= 4.0 for f in filtered)

        # Test maximum magnitude filter
        filtered = response.filter_by_magnitude(max_mag=4.0)
        assert len(filtered) == 2
        assert all(f.properties.magnitude <= 4.0 for f in filtered)

        # Test range filter
        filtered = response.filter_by_magnitude(min_mag=3.0, max_mag=4.5)
        assert len(filtered) == 2  # Should include 3.5 and 4.2, exclude 5.1 and 2.8

    def test_filter_by_mmi(self):
        """Test filtering by MMI."""
        features = [
            QuakeFeature(
                type="Feature",
                properties=QuakeProperties(
                    publicID=f"2024p{i:06d}",
                    time=datetime(2024, 1, 15, 10, 30, 0),
                    depth=5.5,
                    magnitude=4.0,
                    locality="Wellington",
                    mmi=mmi,
                    quality="best",
                ),
                geometry=QuakeGeometry(
                    type="Point", coordinates=[174.7633, -36.8485, 5.5]
                ),
            )
            for i, mmi in enumerate([2, 4, 6, None], 1)
        ]

        response = QuakeResponse(type="FeatureCollection", features=features)

        # Test minimum MMI filter (should exclude None values)
        filtered = response.filter_by_mmi(min_mmi=3)
        assert len(filtered) == 2
        assert all(f.properties.MMI >= 3 for f in filtered)

        # Test maximum MMI filter
        filtered = response.filter_by_mmi(max_mmi=5)
        assert len(filtered) == 2
        assert all(f.properties.MMI <= 5 for f in filtered)


class TestQuakeStatsResponse:
    """Test QuakeStatsResponse model."""

    def test_valid_stats_response(self):
        """Test creating valid stats response."""
        stats = QuakeStatsResponse(
            total_count=150,
            period="24 hours",
            max_magnitude=5.2,
            min_magnitude=1.8,
            avg_magnitude=3.4,
        )

        assert stats.total_count == 150
        assert stats.period == "24 hours"
        assert stats.max_magnitude == 5.2
        assert stats.min_magnitude == 1.8
        assert stats.avg_magnitude == 3.4

    def test_optional_magnitude_fields(self):
        """Test that magnitude fields can be None."""
        stats = QuakeStatsResponse(total_count=0, period="24 hours")

        assert stats.total_count == 0
        assert stats.max_magnitude is None
        assert stats.min_magnitude is None
        assert stats.avg_magnitude is None

"""Test the new gnet model API structure."""

from datetime import datetime

from gnet.models import quake
from gnet.models.common import Point


class TestQuakeModelsNewAPI:
    """Test the new quake model API using from_legacy_api methods."""

    def test_quake_properties_from_legacy_api(self):
        """Test creating Properties from legacy API data."""
        properties = quake.Properties.from_legacy_api(
            publicID="2025p123456",
            time=datetime(2025, 9, 28, 10, 30, 0),
            magnitude=4.2,
            depth=15.5,
            locality="Wellington area",
            MMI=4,
            quality="best",
            longitude=174.7633,
            latitude=-41.2865,
        )

        assert properties.publicID == "2025p123456"
        assert properties.time.origin == datetime(2025, 9, 28, 10, 30, 0)
        assert properties.magnitude.value == 4.2
        assert (
            abs(properties.location.elevation) == 15.5
        )  # Depth converted to elevation
        assert properties.location.locality == "Wellington area"
        assert properties.location.longitude == 174.7633
        assert properties.location.latitude == -41.2865
        assert properties.intensity is not None
        assert properties.intensity.mmi == 4
        assert properties.quality.level == "best"

    def test_quake_feature_creation(self):
        """Test creating a complete Feature with the new API."""
        properties = quake.Properties.from_legacy_api(
            publicID="2025p123456",
            time=datetime(2025, 9, 28, 10, 30, 0),
            magnitude=4.2,
            depth=15.5,
            locality="Wellington area",
            MMI=4,
            quality="best",
            longitude=174.7633,
            latitude=-41.2865,
        )

        geometry = Point(coordinates=[174.7633, -41.2865])

        feature = quake.Feature(properties=properties, geometry=geometry)

        assert feature.type == "Feature"
        assert feature.properties.publicID == "2025p123456"
        assert feature.geometry.longitude == 174.7633
        assert feature.geometry.latitude == -41.2865

    def test_quake_response_creation(self):
        """Test creating a Response with features."""
        properties = quake.Properties.from_legacy_api(
            publicID="2025p123456",
            time=datetime(2025, 9, 28, 10, 30, 0),
            magnitude=4.2,
            depth=15.5,
            locality="Wellington area",
            MMI=4,
            quality="best",
            longitude=174.7633,
            latitude=-41.2865,
        )

        geometry = Point(coordinates=[174.7633, -41.2865])
        feature = quake.Feature(properties=properties, geometry=geometry)

        response = quake.Response(features=[feature])

        assert response.type == "FeatureCollection"
        assert len(response.features) == 1
        assert response.count == 1
        assert not response.is_empty

    def test_point_geometry(self):
        """Test Point geometry functionality."""
        # Test 2D point
        point_2d = Point(coordinates=[174.7633, -41.2865])
        assert point_2d.longitude == 174.7633
        assert point_2d.latitude == -41.2865
        assert point_2d.elevation is None

        # Test 3D point
        point_3d = Point(coordinates=[174.7633, -41.2865, -15.5])
        assert point_3d.longitude == 174.7633
        assert point_3d.latitude == -41.2865
        assert point_3d.elevation == -15.5

    def test_response_filtering(self):
        """Test response filtering capabilities."""
        # Create test features with different magnitudes
        features = []
        for i, mag in enumerate([3.0, 4.5, 5.2, 2.8], 1):
            properties = quake.Properties.from_legacy_api(
                publicID=f"2025p{i:06d}",
                time=datetime(2025, 9, 28, 10, 30, 0),
                magnitude=mag,
                depth=15.5,
                locality="Test area",
                MMI=None,
                quality="best",
                longitude=174.7633,
                latitude=-41.2865,
            )
            geometry = Point(coordinates=[174.7633, -41.2865])
            feature = quake.Feature(properties=properties, geometry=geometry)
            features.append(feature)

        response = quake.Response(features=features)

        # Test magnitude filtering
        filtered = response.filter_by_magnitude(min_mag=4.0)
        assert len(filtered) == 2  # Should include 4.5 and 5.2
        assert all(f.properties.magnitude.value >= 4.0 for f in filtered)

        # Test finding features manually (since get_by_id doesn't exist)
        found = None
        for feature in response.features:
            if feature.properties.publicID == "2025p000001":
                found = feature
                break

        assert found is not None
        assert found.properties.magnitude.value == 3.0


class TestCommonModels:
    """Test common models functionality."""

    def test_point_creation_and_properties(self):
        """Test Point model creation and property access."""
        point = Point(coordinates=[174.7633, -41.2865, -15.5])

        assert point.type == "Point"
        assert point.coordinates == [174.7633, -41.2865, -15.5]
        assert point.longitude == 174.7633
        assert point.latitude == -41.2865
        assert point.elevation == -15.5

    def test_point_without_elevation(self):
        """Test Point model without elevation coordinate."""
        point = Point(coordinates=[174.7633, -41.2865])

        assert point.type == "Point"
        assert point.coordinates == [174.7633, -41.2865]
        assert point.longitude == 174.7633
        assert point.latitude == -41.2865
        assert point.elevation is None

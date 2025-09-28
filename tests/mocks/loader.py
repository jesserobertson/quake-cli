"""
Mock data loader for integration tests.

This module provides utilities to load mock API response data generated
by the build-mocks.py script for use in offline integration testing.
"""

import json
from pathlib import Path
from typing import Any

from logerr import Ok, Result

# Get the directory containing mock data
MOCK_DATA_DIR = Path(__file__).parent / "data"


class MockDataLoader:
    """Loads and provides mock API response data."""

    def __init__(self, data_dir: Path = MOCK_DATA_DIR):
        self.data_dir = data_dir
        self._cache: dict[str, Any] = {}

    def load_mock(self, mock_type: str) -> dict[str, Any] | None:
        """
        Load mock data for a specific API endpoint.

        Args:
            mock_type: Type of mock data (e.g., 'quakes_all', 'volcano_alerts')

        Returns:
            Mock data dictionary or None if not found
        """
        if mock_type in self._cache:
            return self._cache[mock_type]

        mock_file = self.data_dir / f"{mock_type}.json"
        if not mock_file.exists():
            return None

        try:
            with open(mock_file) as f:
                mock_data = json.load(f)
                self._cache[mock_type] = mock_data
                return mock_data
        except Exception:
            return None

    def get_mock_data(self, mock_type: str) -> Any | None:
        """
        Get just the data portion of a mock (without metadata).

        Args:
            mock_type: Type of mock data

        Returns:
            The data portion of the mock or None if not found
        """
        mock = self.load_mock(mock_type)
        return mock["data"] if mock else None

    def get_mock_metadata(self, mock_type: str) -> dict[str, Any] | None:
        """
        Get just the metadata portion of a mock.

        Args:
            mock_type: Type of mock data

        Returns:
            The metadata portion of the mock or None if not found
        """
        mock = self.load_mock(mock_type)
        return mock["metadata"] if mock else None

    def list_available_mocks(self) -> list[str]:
        """
        List all available mock types.

        Returns:
            List of available mock type names
        """
        if not self.data_dir.exists():
            return []

        mock_files = list(self.data_dir.glob("*.json"))
        return [f.stem for f in mock_files if f.stem != "summary"]

    def is_mock_available(self, mock_type: str) -> bool:
        """
        Check if a specific mock is available.

        Args:
            mock_type: Type of mock data to check

        Returns:
            True if the mock exists and can be loaded
        """
        return self.get_mock_data(mock_type) is not None


# Global instance for easy import
mock_loader = MockDataLoader()


def create_mock_result(mock_type: str, model_class=None) -> Result[Any, str]:
    """
    Create a Result object from mock data, optionally parsing with a Pydantic model.

    Args:
        mock_type: Type of mock data to load
        model_class: Optional Pydantic model class to parse the data

    Returns:
        Result containing the mock data or error message
    """
    data = mock_loader.get_mock_data(mock_type)
    if data is None:
        return Result.err(f"Mock data not found for {mock_type}")

    if model_class:
        try:
            parsed_data = model_class.model_validate(data)
            return Ok(parsed_data)
        except Exception as e:
            return Result.err(
                f"Failed to parse mock data with {model_class.__name__}: {e}"
            )

    return Ok(data)


def get_test_earthquake_id() -> str | None:
    """
    Get a test earthquake ID from mock data for use in tests.

    Returns:
        An earthquake publicID from mock data, or None if not available
    """
    quakes_data = mock_loader.get_mock_data("quakes_all")
    if quakes_data and quakes_data.get("features"):
        return quakes_data["features"][0]["properties"]["publicID"]

    quakes_mmi4_data = mock_loader.get_mock_data("quakes_mmi4")
    if quakes_mmi4_data and quakes_mmi4_data.get("features"):
        return quakes_mmi4_data["features"][0]["properties"]["publicID"]

    return None


def get_strong_motion_earthquake_id() -> str | None:
    """
    Get the earthquake ID used for strong motion mock data.

    Returns:
        The earthquake ID used in strong motion mock, or None if not available
    """
    metadata = mock_loader.get_mock_metadata("strong_motion")
    return metadata.get("earthquake_id") if metadata else None

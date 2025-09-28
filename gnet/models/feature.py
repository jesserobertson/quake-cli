"""
Feature models for earthquake data.

This module defines GeoJSON feature models that combine geometry and properties.
"""

from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from .geometry import QuakeGeometry
from .properties import QuakeProperties


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

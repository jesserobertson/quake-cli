"""
Properties models for earthquake metadata.

This module defines models for earthquake properties and quality indicators.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

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

"""
Pydantic models for GeoNet API data structures.

This module provides a clean hierarchy of models:
- gnet.models.common: Shared types (Magnitude, Location, etc.)
- gnet.models.quake: Earthquake models
- gnet.models.volcano: Volcano models with nested quake models
- gnet.models.intensity: Shaking intensity models

Example:
    from gnet.models import quake, volcano, intensity

    # Use earthquake models
    earthquake = quake.Feature(...)

    # Use volcano models
    volcano_alert = volcano.Feature(...)
    volcano_quake = volcano.quake.Feature(...)

    # Use intensity models
    shaking = intensity.Feature(...)
"""

# Import modules, not individual classes
from . import common, intensity, quake, volcano

# Export the module namespaces
__all__ = [
    "common",
    "quake",
    "volcano",
    "intensity",
]
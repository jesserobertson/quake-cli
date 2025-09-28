# Data Models

The quake-cli package provides comprehensive Pydantic models for handling earthquake data from the GeoNet API. All models include validation, type hints, and extensive examples.

## Core Models

::: quake_cli.models.QuakeGeometry
    options:
      members:
        - longitude
        - latitude
        - depth

::: quake_cli.models.QuakeProperties

::: quake_cli.models.QuakeFeature

::: quake_cli.models.QuakeResponse
    options:
      members:
        - count
        - is_empty
        - get_by_id
        - filter_by_magnitude
        - filter_by_mmi

::: quake_cli.models.QuakeStatsResponse

## Type Aliases

::: quake_cli.models.QualityType

## Examples in Action

All the examples shown in the docstrings above are automatically tested as part of our test suite. This ensures that:

- ✅ Examples remain current and functional
- ✅ Code changes that break examples are caught immediately
- ✅ Documentation stays synchronized with the codebase
- ✅ Users can trust that examples will work as shown

To run the docstring tests yourself:

```bash
# Test all doctests
pixi run python -m pytest --doctest-modules quake_cli/

# Test just the models
pixi run python -m doctest quake_cli/models.py -v
```
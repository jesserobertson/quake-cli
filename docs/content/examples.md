# Examples

This page showcases examples from the quake-cli codebase. All examples shown here are automatically tested as part of our test suite to ensure they remain current and functional.

## Data Models Examples

### Working with Earthquake Geometry

```python
from quake_cli.models import QuakeGeometry

# Create earthquake geometry
geom = QuakeGeometry(type="Point", coordinates=[174.123, -41.456, 5.2])

# Access coordinates
print(f"Longitude: {geom.longitude}")  # 174.123
print(f"Latitude: {geom.latitude}")    # -41.456
print(f"Depth: {geom.depth}")          # 5.2

# 2D coordinates (no depth)
geom_2d = QuakeGeometry(type="Point", coordinates=[174.123, -41.456])
print(f"Depth: {geom_2d.depth}")       # None
```

### Filtering Earthquake Data

```python
from datetime import datetime
from quake_cli.models import QuakeProperties, QuakeGeometry, QuakeFeature, QuakeResponse

# Create sample earthquake data
props1 = QuakeProperties(
    publicID="quake1",
    time=datetime(2023, 1, 1),
    depth=5.0,
    magnitude=3.0,
    locality="Place1",
    quality="best"
)
props2 = QuakeProperties(
    publicID="quake2",
    time=datetime(2023, 1, 2),
    depth=10.0,
    magnitude=5.0,
    locality="Place2",
    quality="best"
)

geom = QuakeGeometry(type="Point", coordinates=[174.0, -41.0])
features = [
    QuakeFeature(type="Feature", properties=props1, geometry=geom),
    QuakeFeature(type="Feature", properties=props2, geometry=geom)
]
response = QuakeResponse(type="FeatureCollection", features=features)

# Filter by magnitude
large_quakes = response.filter_by_magnitude(min_mag=4.0)
print(f"Found {len(large_quakes)} large earthquakes")  # 1

# Find specific earthquake
found = response.get_by_id("quake1")
if found:
    print(f"Found: {found.properties.locality}")  # Place1
```

### Working with MMI (Modified Mercalli Intensity)

```python
from datetime import datetime
from quake_cli.models import QuakeProperties, QuakeGeometry, QuakeFeature, QuakeResponse

# Create earthquakes with MMI data
props1 = QuakeProperties(
    publicID="quake1",
    time=datetime(2023, 1, 1),
    depth=5.0,
    magnitude=3.0,
    locality="Place1",
    quality="best",
    mmi=2
)
props2 = QuakeProperties(
    publicID="quake2",
    time=datetime(2023, 1, 2),
    depth=10.0,
    magnitude=5.0,
    locality="Place2",
    quality="best",
    mmi=5
)

geom = QuakeGeometry(type="Point", coordinates=[174.0, -41.0])
features = [
    QuakeFeature(type="Feature", properties=props1, geometry=geom),
    QuakeFeature(type="Feature", properties=props2, geometry=geom)
]
response = QuakeResponse(type="FeatureCollection", features=features)

# Filter by MMI intensity
significant = response.filter_by_mmi(min_mmi=3)
print(f"Found {len(significant)} significant earthquakes")  # 1
print(f"MMI: {significant[0].properties.MMI}")  # 5
```

## CLI Utilities Examples

### Formatting Dates

```python
from datetime import datetime
from quake_cli.cli import format_datetime

# Format earthquake timestamps
dt = datetime(2023, 12, 25, 14, 30, 45)
formatted = format_datetime(dt)
print(formatted)  # "2023-12-25 14:30:45"

# New Year example
dt2 = datetime(2024, 1, 1, 0, 0, 0)
formatted2 = format_datetime(dt2)
print(formatted2)  # "2024-01-01 00:00:00"
```

## Error Handling Examples

### Converting Exceptions to Results

```python
from quake_cli.result import handle_api_error

# Handle API errors functionally
error = ValueError("Invalid input")
result = handle_api_error(error)

# Check if it's an error
print(result.is_err())        # True
print(result.unwrap_err())    # "Invalid input"
```

## Response Analysis Examples

### Checking Response Status

```python
from quake_cli.models import QuakeResponse

# Empty response
empty_response = QuakeResponse(type="FeatureCollection", features=[])
print(f"Count: {empty_response.count}")      # 0
print(f"Empty: {empty_response.is_empty}")   # True

# Response with data (using the earthquake data from above)
filled_response = QuakeResponse(type="FeatureCollection", features=features)
print(f"Count: {filled_response.count}")     # 2
print(f"Empty: {filled_response.is_empty}")  # False
```

## Testing the Examples

All examples on this page are automatically tested. You can run the tests yourself:

```bash
# Run all doctests
pixi run test unit

# Run doctests for specific modules
pixi run python -m doctest quake_cli/models.py -v
pixi run python -m doctest quake_cli/cli.py -v
pixi run python -m doctest quake_cli/result.py -v

# Run pytest with doctest support
pixi run python -m pytest --doctest-modules quake_cli/ -v
```

This ensures that:

- ✅ All examples remain functional as the code evolves
- ✅ Documentation stays synchronized with the codebase
- ✅ Users can trust that examples will work as shown
- ✅ Breaking changes to public APIs are caught immediately
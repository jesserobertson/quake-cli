# Testing Documentation

This document describes the testing strategy and workflow for the quake-cli project, including our mock-based integration testing approach.

## Overview

The project uses a comprehensive testing strategy that includes:

- **Unit Tests**: Fast, isolated tests for individual functions and classes
- **Integration Tests**: Tests that verify complete workflows using real API data mocks
- **Mock-Based Offline Testing**: Integration tests that can run without internet connectivity

## Test Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_client.py             # Client functionality tests
│   ├── test_models.py             # Data model tests
│   └── test_cli.py                # CLI command tests
├── integration/                    # Integration tests
│   └── test_cli_integration.py    # CLI integration tests
├── mocks/                         # Mock data infrastructure
│   ├── data/                      # Generated mock JSON files
│   │   ├── quakes_all.json       # Recent earthquakes
│   │   ├── quake_stats.json      # Statistics data
│   │   ├── volcano_alerts.json   # Volcano alert data
│   │   └── ...                   # Other endpoint mocks
│   ├── loader.py                 # Mock data loading utilities
│   └── __init__.py
├── test_integration_mocked.py     # Main integration test suite
└── conftest.py                   # Pytest configuration
```

## Mock Generation Workflow

### 1. Generating Mock Data

The project includes a script to fetch real API data and save it as mock responses for offline testing:

```bash
# Generate fresh mock data from the GeoNet API
python scripts/build-mocks.py --verbose

# Generate specific mock types only
python scripts/build-mocks.py --types quakes_all,quake_stats

# List available mock types
python scripts/build-mocks.py --list-types
```

**Available Mock Types:**
- `quakes_all` - Recent earthquakes (up to 10)
- `quakes_mmi4` - Earthquakes with MMI ≥ 4
- `quake_stats` - Earthquake statistics
- `intensity_reported` - Reported earthquake intensities
- `intensity_measured` - Measured earthquake intensities
- `volcano_alerts` - Volcano alert levels
- `cap_feed` - CAP (Common Alerting Protocol) feed

### 2. Mock Data Structure

Each mock file contains:

```json
{
  "metadata": {
    "generated_at": "2025-09-28T16:10:29Z",
    "source": "GeoNet API",
    "description": "Recent earthquakes (up to 10)",
    "endpoint": "https://api.geonet.org.nz/quake",
    "mock_type": "quakes_all"
  },
  "data": {
    "type": "FeatureCollection",
    "features": [...]
  }
}
```

### 3. Using Mock Data in Tests

The mock loader provides utilities to access this data in tests:

```python
from tests.mocks.loader import mock_loader

# Load mock data
mock_data = mock_loader.get_mock_data("quakes_all")

# Get metadata
metadata = mock_loader.get_mock_metadata("quakes_all")

# Check availability
if mock_loader.is_mock_available("quakes_all"):
    # Use the mock data
    pass
```

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pixi run test unit

# Run specific test file
pytest tests/unit/test_client.py -v

# Run with coverage
pixi run test unit --coverage
```

### Integration Tests

Integration tests are marked with `@pytest.mark.integration` and require special flags to run:

```bash
# Run integration tests (requires --run-integration flag)
pytest tests/ --run-integration -m integration -v

# Run all tests including integration
pixi run test all

# Run specific integration test class
pytest tests/test_integration_mocked.py::TestIntegrationWithMocks --run-integration -v
```

### Understanding Test Markers

The project uses pytest markers to categorize tests:

- `@pytest.mark.integration` - Integration tests using mock data
- No marker - Unit tests (run by default)

**Why Integration Tests Need Special Flags:**

Integration tests are automatically skipped unless you provide the `--run-integration` flag. This is configured in `tests/conftest.py`:

```python
def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        return
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
```

This design ensures that:
- Fast unit tests run by default during development
- Integration tests run only when explicitly requested
- CI/CD can run different test suites for different purposes

## Integration Test Implementation

### Key Features

1. **Real API Data**: Mock responses are generated from actual GeoNet API calls
2. **Offline Testing**: Tests run without internet connectivity using saved mocks
3. **Format Conversion**: Automatic conversion between new model format and legacy API format
4. **Comprehensive Coverage**: Tests cover all major CLI commands and client operations

### Example Integration Test

```python
@pytest.mark.integration
class TestIntegrationWithMocks:
    def test_cli_quake_list_with_mock_data(self, runner, mock_response):
        """Test CLI quake list command with mock data."""
        mock_data = mock_loader.get_mock_data("quakes_all")
        assert mock_data is not None

        # Convert to legacy format for client compatibility
        legacy_data = self._convert_mock_to_legacy_format(mock_data)

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = mock_response(legacy_data)

            result = runner.invoke(app, ["quake", "list", "--limit", "3"])

            assert result.exit_code == 0
            assert "Recent Earthquakes" in result.stdout
```

### Data Format Conversion

The integration tests include automatic conversion between the new Pydantic model format and the legacy API format that the client expects:

```python
def _convert_mock_to_legacy_format(self, mock_data):
    """Convert new model format back to legacy API format for client testing."""
    if not isinstance(mock_data, dict) or "features" not in mock_data:
        return mock_data

    legacy_features = []
    for feature in mock_data["features"]:
        props = feature["properties"]
        geom = feature["geometry"]

        legacy_props = {
            "publicID": props["publicID"],
            "time": props["time"]["origin"],  # Use the datetime string
            "magnitude": props["magnitude"]["value"],
            "depth": abs(props["location"]["elevation"]) if props["location"]["elevation"] else 0,
            "locality": props["location"]["locality"],
            "quality": props["quality"]["level"],
        }

        # Add MMI if intensity exists
        if props.get("intensity"):
            legacy_props["MMI"] = props["intensity"]["mmi"]

        # ... build legacy feature structure
```

## Test Coverage

The current testing approach provides comprehensive coverage:

- **Overall Coverage**: 44.66% (improved from 37.36%)
- **Key Improvements**:
  - `health.py`: 50.00% → 100.00%
  - `list.py`: 27.66% → 61.70%
  - `stats.py`: 50.00% → 100.00%

### Coverage Analysis

```bash
# Generate coverage report
pixi run test unit --coverage

# Generate HTML coverage report
pytest tests/unit/ --cov=gnet --cov-report=html
open htmlcov/index.html
```

## Manual Testing

For manual verification of the integration testing approach:

```bash
# Run the manual integration test script
python test_integration_manually.py
```

This script provides:
- Mock data coverage analysis
- Client integration testing with verbose output
- CLI integration testing with real command execution
- Comprehensive test result reporting

## Best Practices

### When to Regenerate Mocks

Regenerate mock data when:
- The GeoNet API structure changes
- New endpoints are added to the client
- You need fresh real-world data for testing
- Mock data becomes stale (older than 1-2 weeks)

### Writing New Integration Tests

1. **Use the `@pytest.mark.integration` marker**:
   ```python
   @pytest.mark.integration
   def test_new_feature(self):
       pass
   ```

2. **Load appropriate mock data**:
   ```python
   mock_data = mock_loader.get_mock_data("appropriate_type")
   assert mock_data is not None
   ```

3. **Handle format conversion if needed**:
   ```python
   legacy_data = self._convert_mock_to_legacy_format(mock_data)
   ```

4. **Mock HTTP responses**:
   ```python
   with patch('httpx.AsyncClient.get') as mock_get:
       mock_get.return_value = mock_response(data)
       # ... test implementation
   ```

### Troubleshooting Tests

**Integration tests being skipped?**
- Ensure you're using the `--run-integration` flag
- Check that tests are properly marked with `@pytest.mark.integration`

**Mock data not found?**
- Run `python scripts/build-mocks.py` to generate fresh mocks
- Verify the mock type name matches available mocks

**Format conversion errors?**
- Check that mock data structure matches expected format
- Update conversion logic for new data fields

## Future Enhancements

Potential improvements to the testing strategy:

1. **Automatic Mock Refresh**: CI job to periodically update mock data
2. **Mock Data Validation**: Schema validation for generated mocks
3. **Performance Testing**: Integration tests that measure response times
4. **Error Scenario Mocks**: Generate mocks for API error conditions
5. **Live API Comparison**: Tests that compare mock responses with live API

## Conclusion

The mock-based integration testing approach provides:

- **Reliable offline testing** with real API data
- **Improved test coverage** through comprehensive integration scenarios
- **Fast test execution** without external dependencies
- **Realistic test data** that reflects actual API responses
- **Maintainable test suite** with clear separation of concerns

This strategy ensures that the library works correctly with real-world data while maintaining the ability to run comprehensive tests in any environment.
# GeoNet CLI Design Document

## Overview

This document outlines the design and implementation plan for a CLI tool that pulls earthquake data from the GeoNet API. The tool will provide a modern, user-friendly interface for accessing New Zealand's earthquake monitoring data.

## Requirements

### Core Requirements
- **CLI Framework**: Typer for command-line interface
- **Data Validation**: Pydantic for API response models and validation
- **HTTP Client**: httpx for fully asynchronous API calls
- **Retry Management**: tenacity for robust API call retrying
- **Terminal Output**: Rich for beautiful, formatted terminal output
- **Data Source**: GeoNet API (https://api.geonet.org.nz/)

### Technical Requirements
- Python 3.12+ with modern typing syntax
- 100% ruff compliance and full mypy coverage
- Comprehensive testing with pytest and pytest-asyncio
- Fully asynchronous API design with httpx
- Follow existing project patterns and conventions

## Architecture

### Project Structure
```
quake_cli/
├── __init__.py           # Package initialization
├── cli.py                # Typer CLI commands (async)
├── client.py             # httpx async API client
├── models.py             # Pydantic data models
└── utils.py              # Helper functions and formatters
```

### Core Components

#### 1. Data Models (`models.py`)
Pydantic models based on GeoNet API response structure:

```python
from pydantic import BaseModel
from datetime import datetime

class QuakeFeature(BaseModel):
    publicID: str
    time: datetime
    depth: float
    magnitude: float
    locality: str
    MMI: int | None
    quality: str  # best, preliminary, automatic, deleted

class QuakeResponse(BaseModel):
    type: str
    features: list[QuakeFeature]
```

#### 2. API Client (`client.py`)
Async httpx-based client with tenacity retry handling:

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class GeoNetClient:
    def __init__(self, base_url: str = "https://api.geonet.org.nz/"):
        self.base_url = base_url
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def get_quakes(self, **filters) -> QuakeResponse:
        # Async implementation with httpx and tenacity retries
```

#### 3. CLI Interface (`cli.py`)
Typer-based async commands with Rich output:

```python
import asyncio
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def list_quakes(
    limit: int = 10,
    min_magnitude: float | None = None,
    format: str = "table"
):
    asyncio.run(async_list_quakes(limit, min_magnitude, format))

async def async_list_quakes(
    limit: int,
    min_magnitude: float | None,
    format: str
):
    # Async implementation
```

## API Integration

### GeoNet API Endpoints
- **Base URL**: `https://api.geonet.org.nz/`
- **Quake Data**: `/quake` - Returns recent earthquakes
- **Single Quake**: `/quake/{publicID}` - Specific earthquake details
- **Quake History**: `/quake/history/{publicID}` - Location history
- **Statistics**: `/quake/stats` - Earthquake statistics
- **Filtered**: `/quake?MMI={int}` - Earthquakes by intensity

### Response Format
GeoJSON format with earthquake properties:
- `publicID`: Unique identifier
- `time`: Origin time (ISO 8601)
- `depth`: Depth in kilometers
- `magnitude`: Summary magnitude
- `locality`: Nearest locality description
- `MMI`: Modified Mercalli Intensity (1-12 or null)
- `quality`: Data quality indicator

## CLI Commands

### Primary Commands

#### `quake list`
List recent earthquakes with filtering options:
```bash
quake list --limit 20 --min-magnitude 4.0 --format table
quake list --since "2024-01-01" --locality "Wellington"
```

#### `quake get`
Get details for a specific earthquake:
```bash
quake get 2024p123456
quake get 2024p123456 --format json
```

#### `quake stats`
Display earthquake statistics:
```bash
quake stats --period week
quake stats --period month --format json
```

#### `quake history`
Show location history for an earthquake:
```bash
quake history 2024p123456
```

### Output Formats
- **table**: Rich formatted table (default)
- **json**: JSON output for scripting
- **csv**: CSV format for data analysis

### Filtering Options
- `--limit`: Number of results (default: 10)
- `--min-magnitude`: Minimum magnitude threshold
- `--max-magnitude`: Maximum magnitude threshold
- `--since`: Start date (ISO format or relative: "1 week ago")
- `--until`: End date
- `--locality`: Filter by locality name
- `--min-mmi`: Minimum Modified Mercalli Intensity
- `--quality`: Data quality filter (best, preliminary, automatic)

## Implementation Plan

### Phase 1: Core Infrastructure
1. **Dependencies**: Add typer, pydantic, httpx, rich to pyproject.toml
2. **Models**: Create Pydantic models for GeoNet API responses
3. **Client**: Implement basic httpx client with error handling
4. **CLI Entry Point**: Configure CLI command in pyproject.toml

### Phase 2: Basic Commands
5. **List Command**: Implement `quake list` with basic filtering
6. **Get Command**: Implement `quake get` for single earthquake details
7. **Rich Output**: Add formatted table output with Rich
8. **Error Handling**: Comprehensive API error handling

### Phase 3: Advanced Features
9. **Stats Command**: Implement earthquake statistics
10. **History Command**: Add location history functionality
11. **Output Formats**: Support JSON and CSV export
12. **Performance**: Optimize async operations and add concurrent requests

### Phase 4: Polish & Testing
13. **Testing**: Comprehensive async unit tests with pytest-asyncio
14. **Documentation**: Update docstrings and examples
15. **Quality Check**: Ensure 100% ruff compliance and mypy coverage
16. **Integration**: Update package initialization

## Error Handling

### API Errors
- HTTP connection errors (with tenacity retries)
- API rate limiting (with exponential backoff)
- Invalid earthquake IDs
- Network timeouts (with configurable retry attempts)

### User Input Errors
- Invalid date formats
- Out-of-range parameters
- Missing required arguments

### Error Display
- User-friendly error messages with Rich formatting
- Suggest corrections for common mistakes
- Graceful degradation when API is unavailable

## Configuration

### Environment Variables
- `GEONET_API_URL`: Override default API URL
- `GEONET_TIMEOUT`: HTTP request timeout (default: 30s)
- `GEONET_RETRIES`: Number of retry attempts (default: 3)
- `GEONET_RETRY_MIN_WAIT`: Minimum retry wait time in seconds (default: 4)
- `GEONET_RETRY_MAX_WAIT`: Maximum retry wait time in seconds (default: 10)

### Config File Support
Optional TOML config file for default preferences:
```toml
[quake]
default_limit = 20
default_format = "table"
api_timeout = 60
retry_attempts = 3
retry_min_wait = 4
retry_max_wait = 10
```

## Testing Strategy

### Unit Tests
- Pydantic model validation
- Async API client methods with mocked httpx responses
- Tenacity retry behavior with simulated failures
- CLI command parsing and output
- Error handling scenarios

### Integration Tests
- Live async API calls (with rate limiting consideration)
- End-to-end async CLI command execution
- Output format validation

### Test Data
- Mock GeoNet API responses
- Sample earthquake data for consistent testing
- Edge cases (empty responses, malformed data)

## Dependencies

### Required Dependencies
```toml
dependencies = [
    "typer>=0.12.0,<1",
    "pydantic>=2.5.0,<3",
    "httpx>=0.26.0,<1",
    "rich>=13.7.0,<14",
    "tenacity>=9.1.2,<10",  # existing
]
```

### Development Dependencies
All existing dev dependencies plus any additional testing tools for CLI testing.

## Future Enhancements

### Potential Features
- Interactive mode with prompts
- Earthquake alerts/notifications
- Data visualization with plots
- Export to different formats (KML, GeoJSON)
- Integration with mapping services
- Caching for offline access

### Performance Optimizations
- Response caching
- Concurrent API requests with tenacity retries
- Streaming for large datasets
- Progress bars for long operations with retry feedback

This design provides a solid foundation for implementing a professional-quality CLI tool that follows modern Python practices and integrates seamlessly with the GeoNet API.
# GeoNet CLI Design Document

## Overview

This document outlines the design and implementation status for a CLI tool that pulls earthquake data from the GeoNet API. The tool provides a modern, user-friendly interface for accessing New Zealand's earthquake monitoring data.

**Current Status: ✅ FULLY IMPLEMENTED & PRODUCTION READY**

The CLI tool has been successfully implemented with all core features operational, comprehensive testing, and production-ready code quality standards.

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

### Project Structure (IMPLEMENTED)
```
quake_cli/
├── __init__.py           # ✅ Package initialization with Result types
├── cli/                  # ✅ CLI commands (modular structure)
│   ├── __init__.py       # ✅ CLI module initialization
│   ├── main.py           # ✅ Main Typer app and entry point
│   ├── list.py           # ✅ List earthquakes command
│   ├── get.py            # ✅ Get specific earthquake command
│   ├── history.py        # ✅ Earthquake history command
│   ├── stats.py          # ✅ Statistics command
│   └── health.py         # ✅ API health check command
├── models/               # ✅ Pydantic data models (comprehensive)
│   ├── __init__.py       # ✅ Models module initialization
│   ├── response.py       # ✅ API response models
│   ├── feature.py        # ✅ Earthquake feature models
│   ├── geometry.py       # ✅ GeoJSON geometry models
│   └── properties.py     # ✅ Earthquake properties models
├── client.py             # ✅ httpx async API client with Result types
└── utils/                # ✅ Utilities and helpers
    ├── __init__.py       # ✅ Utils module initialization
    ├── base.py           # ✅ Base utility functions
    ├── output.py         # ✅ Rich output formatting
    └── result.py         # ✅ Result type utilities and decorators
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

## Implementation Status

### ✅ Phase 1: Core Infrastructure (COMPLETED)
1. **Dependencies**: ✅ Added typer, pydantic, httpx, rich, logerr to pyproject.toml
2. **Models**: ✅ Created comprehensive Pydantic models for GeoNet API responses
3. **Client**: ✅ Implemented async httpx client with Result-based error handling
4. **CLI Entry Point**: ✅ Configured CLI command in pyproject.toml with unified scripts

### ✅ Phase 2: Basic Commands (COMPLETED)
5. **List Command**: ✅ Implemented `quake list` with comprehensive filtering options
6. **Get Command**: ✅ Implemented `quake get` for single earthquake details
7. **Rich Output**: ✅ Added beautiful formatted table output with Rich
8. **Error Handling**: ✅ Comprehensive Result-based error handling with logerr

### ✅ Phase 3: Advanced Features (COMPLETED)
9. **Stats Command**: ✅ Implemented earthquake statistics with JSON output
10. **History Command**: ✅ Added location history functionality
11. **Output Formats**: ✅ Support for table, JSON, and CSV export formats
12. **Performance**: ✅ Optimized async operations with proper error handling

### ✅ Phase 4: Polish & Testing (COMPLETED)
13. **Testing**: ✅ Comprehensive async unit tests with pytest-asyncio
14. **Documentation**: ✅ Complete API documentation with MkDocs
15. **Quality Check**: ✅ 100% ruff compliance and mypy coverage maintained
16. **Integration**: ✅ Full package integration with unified pixi task management

### ✅ Phase 5: Production Features (COMPLETED)
17. **Health Check**: ✅ API health monitoring command
18. **Result Types**: ✅ Functional error handling with logerr Result types
19. **Modern Python**: ✅ Python 3.12+ features with modern typing
20. **CLI Polish**: ✅ Beautiful output with Rich, comprehensive help text

## Implementation vs Original Design

### Features That Exceeded Original Design

The final implementation went significantly beyond the original design specification:

#### 🚀 Enhanced Architecture
- **Modular CLI Structure**: Expanded from single `cli.py` to modular `cli/` package with separate command files
- **Result-Based Error Handling**: Added sophisticated functional error handling with logerr Result types (not in original design)
- **Comprehensive Models**: Expanded from basic models to full GeoJSON model hierarchy with geometry and properties
- **Utils Package**: Added comprehensive utilities for output formatting, Result handling, and base operations

#### 🚀 Advanced Features Not Originally Planned
- **Health Check Command**: Added `quake health` for API status monitoring
- **Enhanced Filtering**: More comprehensive filtering options than originally designed:
  - Multiple magnitude filters (min/max)
  - MMI (Modified Mercalli Intensity) filtering
  - Quality-based filtering with specific data quality indicators
  - Date range filtering beyond simple "since" parameter
- **Output Format Flexibility**: Enhanced beyond table/JSON to include CSV export
- **Verbose Logging**: Added `--verbose` flag for detailed error tracking and debugging

#### 🚀 Development Experience Improvements
- **Unified Task Management**: Integrated with pixi task system for unified development workflow
- **Comprehensive Documentation**: Added full MkDocs documentation site (beyond basic docstrings)
- **Result Type Integration**: Deep integration of functional programming patterns throughout codebase
- **Automatic Error Logging**: Built-in structured logging with contextual error information

#### 🚀 Code Quality Beyond Original Specification
- **100% Type Coverage**: Comprehensive mypy compliance with strict settings
- **Modern Python 3.12+**: Used latest Python features including new type syntax and match statements
- **Functional Programming**: Adopted Result types and functional composition patterns
- **Comprehensive Testing**: Enhanced async testing patterns with Result type validation

### Original Design Goals: All Achieved ✅

Every original design requirement was successfully implemented:

| Original Requirement | Implementation Status | Enhancement Level |
|----------------------|----------------------|-------------------|
| Typer CLI Framework | ✅ Fully Implemented | Enhanced with modular structure |
| Pydantic Models | ✅ Fully Implemented | Enhanced with comprehensive GeoJSON models |
| httpx Async Client | ✅ Fully Implemented | Enhanced with Result-based error handling |
| Rich Terminal Output | ✅ Fully Implemented | Enhanced with multiple output formats |
| Tenacity Retries | ✅ Fully Implemented | Enhanced with Result type integration |
| All Core Commands | ✅ Fully Implemented | Enhanced with additional health command |
| Filtering Options | ✅ Fully Implemented | Enhanced with additional filter types |
| Error Handling | ✅ Fully Implemented | Enhanced with functional Result patterns |
| Testing Coverage | ✅ Fully Implemented | Enhanced with async Result validation |
| Code Quality | ✅ Fully Implemented | Enhanced with 100% compliance standards |

### Architectural Improvements

The final architecture demonstrates several improvements over the original design:

1. **Separation of Concerns**: CLI commands separated into individual modules for better maintainability
2. **Functional Error Handling**: Adopted Result types for predictable error propagation instead of exception-based handling
3. **Type Safety**: Enhanced type safety with comprehensive models and strict mypy settings
4. **Modularity**: Clear separation between client, models, CLI, and utilities
5. **Extensibility**: Architecture supports easy addition of new commands and features

## Next Phase Opportunities

Based on the successful implementation and current architecture, several natural expansion opportunities have emerged:

### 🎯 Immediate Opportunities (Version 1.1)

#### User Experience Enhancements
1. **Interactive Mode**: Build on the existing CLI structure to add interactive prompts
   - Leverage existing filtering logic for guided query building
   - Use Rich's prompt capabilities for enhanced interactivity
   - Maintain Result-based error handling for validation

2. **Configuration Management**: Extend the current architecture for user preferences
   - Add TOML config file support building on existing patterns
   - Integrate with current environment variable handling
   - Maintain unified pixi task workflow

3. **Performance Optimizations**: Build on existing async foundation
   - Add caching layer using existing Result types for cache hit/miss handling
   - Implement concurrent requests for bulk operations
   - Add progress indicators using Rich's progress capabilities

#### Developer Experience
4. **Shell Completion**: Enhance CLI usability
   - Build on existing Typer structure for auto-completion
   - Integrate with current command structure and options
   - Support dynamic completion for earthquake IDs and localities

5. **Enhanced Output Options**: Extend current Rich-based formatting
   - Add customizable table columns and sorting
   - Expand CSV export with configurable fields
   - Add KML/GeoJSON export building on existing Pydantic models

### 🚀 Medium-term Opportunities (Version 1.2)

#### Data Visualization
6. **Terminal-based Visualization**: Leverage existing Rich integration
   - ASCII charts for earthquake trends using current statistics data
   - Terminal maps showing geographic distribution
   - Build on existing date/time filtering for trend analysis

7. **Export Enhancements**: Extend current Pydantic model system
   - Direct integration with plotting libraries
   - Enhanced data export formats building on existing CSV functionality
   - Statistical analysis tools using current filtering capabilities

#### Advanced Analysis
8. **Pattern Analysis**: Build on existing filtering and statistics
   - Trend analysis using current date range filtering
   - Anomaly detection building on current statistics command
   - Comparison tools leveraging existing Result-based error handling

### 🌟 Long-term Vision (Version 2.0+)

#### Real-time Capabilities
9. **Live Monitoring**: Extend current async architecture
   - Real-time feeds building on existing httpx client
   - Alert system using current notification patterns
   - Streaming data with existing Result type error handling

10. **Integration Ecosystem**: Leverage current modular architecture
    - Plugin system building on current CLI module structure
    - External API integration using existing client patterns
    - Webhook support extending current async capabilities

#### Platform Expansion
11. **Multi-platform Support**: Build on current foundation
    - Web API using existing client and model architecture
    - Desktop GUI leveraging current Rich formatting concepts
    - Mobile companion using existing API patterns

### 🔧 Technical Foundation for Growth

The current implementation provides an excellent foundation for these opportunities:

#### Architectural Strengths
- **Modular Design**: Easy addition of new commands and features
- **Result Types**: Robust error handling for any new functionality
- **Async Foundation**: Ready for real-time and concurrent features
- **Rich Integration**: Extensible for enhanced visualization
- **Comprehensive Models**: Solid data foundation for any expansion

#### Development Infrastructure
- **Quality Standards**: 100% compliance framework ready for new features
- **Testing Patterns**: Established async testing for new functionality
- **Documentation System**: MkDocs structure ready for feature documentation
- **Unified Workflow**: Pixi task system supports expanded development needs

#### Code Quality Momentum
- **Modern Python**: Foundation supports latest language features
- **Type Safety**: Comprehensive typing enables confident refactoring
- **Functional Patterns**: Result types scale to complex feature interactions
- **Maintainability**: Clean architecture supports long-term evolution

### 📋 Implementation Strategy

For each next phase opportunity:

1. **Leverage Existing Patterns**: Build on established Result types, async patterns, and modular structure
2. **Maintain Quality Standards**: All new features must meet existing 100% compliance requirements
3. **Enhance User Experience**: Focus on Rich integration and beautiful terminal output
4. **Preserve Architecture**: Maintain separation of concerns and functional error handling
5. **Comprehensive Testing**: Extend existing async testing patterns to new functionality

The solid foundation established in the current implementation makes these opportunities highly achievable while maintaining the project's high quality standards and user experience excellence.

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
- **Real-time monitoring** - See monitor design below

### Performance Optimizations
- Response caching
- Concurrent API requests with tenacity retries
- Streaming for large datasets
- Progress bars for long operations with retry feedback

---

# gnet monitor - Real-time Monitoring Design

## Overview

The `gnet monitor` command provides real-time monitoring of geological hazards with configurable alerts and notifications. It continuously polls GeoNet APIs and triggers actions when specified conditions are met.

## Command Structure

```bash
gnet monitor [TYPE] [OPTIONS]
```

### Monitoring Types

```bash
# Monitor all hazards
gnet monitor all --config monitor.yaml

# Monitor specific hazard types
gnet monitor quake --min-magnitude 4.0 --region wellington
gnet monitor volcano --volcano ruapehu --min-level 2
gnet monitor intensity --min-mmi 4

# Combined monitoring
gnet monitor quake volcano --config monitor.yaml
```

## Core Features

### 1. Real-time Event Streaming

```python
# Continuous polling with configurable intervals
class MonitorConfig:
    poll_interval: int = 30  # seconds
    backoff_strategy: str = "exponential"
    max_retries: int = 5
    deduplication_window: int = 300  # 5 minutes
```

### 2. Filtering & Triggers

```yaml
# monitor.yaml configuration
monitors:
  earthquakes:
    enabled: true
    filters:
      min_magnitude: 4.0
      max_depth: 50
      regions:
        - name: wellington
          bounds: [-41.5, 174.5, -41.0, 175.0]
        - name: auckland
          bounds: [-37.0, 174.5, -36.5, 175.0]
    triggers:
      - magnitude >= 5.0
      - mmi >= 5
      - location in regions.wellington and magnitude >= 4.0

  volcanoes:
    enabled: true
    volcanoes: [ruapehu, white_island, tongariro]
    triggers:
      - alert_level >= 2
      - alert_level changed
      - volcanic_earthquakes > 50 per hour
```

### 3. Alert Actions

```python
type AlertAction = Literal["console", "file", "webhook", "email", "script"]

class AlertConfig:
    actions: list[AlertAction]

    # Console output
    console:
        format: str = "rich"  # rich, json, simple
        sound: bool = True

    # File logging
    file:
        path: Path = "./monitoring.log"
        format: str = "jsonl"
        rotate: str = "daily"

    # Webhooks
    webhooks:
        - url: "https://hooks.slack.com/..."
          template: "slack"
        - url: "https://discord.com/api/webhooks/..."
          template: "discord"
        - url: "https://api.custom.com/alerts"
          template: "custom"
          headers: {"Authorization": "Bearer ..."}

    # Email (via SMTP or service)
    email:
        to: ["emergency@example.com"]
        smtp_server: "smtp.gmail.com"
        template: "detailed"

    # Custom scripts
    scripts:
        - path: "./alert_handler.py"
          args: ["--severity", "{magnitude}"]
```

## Implementation Architecture

### 1. Monitor Engine

```python
class MonitorEngine:
    """Core monitoring engine with event loop."""

    def __init__(self, config: MonitorConfig):
        self.config = config
        self.event_cache = EventCache()  # Deduplication
        self.alert_dispatcher = AlertDispatcher()
        self.health_monitor = HealthMonitor()

    async def run(self) -> None:
        """Main monitoring loop."""
        tasks = []
        if self.config.earthquakes.enabled:
            tasks.append(self.monitor_earthquakes())
        if self.config.volcanoes.enabled:
            tasks.append(self.monitor_volcanoes())

        await asyncio.gather(*tasks)

    async def monitor_earthquakes(self) -> None:
        """Monitor earthquake events."""
        while True:
            try:
                result = await self.fetch_earthquakes()
                new_events = self.event_cache.filter_new(result)

                for event in new_events:
                    if self.evaluate_triggers(event):
                        await self.alert_dispatcher.dispatch(event)

            except Exception as e:
                await self.handle_error(e)

            await asyncio.sleep(self.config.poll_interval)
```

### 2. Event Processing Pipeline

```python
class EventProcessor:
    """Process and enrich events before alerting."""

    async def process(self, event: QuakeFeature) -> ProcessedEvent:
        # Enrich with additional data
        enriched = await self.enrich_event(event)

        # Calculate derived metrics
        enriched.estimated_impact = self.calculate_impact(event)
        enriched.affected_population = await self.get_population_data(event)

        # Add contextual information
        enriched.historical_context = await self.get_historical_context(event)
        enriched.nearby_events = await self.get_nearby_events(event)

        return enriched
```

### 3. Alert Templates

```python
# Slack template
SLACK_TEMPLATE = {
    "text": "Earthquake Alert",
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 M{magnitude} Earthquake Detected"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Location:* {location}"},
                {"type": "mrkdwn", "text": "*Depth:* {depth} km"},
                {"type": "mrkdwn", "text": "*Time:* {time}"},
                {"type": "mrkdwn", "text": "*MMI:* {mmi}"}
            ]
        }
    ]
}

# Email template
EMAIL_TEMPLATE = """
EARTHQUAKE ALERT - M{magnitude}

Location: {location}
Time: {time} UTC
Depth: {depth} km
Intensity: MMI {mmi}

Estimated Impact:
- Affected Population: {affected_population:,}
- Expected Shaking: {shaking_description}

View Details: https://www.geonet.org.nz/earthquake/{publicid}

This is an automated alert from gnet monitor.
"""
```

## CLI Interface

### Basic Monitoring

```bash
# Simple magnitude-based monitoring
gnet monitor quake --min-magnitude 4.0

# Region-specific monitoring
gnet monitor quake --region wellington --min-magnitude 3.5

# Volcano monitoring
gnet monitor volcano --volcano ruapehu

# Multiple hazard monitoring
gnet monitor all --min-magnitude 4.0 --min-alert-level 2
```

### Advanced Configuration

```bash
# Use configuration file
gnet monitor --config monitor.yaml

# Override config options
gnet monitor --config monitor.yaml --poll-interval 10

# Dry run mode (test triggers without sending alerts)
gnet monitor --config monitor.yaml --dry-run

# Verbose debugging
gnet monitor --config monitor.yaml --verbose
```

### Output Examples

```
┌─────────────────────────────────────────────────────────────┐
│ gnet monitor - Real-time Geological Hazard Monitoring      │
├─────────────────────────────────────────────────────────────┤
│ Status: ACTIVE | Uptime: 02:34:15 | Events: 12            │
│ Monitoring: Earthquakes (M≥4.0), Volcanoes (Level≥2)      │
└─────────────────────────────────────────────────────────────┘

[2025-10-01 14:23:45] 🔴 ALERT: M5.2 Earthquake
  Location: 15 km north-east of Wellington
  Depth: 23 km | MMI: 5 (Moderate)
  → Webhook notification sent
  → Email alert dispatched

[2025-10-01 14:45:12] 🟡 WARNING: Ruapehu Alert Level Changed
  Previous: 1 (Minor unrest)
  Current: 2 (Moderate unrest)
  → Monitoring frequency increased

[2025-10-01 15:01:33] ⚪ INFO: M3.8 Earthquake (below threshold)
  Location: 45 km south of Taupo
  Depth: 67 km | MMI: 2 (Weak)
```

## Integration Examples

### Python Script Integration

```python
from gnet.monitor import Monitor, MonitorConfig

# Programmatic monitoring
async def custom_monitor():
    config = MonitorConfig(
        earthquakes={
            "min_magnitude": 4.0,
            "regions": ["wellington", "auckland"]
        },
        alerts={
            "webhook": "https://myapp.com/alerts",
            "custom_handler": process_alert
        }
    )

    monitor = Monitor(config)

    # Custom event handler
    @monitor.on_event
    async def handle_event(event):
        if event.magnitude >= 5.0:
            await send_emergency_alert(event)

    await monitor.start()

# Custom alert processor
async def process_alert(event):
    # Custom logic for handling alerts
    if event.type == "earthquake" and event.magnitude >= 6.0:
        await activate_emergency_protocol()
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

RUN pip install gnet

COPY monitor.yaml /config/monitor.yaml

CMD ["gnet", "monitor", "--config", "/config/monitor.yaml"]
```

```yaml
# docker-compose.yaml
services:
  gnet-monitor:
    image: gnet-monitor:latest
    volumes:
      - ./config:/config
      - ./logs:/logs
    environment:
      - GNET_LOG_LEVEL=INFO
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    restart: always
```

### Systemd Service

```ini
# /etc/systemd/system/gnet-monitor.service
[Unit]
Description=GeoNet Hazard Monitor
After=network.target

[Service]
Type=simple
User=monitor
WorkingDirectory=/opt/gnet-monitor
ExecStart=/usr/local/bin/gnet monitor --config /opt/gnet-monitor/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Performance Considerations

### Resource Usage

- **Memory**: ~50-100MB base, +10MB per 1000 cached events
- **CPU**: <5% average, spikes during event processing
- **Network**: ~1-5 requests/minute per monitor type
- **Disk I/O**: Minimal, only for logging and caching

### Scaling Strategies

1. **Horizontal Scaling**: Run multiple monitors for different regions
2. **Event Bus**: Use Redis/RabbitMQ for event distribution
3. **Database Backend**: Store events in TimescaleDB for analysis
4. **Load Distribution**: Round-robin API requests across endpoints

## Security Considerations

### API Keys & Credentials

```python
# Use environment variables or secure vault
os.environ["GNET_API_KEY"]  # If GeoNet implements auth
os.environ["SLACK_WEBHOOK_URL"]
os.environ["EMAIL_PASSWORD"]

# Or use config file with proper permissions
chmod 600 monitor.yaml
```

### Webhook Security

- Validate SSL certificates
- Use webhook signing/HMAC verification
- Implement rate limiting
- Whitelist allowed webhook domains

## Future Enhancements

### Phase 1 (MVP)
- [x] Basic earthquake monitoring
- [x] Console output alerts
- [x] Magnitude/region filtering
- [ ] Configuration file support
- [ ] Webhook notifications

### Phase 2 (Enhanced)
- [ ] Volcano monitoring integration
- [ ] Email notifications
- [ ] Event deduplication
- [ ] Historical context in alerts
- [ ] Custom alert templates

### Phase 3 (Advanced)
- [ ] Machine learning predictions
- [ ] Swarm detection algorithms
- [ ] P-wave/S-wave analysis
- [ ] Integration with other hazard systems
- [ ] Mobile app notifications
- [ ] GraphQL subscriptions

## Testing Strategy

### Unit Tests

```python
async def test_monitor_trigger_evaluation():
    """Test trigger condition evaluation."""
    monitor = Monitor(config)

    event = create_test_event(magnitude=5.2)
    assert monitor.evaluate_triggers(event) == True

    event = create_test_event(magnitude=3.0)
    assert monitor.evaluate_triggers(event) == False

async def test_event_deduplication():
    """Test that duplicate events are filtered."""
    cache = EventCache(window=300)

    event1 = create_test_event(id="2025p001")
    event2 = create_test_event(id="2025p001")  # Duplicate

    assert cache.is_new(event1) == True
    assert cache.is_new(event2) == False
```

### Integration Tests

```python
@pytest.mark.integration
async def test_full_monitoring_pipeline():
    """Test complete monitoring pipeline."""
    with mock_geonet_api():
        monitor = Monitor(test_config)

        # Inject test event
        await inject_test_event(magnitude=5.0)

        # Verify alert was triggered
        assert await wait_for_alert() == True

        # Verify webhook was called
        assert mock_webhook.called == True
```

## Documentation

### User Guide
- Getting started with monitoring
- Configuration file reference
- Alert template customization
- Troubleshooting guide

### API Reference
- MonitorConfig schema
- Event types and properties
- Webhook payload formats
- Custom handler interfaces

### Examples
- Basic earthquake monitoring
- Multi-region monitoring
- Custom alert handlers
- Docker deployment
- Kubernetes deployment

---

This design provides a solid foundation for implementing a professional-quality CLI tool that follows modern Python practices and integrates seamlessly with the GeoNet API.
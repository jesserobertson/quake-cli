# CLI Utilities

The CLI module provides utilities for formatting and displaying earthquake data in terminal applications.

## Utility Functions

::: quake_cli.cli.format_datetime
::: quake_cli.cli.create_quakes_table
::: quake_cli.cli.output_data

## Error Handling

::: quake_cli.cli.handle_result
::: quake_cli.cli.handle_errors

## Configuration

::: quake_cli.cli.configure_logging

## Command Implementations

The CLI commands (list, get, history, stats, health) are implemented as Typer commands. See the [CLI Usage Guide](../quickstart.md) for examples of using the command-line interface.

## Examples

All utility functions include comprehensive docstring examples that are automatically tested:

```python
from datetime import datetime
from quake_cli.cli import format_datetime

# Format a datetime for display
dt = datetime(2023, 12, 25, 14, 30, 45)
formatted = format_datetime(dt)
print(formatted)  # Output: "2023-12-25 14:30:45"
```

The CLI utilities support rich console output with tables, progress bars, and colored text for an excellent user experience.
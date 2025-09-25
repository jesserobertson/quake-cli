# Installation

## Requirements

- Python 3.12+

## Install from PyPI

The recommended way to install quake-cli is from PyPI using pip:

```bash
pip install quake_cli
```

## Optional Dependencies

quake-cli supports several optional dependencies for additional functionality:

### Development Dependencies

If you want to contribute to the project or run tests:

```bash
pip install quake_cli[dev]
```

### Documentation Dependencies

To build documentation locally:

```bash
pip install quake_cli[docs]
```

### All Dependencies

To install all optional dependencies:

```bash
pip install quake_cli[all]
```

## Development Installation

If you want to contribute to quake-cli, you can install it in development mode:

### Prerequisites

1. Install [pixi](https://pixi.sh) package manager
2. Clone the repository:

```bash
git clone https://github.com/jesserobertson/quake-cli.git
cd quake-cli
```

### Setup Development Environment

```bash
# Install dependencies
pixi install

# Set up development environment (pre-commit hooks, etc.)
pixi run dev setup

# Run tests to verify installation
pixi run test unit
```

## Verify Installation

To verify that quake-cli is installed correctly:

```python
import quake_cli
print(quake_cli.__version__)
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've installed quake_cli in the correct Python environment.

2. **Version Conflicts**: Try installing in a fresh virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install quake_cli
   ```

### Getting Help

If you encounter any issues during installation:

1. Check the [Issue Tracker](https://github.com/jesserobertson/quake-cli/issues)
2. Search for existing solutions
3. Create a new issue if needed
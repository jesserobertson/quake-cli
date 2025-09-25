# quake-cli

[![CI](https://github.com/jesserobertson/quake-cli/workflows/CI/badge.svg)](https://github.com/jesserobertson/quake-cli/actions)
[![codecov](https://codecov.io/gh/jesserobertson/quake-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/jesserobertson/quake-cli)
[![PyPI version](https://badge.fury.io/py/quake_cli.svg)](https://badge.fury.io/py/quake_cli)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jesserobertson.github.io/quake-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pull data from GeoNet API

## Features

- 🚀 **Modern Python 3.12+** with comprehensive type hints
- 📦 **Unified Development Experience** with pixi task management
- 🧪 **Comprehensive Testing** with pytest
- 🔍 **Code Quality Enforcement** with ruff and mypy (100% compliance)
- ⚡ **Async Support** with both synchronous and asynchronous APIs
- 📚 **Beautiful Documentation** with MkDocs Material
- 🔒 **Security Scanning** and dependency management
- 🤖 **Automated CI/CD** with GitHub Actions

## Quick Start

### Installation

```bash
pip install quake_cli
```

### Basic Usage

```python
import quake_cli

# Your code here
print("Hello from quake-cli!")
```

### Async Usage

```python
import asyncio
import quake_cli

async def main():
    # Your async code here
    print("Async hello from quake-cli!")

asyncio.run(main())
```

## Installation Options

### Basic Installation

```bash
pip install quake_cli
```

### Development Installation

For contributors and developers:

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Clone and set up the project
git clone https://github.com/jesserobertson/quake-cli.git
cd quake-cli

# Install dependencies and set up development environment
pixi install
pixi run dev setup

# Run tests to verify installation
pixi run test unit
```

## Development

This project uses modern Python development practices with comprehensive tooling:

### Development Commands

```bash
# Testing
pixi run test unit                 # Run unit tests

# Code Quality  
pixi run quality check             # Run all quality checks
pixi run quality fix               # Auto-fix issues

# Documentation
pixi run docs serve                # Serve docs locally
pixi run docs build                # Build documentation

# Build & Distribution
pixi run build package             # Build package
pixi run build check               # Check package

# Development Environment
pixi run dev setup                 # Set up dev environment
pixi run dev status                # Show environment status
```

### Code Quality Standards

This project maintains **100% ruff compliance** and comprehensive type coverage:

- **Formatting**: Automated with ruff
- **Linting**: Strict ruff configuration with modern Python rules
- **Type Checking**: Full mypy coverage with strict settings
- **Testing**: Comprehensive test suite with coverage reporting

### Contributing

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/quake-cli.git
   cd quake-cli
   ```
3. **Set up development environment**:
   ```bash
   pixi install
   pixi run dev setup
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
5. **Make your changes** and ensure all tests pass:
   ```bash
   pixi run check-all
   ```
6. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Create a Pull Request** on GitHub

## Documentation
- **[Full Documentation](https://jesserobertson.github.io/quake-cli)** - Comprehensive guides and API reference
- **[Installation Guide](docs/content/installation.md)** - Detailed installation instructions
- **[Quick Start](docs/content/quickstart.md)** - Get up and running quickly
- **[API Reference](docs/content/api/)** - Complete API documentation

### Building Documentation Locally

```bash
# Serve documentation with live reload
pixi run docs serve

# Build static documentation
pixi run docs build
```

## Requirements

- **Python 3.12+**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://jesserobertson.github.io/quake-cli
- **Issues**: https://github.com/jesserobertson/quake-cli/issues
- **Discussions**: https://github.com/jesserobertson/quake-cli/discussions

## Acknowledgments

- Built with [pixi](https://pixi.sh) for modern Python dependency management
- Tested with [pytest](https://pytest.org)
- Documentation powered by [MkDocs](https://mkdocs.org) with [Material theme](https://squidfunk.github.io/mkdocs-material/)
- Code quality enforced by [ruff](https://docs.astral.sh/ruff/) and [mypy](https://mypy.readthedocs.io)

---

Made with ❤️ by [Jess Robertson](https://github.com/jesserobertson)
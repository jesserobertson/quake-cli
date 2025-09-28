"""
Entry point for running quake-cli as a module.

This allows the package to be run as:
    python -m quake_cli
"""

from quake_cli.cli import app

if __name__ == "__main__":
    app()

"""
Entry point for running gnet as a module.

This allows the package to be run as:
    python -m gnet
"""

from gnet.cli.main import app

if __name__ == "__main__":
    app()
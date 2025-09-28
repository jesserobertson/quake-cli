"""
Base utilities and decorators for CLI commands.

This module provides common functionality used across all CLI commands.
"""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any

import typer
from logerr import Err, Ok, Result
from loguru import logger
from rich.console import Console

from quake_cli.client import GeoNetError

# Initialize Rich console
console = Console()

# Global verbose flag
_verbose_logging = False


def configure_logging(verbose: bool) -> None:
    """Configure logging levels based on verbose flag."""
    global _verbose_logging
    _verbose_logging = verbose

    if verbose:
        # Enable detailed logging with timestamps and levels
        logger.remove()  # Remove default handler
        import sys

        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
        )
        console.print("[dim]Verbose logging enabled[/dim]")
    else:
        # Remove all handlers to suppress logerr automatic logging
        logger.remove()
        # Add a minimal handler that only shows critical errors to stderr
        import sys

        logger.add(
            sys.stderr,
            format="<red>{message}</red>",
            level="CRITICAL",
            filter=lambda record: record["level"].name == "CRITICAL",
        )


def handle_result(result: Result) -> Any:
    """Handle Result types and convert errors to CLI exits."""
    match result:
        case Ok(value):
            return value
        case Err(error_msg):
            if _verbose_logging:
                # In verbose mode, the error is already logged by logerr
                console.print(f"[red]Error:[/red] {error_msg}")
            else:
                # In non-verbose mode, show a clean error message
                console.print(f"[red]Error:[/red] {error_msg}")
            raise typer.Exit(1)


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle common CLI errors."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except typer.Exit:
            # Re-raise typer.Exit to allow proper CLI exit
            raise
        except GeoNetError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            raise typer.Exit(130) from None
        except Exception as e:
            console.print(f"[red]Unexpected error:[/red] {e}")
            raise typer.Exit(1) from e

    return wrapper


def get_progress_console() -> "Console":
    """Get a console instance for progress indicators that outputs to stderr.

    This ensures progress indicators don't interfere with stdout output,
    following Unix conventions for separating data and status information.
    """
    import sys

    from rich.console import Console as RichConsole

    return RichConsole(file=sys.stderr)


def async_command(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to run async commands with asyncio."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(func(*args, **kwargs))

    return wrapper

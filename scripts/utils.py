#!/usr/bin/env python3
"""
Shared utilities for script commands.
Provides a unified command runner using the sh library.
"""

from pathlib import Path
from typing import Any

import sh
import typer
from rich.console import Console

console = Console()

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent


class CommandResult:
    """Result wrapper for command execution."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def success(self) -> bool:
        """Whether the command was successful."""
        return self.returncode == 0


def run_command(
    cmd: list[str], capture_output: bool = False, check: bool = True, real_time_output: bool = False
) -> CommandResult:
    """Run a shell command with proper error handling using sh.

    Args:
        cmd: Command and arguments as list
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise on non-zero exit code
        real_time_output: Whether to show output in real-time

    Returns:
        CommandResult with returncode, stdout, stderr

    Raises:
        typer.Exit: If check=True and command fails
    """
    try:
        command_name = cmd[0]
        args = cmd[1:] if len(cmd) > 1 else []
        
        # Handle special cases for command names with hyphens
        command_attr = command_name.replace("-", "_")
        
        # Get the command from sh
        try:
            command = getattr(sh, command_attr)
        except AttributeError:
            # Try without underscore replacement for some commands
            try:
                command = getattr(sh, command_name)
            except AttributeError:
                console.print(f"[red]❌ Command not found: {command_name}[/red]")
                if check:
                    raise typer.Exit(1)
                return CommandResult(
                    returncode=1, stderr=f"Command not found: {command_name}"
                )
        
        # Set working directory
        command = command.bake(_cwd=PROJECT_ROOT)

        if capture_output:
            try:
                result = command(*args, _return_cmd=True)
                return CommandResult(
                    returncode=0, stdout=str(result.stdout), stderr=str(result.stderr)
                )
            except sh.ErrorReturnCode as e:
                return CommandResult(
                    returncode=e.exit_code,
                    stdout=e.stdout.decode() if e.stdout else "",
                    stderr=e.stderr.decode() if e.stderr else "",
                )
        else:
            # Run command without capturing output
            if real_time_output:
                # Force real-time output by explicitly setting _out and _err
                import sys
                command(*args, _out=sys.stdout, _err=sys.stderr)
            else:
                command(*args)
            return CommandResult()

        
    except sh.ErrorReturnCode as e:
        console.print(f"[red]❌ Command failed: {' '.join(cmd)}[/red]")
        if capture_output:
            stdout = e.stdout.decode() if e.stdout else ""
            stderr = e.stderr.decode() if e.stderr else ""
            if stdout:
                console.print(f"[yellow]STDOUT: {stdout}[/yellow]")
            if stderr:
                console.print(f"[red]STDERR: {stderr}[/red]")

        if check:
            raise typer.Exit(1)

        return CommandResult(
            returncode=e.exit_code,
            stdout=e.stdout.decode() if e.stdout else "",
            stderr=e.stderr.decode() if e.stderr else "",
        )
    except Exception as e:
        console.print(f"[red]❌ Unexpected error running command: {e}[/red]")
        if check:
            raise typer.Exit(1)
        return CommandResult(returncode=1, stderr=str(e))


def run_command_simple(cmd: list[str]) -> bool:
    """Simple command runner that returns success/failure.

    Args:
        cmd: Command and arguments as list

    Returns:
        True if command succeeded, False otherwise
    """
    result = run_command(cmd, capture_output=False, check=False)
    return result.success


def run_command_capture(cmd: list[str]) -> CommandResult:
    """Run command and capture output without raising on failure.

    Args:
        cmd: Command and arguments as list

    Returns:
        CommandResult with captured output
    """
    return run_command(cmd, capture_output=True, check=False)
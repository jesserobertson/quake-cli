#!/usr/bin/env python3
"""
Code quality management script with mypy, ruff, and coverage support.
Unified interface for all code quality tasks.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from utils import run_command

app = typer.Typer(
    name="quality",
    help="Code Quality Management Script",
    add_completion=False,
)
console = Console()

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
PACKAGE_PATH = PROJECT_ROOT / "quake_cli"
TESTS_PATH = PROJECT_ROOT / "tests"


@app.command()
def check() -> None:
    """Run all quality checks (typecheck + lint + format check)."""
    panel = Panel.fit("🔍 Running All Code Quality Checks", style="blue")
    console.print(panel)
    
    results = {}
    
    # Type checking
    with Status("Running mypy type checking...", console=console, spinner="dots"):
        try:
            run_command(["mypy", "quake_cli"])
            results["typecheck"] = "✅ Pass"
        except typer.Exit:
            results["typecheck"] = "❌ Fail"
    
    # Linting
    with Status("Running ruff linting...", console=console, spinner="dots"):
        try:
            run_command(["ruff", "check", "quake_cli", "tests"])
            results["lint"] = "✅ Pass"
        except typer.Exit:
            results["lint"] = "❌ Fail"
    
    # Format checking
    with Status("Checking code formatting...", console=console, spinner="dots"):
        try:
            run_command(["ruff", "format", "--check", "quake_cli", "tests"])
            results["format"] = "✅ Pass"
        except typer.Exit:
            results["format"] = "❌ Fail"
    
    # Results table
    table = Table(title="Quality Check Results", show_header=True, header_style="bold magenta")
    table.add_column("Check", style="cyan")
    table.add_column("Result", justify="center")
    
    table.add_row("Type Check", results["typecheck"])
    table.add_row("Linting", results["lint"])
    table.add_row("Formatting", results["format"])
    
    console.print(table)
    
    # Exit with error if any check failed
    if "❌ Fail" in results.values():
        console.print("\n[red]❌ Some quality checks failed[/red]")
        raise typer.Exit(1)
    else:
        console.print("\n[green]✅ All quality checks passed![/green]")


@app.command()
def typecheck() -> None:
    """Run mypy type checking."""
    console.print("🔍 Running mypy type checking...")
    run_command(["mypy", "quake_cli"])
    console.print("[green]✅ Type checking passed![/green]")


@app.command()
def lint() -> None:
    """Run ruff linting (check only)."""
    console.print("🔍 Running ruff linting...")
    run_command(["ruff", "check", "quake_cli", "tests"])
    console.print("[green]✅ Linting passed![/green]")


@app.command()
def format(check_only: bool = typer.Option(False, "--check", help="Check formatting without making changes")) -> None:
    """Format code with ruff (or check formatting)."""
    if check_only:
        console.print("🔍 Checking code formatting...")
        run_command(["ruff", "format", "--check", "quake_cli", "tests"])
        console.print("[green]✅ Code formatting is correct![/green]")
    else:
        console.print("🎨 Formatting code with ruff...")
        run_command(["ruff", "format", "quake_cli", "tests"])
        console.print("[green]✅ Code formatted![/green]")


@app.command()
def fix() -> None:
    """Auto-fix all possible issues (format + lint --fix)."""
    console.print("🔧 Auto-fixing code issues...")
    
    # Format code
    with Status("Formatting code...", console=console, spinner="dots"):
        run_command(["ruff", "format", "quake_cli", "tests"])
    
    # Fix linting issues
    with Status("Fixing linting issues...", console=console, spinner="dots"):
        run_command(["ruff", "check", "--fix", "quake_cli", "tests"])
    
    console.print("[green]✅ Auto-fix completed![/green]")
    console.print("[yellow]💡 Run 'pixi run quality check' to verify all issues are resolved[/yellow]")


@app.command()
def coverage(
    html: bool = typer.Option(False, "--html", help="Generate HTML coverage report"),
    show_missing: bool = typer.Option(True, "--show-missing/--no-missing", help="Show missing lines")
) -> None:
    """Show coverage report."""
    if html:
        console.print("📊 Generating HTML coverage report...")
        run_command(["coverage", "html"])
        console.print("[green]✅ Coverage report generated in htmlcov/index.html[/green]")
    else:
        console.print("📊 Showing coverage report...")
        cmd = ["coverage", "report"]
        if show_missing:
            cmd.append("--show-missing")
        run_command(cmd)


if __name__ == "__main__":
    # Change to project root directory
    import os
    os.chdir(PROJECT_ROOT)
    app()
"""Test basic package setup and imports."""

import pytest


def test_package_imports():
    """Test that the main package can be imported."""
    import quake_cli

    assert quake_cli.__version__ == "0.1.0"
    assert quake_cli.__author__ == "Jess Robertson"


def test_dependencies_import():
    """Test that all required dependencies can be imported."""
    # Core dependencies
    import httpx
    import pydantic
    import rich.console
    import tenacity
    import typer

    # Verify basic functionality
    assert hasattr(httpx, "AsyncClient")
    assert hasattr(pydantic, "BaseModel")
    assert hasattr(rich.console, "Console")
    assert hasattr(tenacity, "retry")
    assert hasattr(typer, "Typer")


def test_exception_classes():
    """Test that custom exception classes are available."""
    from quake_cli import QuakeCliConfigError, QuakeCliError

    # Test exception hierarchy
    assert issubclass(QuakeCliConfigError, QuakeCliError)
    assert issubclass(QuakeCliError, Exception)

    # Test that exceptions can be raised and caught
    with pytest.raises(QuakeCliError):
        raise QuakeCliError("Test error")

    with pytest.raises(QuakeCliConfigError):
        raise QuakeCliConfigError("Test config error")


def test_public_api():
    """Test that the public API is correctly exposed."""
    import quake_cli

    # Check that __all__ contains expected items
    expected_exports = {
        "__author__",
        "__email__",
        "__version__",
        "QuakeCliError",
        "QuakeCliConfigError",
    }

    assert set(quake_cli.__all__) == expected_exports

    # Check that all exported items can be accessed
    for item in expected_exports:
        assert hasattr(quake_cli, item), f"Missing export: {item}"

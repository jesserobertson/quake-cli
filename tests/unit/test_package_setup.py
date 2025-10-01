"""Test basic package setup and imports."""

import pytest


def test_package_imports():
    """Test that the main package can be imported."""
    import gnet

    assert gnet.__version__ == "0.1.0"
    assert gnet.__author__ == "Jess Robertson"


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
    from gnet import GNetConfigError, GNetError

    # Test exception hierarchy
    assert issubclass(GNetConfigError, GNetError)
    assert issubclass(GNetError, Exception)

    # Test that exceptions can be raised and caught
    with pytest.raises(GNetError):
        raise GNetError("Test error")

    with pytest.raises(GNetConfigError):
        raise GNetConfigError("Test config error")


def test_public_api():
    """Test that the public API is correctly exposed."""
    import gnet

    # Check that __all__ contains expected items (excluding CLI to avoid circular imports)
    expected_exports = {
        "__author__",
        "__email__",
        "__version__",
        "GNetError",
        "GNetConfigError",
        "GeoNetClient",
        "GeoNetError",
    }

    assert set(gnet.__all__) == expected_exports

    # Check that all exported items can be accessed
    for item in expected_exports:
        assert hasattr(gnet, item), f"Missing export: {item}"

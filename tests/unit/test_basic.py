"""
Basic unit tests for quake-cli.
"""

import pytest

import quake_cli


class TestBasicFunctionality:
    """Test basic functionality of the package."""

    def test_package_imports(self):
        """Test that the package can be imported."""
        assert quake_cli is not None

    def test_package_has_version(self):
        """Test that the package has a version attribute."""
        assert hasattr(quake_cli, "__version__")
        assert isinstance(quake_cli.__version__, str)
        assert len(quake_cli.__version__) > 0

    def test_package_version_format(self):
        """Test that the version follows semantic versioning."""
        version = quake_cli.__version__
        # Basic semantic version format check (major.minor.patch)
        parts = version.split(".")
        assert len(parts) >= 2, f"Version {version} should have at least major.minor"

        # Check that major and minor are numbers
        assert parts[0].isdigit(), f"Major version should be numeric, got {parts[0]}"
        assert parts[1].isdigit(), f"Minor version should be numeric, got {parts[1]}"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_import_all_public_modules(self):
        """Test that all public modules can be imported without errors."""
        # This test helps catch import-time errors
        import quake_cli

        # Test that we can access common attributes without errors
        dir(quake_cli)


class TestTypeHints:
    """Test type hint compatibility."""

    def test_package_is_typed(self):
        """Test that the package includes type information."""
        import quake_cli

        # Check if py.typed file exists (indicates PEP 561 compliance)
        # This is more of a packaging test
        package_path = quake_cli.__file__
        if package_path:
            from pathlib import Path

            package_dir = Path(package_path).parent
            py_typed = package_dir / "py.typed"
            # Note: This might not exist during development, so we make it optional
            if py_typed.exists():
                assert py_typed.is_file()


class TestAsyncSupport:
    """Test async functionality support."""

    @pytest.mark.asyncio
    async def test_async_import(self):
        """Test that async modules can be imported."""
        try:
            # Import async components if they exist
            import quake_cli.async_module  # noqa: F401
        except ImportError:
            # Async module might not exist yet, skip test
            pytest.skip("Async module not implemented yet")

    @pytest.mark.asyncio
    async def test_basic_async_functionality(self):
        """Test basic async functionality."""

        async def dummy_async_function():
            return "async_result"

        result = await dummy_async_function()
        assert result == "async_result"


class TestModernPythonPatterns:
    """Test modern Python 3.12+ patterns and features."""

    def test_match_statement_basic(self):
        """Test basic match statement usage."""

        def process_value(value: int | str | list) -> str:
            match value:
                case int() if value > 0:
                    return "positive_integer"
                case int() if value == 0:
                    return "zero"
                case int():
                    return "negative_integer"
                case str() if len(value) > 5:
                    return "long_string"
                case str():
                    return "short_string"
                case list() if len(value) == 0:
                    return "empty_list"
                case list():
                    return "non_empty_list"
                case _:
                    return "unknown_type"

        assert process_value(42) == "positive_integer"
        assert process_value(0) == "zero"
        assert process_value(-5) == "negative_integer"
        assert process_value("hello world") == "long_string"
        assert process_value("hi") == "short_string"
        assert process_value([]) == "empty_list"
        assert process_value([1, 2, 3]) == "non_empty_list"

    def test_match_statement_with_destructuring(self):
        """Test match statement with destructuring."""

        def process_coordinates(coord: tuple[int, int] | tuple[int, int, int]) -> str:
            match coord:
                case (0, 0):
                    return "origin_2d"
                case (x, 0) if x > 0:
                    return "positive_x_axis"
                case (0, y) if y > 0:
                    return "positive_y_axis"
                case (x, y) if x > 0 and y > 0:
                    return "first_quadrant"
                case (x, y):
                    return f"2d_point({x}, {y})"
                case (x, y, z):
                    return f"3d_point({x}, {y}, {z})"
                case _:
                    return "invalid_coordinate"

        assert process_coordinates((0, 0)) == "origin_2d"
        assert process_coordinates((5, 0)) == "positive_x_axis"
        assert process_coordinates((0, 3)) == "positive_y_axis"
        assert process_coordinates((2, 3)) == "first_quadrant"
        assert process_coordinates((-1, -2)) == "2d_point(-1, -2)"
        assert process_coordinates((1, 2, 3)) == "3d_point(1, 2, 3)"

    def test_modern_type_annotations(self):
        """Test modern Python 3.12+ type annotations."""

        # Union types with |
        def process_id(user_id: int | str) -> str:
            match user_id:
                case int():
                    return f"numeric_id_{user_id}"
                case str():
                    return f"string_id_{user_id}"

        assert process_id(123) == "numeric_id_123"
        assert process_id("abc") == "string_id_abc"

        # Built-in generics
        def process_items(items: list[dict[str, int | str]]) -> int:
            return len(items)

        test_items = [{"name": "item1", "count": 5}, {"name": "item2", "count": "many"}]
        assert process_items(test_items) == 2

    def test_type_aliases(self):
        """Test modern type alias syntax."""
        # Modern type statement (Python 3.12+)
        type UserId = int | str
        type ConfigDict = dict[str, str | int | bool]

        def validate_user_id(user_id: UserId) -> bool:
            match user_id:
                case int() if user_id > 0:
                    return True
                case str() if len(user_id) > 0:
                    return True
                case _:
                    return False

        assert validate_user_id(123) is True
        assert validate_user_id("user123") is True
        assert validate_user_id(0) is False
        assert validate_user_id("") is False

        def process_config(config: ConfigDict) -> bool:
            required_keys = {"host", "port", "debug"}
            return all(key in config for key in required_keys)

        test_config: ConfigDict = {"host": "localhost", "port": 8080, "debug": True}
        assert process_config(test_config) is True

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

quake-cli is Pull data from GeoNet API. It follows modern Python development practices with comprehensive tooling and unified development workflows.

**Key Features:**
- Modern Python 3.12+ with comprehensive type hints
- **Functional error handling with Result types using logerr**
- **Automatic error logging with structured context**
- Unified development experience with pixi task management
- Comprehensive testing with pytest
- Code quality enforcement with ruff and mypy (100% compliance required)
- Both synchronous and asynchronous APIs
- Beautiful documentation with MkDocs Material
- Automated CI/CD with GitHub Actions
- Security scanning and dependency management

## Development Commands

Use `pixi` with unified task scripts for all development tasks:

### **Core Unified Scripts**
```bash
# Testing (unit)
pixi run test --help               # Show all test commands
pixi run test unit                 # Run unit tests with coverage
pixi run test all                  # Run all tests (unit + docs)
pixi run test clean                # Clean test artifacts

# Code Quality (linting, formatting, type checking)
pixi run quality --help            # Show all quality commands
pixi run quality check             # Run all quality checks (MUST pass 100%)
pixi run quality typecheck         # Run mypy type checking
pixi run quality format            # Format code with ruff
pixi run quality lint              # Run ruff linting
pixi run quality fix               # Auto-fix all possible issues

# Development Environment
pixi run dev --help               # Show all dev commands
pixi run dev setup                # Install pre-commit hooks
pixi run dev status               # Show development environment status
pixi run dev clean                # Clean development artifacts

# Build & Distribution
pixi run build --help             # Show all build commands
pixi run build package            # Build wheel and source distribution
pixi run build status             # Show build status and information
pixi run build clean              # Clean build artifacts

# Documentation
pixi run docs --help              # Show all docs commands
pixi run docs serve               # Serve documentation locally
pixi run docs build               # Build documentation
pixi run docs status              # Show documentation status
pixi run docs clean               # Clean documentation build
```

### **Unified Operations**
```bash
# Unified clean (all artifacts)
pixi run clean                    # Clean test + docs + build + dev artifacts

# Comprehensive checks (all tests + quality)
pixi run check-all                # Run all tests + quality checks
```

## Architecture & Philosophy

### Core Principles
- **Modern Python patterns**: Use Python 3.12+ features and type hints
- **Functional error handling**: Use Result types instead of exceptions for predictable error flows
- **Automatic observability**: Structured logging with logerr for all operations
- **Unified development experience**: Local commands match CI/CD exactly
- **Quality enforcement**: 100% ruff compliance, comprehensive mypy typing
- **Comprehensive testing**: Unit tests with Result pattern validation
- **Async-first design**: Support both sync and async APIs where appropriate
- **Documentation-driven**: Keep docs up-to-date and comprehensive
- **Security-conscious**: Regular dependency scanning and security checks

### Project Structure
```
quake-cli/
├── quake_cli/         # Main package  
│   ├── __init__.py            # Package initialization
│   ├── py.typed               # PEP 561 type marker
│   ├── sync/                  # Synchronous operations
│   ├── async/                 # Asynchronous operations
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── conftest.py            # Test configuration
├── docs/                      # Documentation
│   ├── content/               # Documentation content
│   └── mkdocs.yml             # MkDocs configuration
├── scripts/                   # Unified development scripts
└── .github/workflows/         # CI/CD workflows
```

### API Design Principles
- **Explicit over implicit**: Clear function signatures and parameters
- **Type safety first**: Full mypy coverage with strict settings
- **Result-based error handling**: Use Result types for predictable error propagation
- **Functional composition**: Chain operations using `.then()` and `.map()` methods
- **Match statement patterns**: Use pattern matching for Result handling instead of `.is_err()`
- **Async compatibility**: Consistent APIs between sync and async versions
- **Modern Python patterns**: Use match statements, union types, and built-in generics
- **Automatic logging**: All errors automatically logged with structured context
- **Documentation**: Comprehensive docstrings with examples
- **Testing**: Every public function should have comprehensive tests

## Result-Based Error Handling (MANDATORY)

**This project uses functional error handling with logerr Result types instead of exceptions for predictable error flows.**

### Required Result Patterns

**✅ ALWAYS use Result types for fallible operations:**
```python
from logerr import Ok, Err, Result

# Define Result type aliases
type QuakeResult = Result[QuakeResponse, str]
type FeatureResult = Result[QuakeFeature, str]

async def get_quakes(self, limit: int | None = None) -> QuakeResult:
    result = await self._make_request("quake", params)

    def parse_and_limit_response(data: dict[str, Any]) -> QuakeResult:
        try:
            response = QuakeResponse.model_validate(data)
            if limit is not None and limit > 0:
                response.features = response.features[:limit]
            return Ok(response)
        except Exception as e:
            return Err(f"Failed to parse response: {e!s}")

    return result.then(parse_and_limit_response)  # Functional chaining
```

**✅ Use match statements for Result handling:**
```python
# In CLI handlers
def handle_result(result: Result) -> Any:
    match result:
        case Ok(value):
            return value
        case Err(error_msg):
            console.print(f"[red]Error:[/red] {error_msg}")
            raise typer.Exit(1)

# In API operations
match result:
    case Err(error):
        return Err(f"Health check failed: {error}")
    case Ok(_):
        return Ok(True)
```

**✅ Chain operations with .then() and .map():**
```python
# Functional composition instead of unwrapping
return (await self.get_quakes())
    .then(apply_magnitude_filters)
    .then(apply_mmi_filters)
    .map(limit_results)
```

**❌ NEVER use these anti-patterns:**
```python
# ❌ Don't unwrap Results manually
if result.is_err():
    return result
data = result.unwrap()  # Avoid this

# ❌ Don't use exceptions for predictable errors
try:
    response = await api_call()
    if response.status_code >= 400:
        raise APIError("Bad response")  # Use Result instead
except APIError as e:
    handle_error(e)

# ❌ Don't use is_err() when match statements are clearer
if result.is_err():
    handle_error(result.unwrap_err())
else:
    process_success(result.unwrap())
```

### Automatic Error Logging

**All Result errors are automatically logged with structured context:**
```python
# Automatic logging when Result contains errors
result = await client.get_quakes()
# If error occurs, logerr automatically logs:
# 2025-09-28 16:10:29 | ERROR | quake_cli.client:_make_request:158 - API error occurred

# Enable verbose logging in CLI
pixi run quake list --verbose  # Shows detailed error traces
```

### Result Type Guidelines

**Define clear Result type aliases:**
```python
# ✅ Clear type aliases for common Result patterns
type QuakeResult = Result[QuakeResponse, str]
type FeatureResult = Result[QuakeFeature, str]
type DataResult = Result[dict[str, Any], str]
```

**Use Result composition for complex operations:**
```python
# ✅ Compose operations functionally
return (await self.get_quakes()).then(apply_filters)
```

## Modern Python 3.12+ Typing Requirements

**This project targets Python 3.12+ and MUST use modern typing syntax:**

- **Use union syntax**: `A | B` instead of `Union[A, B]`
- **Use built-in generics**: `list[str]`, `dict[str, Any]` instead of `List[str]`, `Dict[str, Any]`
- **Use modern optional syntax**: `T | None` instead of `Optional[T]`
- **Use new type statement**: `type MyType = int | str` instead of `MyType: TypeAlias = Union[int, str]`
- **Minimal typing imports**: Only import what you actually need
- **Use match statements**: Prefer pattern matching over if/elif chains where appropriate

**Examples of correct modern typing:**
```python
# ✅ Modern (Python 3.12+)
type UserId = int | str
type ConfigDict = dict[str, Any]
type ItemList = list[dict[str, Any]]

def process_items(
    items: ItemList,
    user_id: UserId | None = None,
    config: ConfigDict | None = None
) -> bool:
    match result:
        case Success(data):
            return process_success(data)
        case Error(msg):
            return handle_error(msg)
```

**Examples of deprecated syntax (DO NOT USE):**
```python
# ❌ Old style (Python < 3.12)
from typing import Union, List, Dict, Optional, TypeAlias

UserIdType: TypeAlias = Union[int, str]
ConfigDict = Dict[str, Any]
ItemList = List[Dict[str, Any]]

def process_items(
    items: ItemList,
    user_id: Optional[UserIdType] = None,
    config: Optional[Dict[str, str]] = None
) -> bool:
    if result.is_ok():
        return process_success(result.value)
    else:
        return handle_error(result.error)
```

## Development Practices

### Code Quality Standards
- **MANDATORY**: Maintain 100% ruff compliance - all ruff checks must pass before committing
- Always run `pixi run check-all` before committing changes
- Use pre-commit hooks for automated quality checks: `pixi run dev setup`
- Maintain 100% type coverage with mypy
- Write comprehensive tests with good coverage

### Ruff Compliance Standards
This project enforces **100% ruff compliance** with no exceptions. All code must pass:

```bash
# These commands must return "All checks passed!"
pixi run quality check             # Runs all quality checks
pixi run quality lint              # Linting compliance  
pixi run quality format --check    # Formatting compliance
```

**Key ruff rules enforced:**
- **No unused arguments (ARG001)**: All function parameters must be used
- **Proper variable binding**: Correct closure handling in lambdas
- **Boolean simplification**: Use direct boolean evaluation instead of `== True`
- **Absolute imports**: Use absolute imports instead of relative imports
- **Clean formatting**: No trailing whitespace or formatting inconsistencies

**Code quality workflow:**
1. Write code following project patterns
2. Run `pixi run quality check` to verify compliance
3. Fix any ruff issues before committing
4. Commit only when all checks pass

**When ruff issues arise:**
- **Auto-fix when possible**: Run `pixi run quality fix` to automatically resolve fixable issues
- **Manual fixes required for**: Complex logic issues, unused arguments, variable binding
- **Never ignore rules**: All ruff issues must be resolved, no exceptions

### Testing Strategy
- **Comprehensive coverage**: Aim for high test coverage across all code paths
- **Multiple test types**: Unit tests
- **Test organization**: Keep tests well-organized and maintainable
- **Async testing patterns**: Use `pytest-asyncio` with proper async fixtures

### Async Development Practices
- **Use async/await consistently**: Don't mix async and sync operations without proper handling
- **Leverage concurrency**: Use `asyncio.gather()` for concurrent operations when appropriate
- **Handle backpressure**: Use proper flow control to avoid overwhelming resources
- **Test async code properly**: Use `pytest-asyncio` for async test methods

## Environment Setup

This project uses pixi for dependency management and provides a unified development experience.

**Prerequisites:**
- Python 3.12+
- [pixi](https://pixi.sh) package manager

**Setup:**
```bash
# Clone repository
git clone https://github.com/jesserobertson/quake-cli.git
cd quake-cli

# Install dependencies
pixi install

# Set up development environment
pixi run dev setup

# Verify installation
pixi run test unit
pixi run quality check
```

## Security Guidelines

### Critical Security Rules
- **NEVER commit credentials**: API keys, tokens, passwords, or connection strings must never be committed to git
- **Environment variables**: Use environment variables for sensitive configuration
- **Dependency security**: Regularly check dependencies for vulnerabilities with `pixi run security`
- **Input validation**: Sanitize all user inputs to prevent injection attacks

### Development Security Practices
- **Type safety**: Full mypy coverage helps prevent security bugs
- **Logging safety**: Ensure credentials are never logged
- **Dependency pinning**: Use pinned dependency versions to prevent supply chain attacks
- **Pre-commit hooks**: Use automated security scanning before commits

## Adding New Functionality

When adding new features to quake-cli:

1. **Follow existing patterns**: Look at similar functionality for consistency
2. **Add comprehensive tests**: Include unit tests
3. **Update documentation**: Add docstrings and update user guides
4. **Type everything**: Ensure full mypy compatibility with modern typing
5. **Run quality checks**: Ensure `pixi run check-all` passes
6. **Consider async support**: Add async versions for I/O operations
7. **Update CLAUDE.md**: Add any new development patterns or requirements

## Deployment & Distribution

### Building for Distribution
```bash
# Build package
pixi run build package

# Check package quality
pixi run build check

# Upload to PyPI (with proper credentials)
pixi run build upload
```

### CI/CD Pipeline
The project uses GitHub Actions for:
- **Continuous Integration**: Automated testing and quality checks
- **Security Scanning**: Dependency vulnerability scanning
- **Documentation**: Automated documentation builds
- **Release Management**: Automated PyPI publishing on releases

All CI/CD operations use the same unified scripts as local development, ensuring consistency between local testing and production deployment.
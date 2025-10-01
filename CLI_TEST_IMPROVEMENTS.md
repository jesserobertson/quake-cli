# CLI Test Structure Improvements

## Issues Found and Solutions

### 1. Root Cause: Incorrect Mock Setup ✅ FIXED

**Issue**: Tests were mocking `client.get_quakes()` but the command calls `client.search_quakes()` by default.

**Solution Applied**: Updated all list command tests to mock the correct method:
```python
# OLD (incorrect)
mock_client.get_quakes.return_value = Ok(mock_response)

# NEW (correct)
mock_client.search_quakes.return_value = Ok(mock_response)
```

### 2. String Matching Brittleness ✅ PARTIALLY FIXED

**Issue**: Tests fail when table formatting truncates "Wellington" → "Wellingt…"

**Solution Applied**: Updated assertions to match actual output:
```python
# OLD (brittle)
assert "Wellington" in result.stdout

# NEW (robust)
assert "Wellingt" in result.stdout  # Text is truncated in table display
```

## Proposed Improvements for Future

### 1. Layer-Based Testing Strategy

Instead of testing everything through the full CLI stack, use multiple test layers:

```python
# Layer 1: Command Logic Tests (Unit)
@pytest.mark.unit
def test_list_command_logic():
    """Test command logic without CLI framework"""
    # Test the core business logic directly
    # Mock only the client, not the CLI framework

# Layer 2: CLI Integration Tests
@pytest.mark.integration
def test_list_command_cli():
    """Test CLI integration with known good data"""
    # Use fixed test data files instead of complex mocks

# Layer 3: Output Format Tests
@pytest.mark.format
def test_list_command_output_formats():
    """Test that different output formats work"""
    # Focus on format structure, not specific content
```

### 2. Mock Abstraction Layer

Create a test utility to handle client mocking consistently:

```python
class MockGeoNetClient:
    """Test utility for consistent client mocking"""

    @classmethod
    def setup_list_success(cls, response_data):
        """Setup mock for successful list command"""
        mock_client = AsyncMock()
        # Automatically mock both get_quakes AND search_quakes
        mock_client.get_quakes.return_value = Ok(response_data)
        mock_client.search_quakes.return_value = Ok(response_data)
        return mock_client

    @classmethod
    def setup_error(cls, error_msg):
        """Setup mock for error scenarios"""
        mock_client = AsyncMock()
        # Mock all methods to return the same error
        error_result = Err(error_msg)
        mock_client.get_quakes.return_value = error_result
        mock_client.search_quakes.return_value = error_result
        return mock_client
```

### 3. Flexible Output Verification

Instead of exact string matching, use more flexible patterns:

```python
def test_list_command_contains_earthquake_data(self, runner, mock_response):
    """Test that list output contains expected earthquake data"""
    # Setup mock with utility
    mock_client = MockGeoNetClient.setup_list_success(mock_response)

    result = runner.invoke(app, ["quake", "list", "--limit", "1"])

    # Flexible assertions
    assert result.exit_code == 0
    assert_contains_earthquake_id(result.stdout, "2025p123456")
    assert_contains_magnitude(result.stdout, 4.2)
    assert_contains_location_reference(result.stdout, "Wellington")  # Handles truncation

def assert_contains_location_reference(output: str, location: str):
    """Helper that handles truncated location names"""
    # Check for full name or reasonable truncation
    min_chars = min(8, len(location))  # At least 8 chars or full name
    truncated = location[:min_chars]
    assert truncated in output, f"Expected location reference '{truncated}' in output"
```

### 4. Data-Driven Tests

Use parameterized tests for different scenarios:

```python
@pytest.mark.parametrize("command_args,expected_method", [
    (["quake", "list"], "search_quakes"),
    (["quake", "list", "--mmi", "4"], "get_quakes"),
    (["quake", "list", "--min-magnitude", "3.0"], "search_quakes"),
])
def test_list_command_calls_correct_method(command_args, expected_method):
    """Test that different parameter combinations call the right client method"""
    # This would catch the get_quakes vs search_quakes issue automatically
```

### 5. Contract Testing

Test the interface contracts rather than implementation details:

```python
def test_list_command_contract(self, runner):
    """Test the command contract - what it promises to do"""
    # Given: A successful response from any client method
    # When: Running list command
    # Then: Should display earthquake data in table format

    # This test doesn't care which client method is called,
    # only that the command fulfills its contract
```

## Benefits of Proposed Structure

1. **Reduced Brittleness**: Tests focus on behavior rather than implementation details
2. **Better Error Messages**: Clear separation between different types of failures
3. **Easier Maintenance**: Changes to formatting don't break core functionality tests
4. **Better Coverage**: Different aspects tested at appropriate levels
5. **Faster Feedback**: Unit tests run faster, integration tests catch system issues

## Implementation Priority

1. **High Priority**: Mock abstraction layer (prevents future mock setup issues)
2. **Medium Priority**: Flexible output verification (reduces string matching brittleness)
3. **Low Priority**: Full layer restructure (would require larger refactoring)

The current fixes solve the immediate issues. These improvements would prevent similar issues in the future.
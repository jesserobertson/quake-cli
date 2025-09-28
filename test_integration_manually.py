#!/usr/bin/env python3
"""
Manual test runner for integration tests to verify they work properly.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from httpx import Response

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.mocks.loader import mock_loader
from gnet.client import GeoNetClient
from gnet.models import quake


async def test_client_integration():
    """Test client integration with mock data."""
    print("🔄 Testing client integration with mock data...")

    # Load mock data
    mock_data = mock_loader.get_mock_data("quakes_all")
    if mock_data is None:
        print("❌ No mock data found!")
        return False

    print(f"✅ Mock data loaded: {len(mock_data['features'])} earthquakes")

    # Create mock response
    mock_resp = AsyncMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_data

    # Test client with mock
    with patch('httpx.AsyncClient.get', return_value=mock_resp):
        async with GeoNetClient() as client:
            result = await client.get_quakes()

            if result.is_err():
                print(f"❌ Client error: {result.unwrap_err()}")
                return False

            response = result.unwrap()
            print(f"✅ Client returned {len(response.features)} earthquakes")

            # Test model structure
            if response.features:
                feature = response.features[0]
                print(f"✅ First earthquake: {feature.properties.publicID}")
                print(f"   Magnitude: {feature.properties.magnitude.value}")
                print(f"   Location: {feature.properties.location.locality}")
                print(f"   Coordinates: {feature.geometry.longitude}, {feature.geometry.latitude}")

    return True


def test_cli_integration():
    """Test CLI integration with mock data."""
    print("\n🔄 Testing CLI integration with mock data...")

    from typer.testing import CliRunner
    from gnet.cli.main import app

    mock_data = mock_loader.get_mock_data("quakes_all")
    if mock_data is None:
        print("❌ No mock data found!")
        return False

    mock_resp = AsyncMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_data

    runner = CliRunner()

    with patch('httpx.AsyncClient.get', return_value=mock_resp):
        result = runner.invoke(app, ["quake", "list", "--limit", "3"])

        if result.exit_code != 0:
            print(f"❌ CLI error: {result.stdout}")
            return False

        print("✅ CLI command successful")
        print(f"   Output contains 'Recent Earthquakes': {'Recent Earthquakes' in result.stdout}")

        # Test JSON output
        result_json = runner.invoke(app, ["quake", "list", "--format", "json", "--limit", "1"])
        if result_json.exit_code == 0:
            print("✅ JSON output format working")
        else:
            print(f"❌ JSON output failed: {result_json.stdout}")

    return True


def test_mock_data_coverage():
    """Test what mock data we have available."""
    print("\n📊 Mock Data Coverage:")

    available_mocks = mock_loader.list_available_mocks()
    print(f"Available mock datasets: {len(available_mocks)}")

    for mock_type in available_mocks:
        metadata = mock_loader.get_mock_metadata(mock_type)
        data = mock_loader.get_mock_data(mock_type)

        if metadata:
            print(f"  • {mock_type}")
            print(f"    Description: {metadata.get('description', 'No description')}")
            print(f"    Generated: {metadata.get('generated_at', 'Unknown')}")

            if isinstance(data, dict) and 'features' in data:
                print(f"    Features: {len(data['features'])}")
            elif isinstance(data, dict):
                print(f"    Keys: {list(data.keys())}")


async def main():
    """Run all integration tests."""
    print("🧪 Manual Integration Test Runner")
    print("=" * 50)

    # Test mock data coverage
    test_mock_data_coverage()

    # Test client integration
    client_success = await test_client_integration()

    # Test CLI integration
    cli_success = test_cli_integration()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Client Integration: {'✅ PASS' if client_success else '❌ FAIL'}")
    print(f"  CLI Integration: {'✅ PASS' if cli_success else '❌ FAIL'}")

    if client_success and cli_success:
        print("\n🎉 All integration tests PASSED!")
        print("   The mock-based testing approach is working correctly.")
        print("   Real API data is being used to test offline functionality.")
        return 0
    else:
        print("\n❌ Some integration tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
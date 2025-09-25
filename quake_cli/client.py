"""
Async HTTP client for GeoNet API.

This module provides an async client for interacting with the GeoNet API,
including retry logic with tenacity and comprehensive error handling.
"""

import os
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from quake_cli.models import QuakeFeature, QuakeResponse


class GeoNetError(Exception):
    """Base exception for GeoNet API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GeoNetConnectionError(GeoNetError):
    """Raised when unable to connect to GeoNet API."""

    pass


class GeoNetTimeoutError(GeoNetError):
    """Raised when GeoNet API request times out."""

    pass


class GeoNetAPIError(GeoNetError):
    """Raised when GeoNet API returns an error response."""

    pass


class GeoNetClient:
    """Async client for GeoNet API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        retries: int | None = None,
        retry_min_wait: float | None = None,
        retry_max_wait: float | None = None,
    ) -> None:
        """
        Initialize GeoNet API client.

        Args:
            base_url: Base URL for GeoNet API (default from env or https://api.geonet.org.nz/)
            timeout: Request timeout in seconds (default from env or 30)
            retries: Number of retry attempts (default from env or 3)
            retry_min_wait: Minimum wait time between retries (default from env or 4)
            retry_max_wait: Maximum wait time between retries (default from env or 10)
        """
        self.base_url = base_url or os.getenv(
            "GEONET_API_URL", "https://api.geonet.org.nz/"
        )
        self.timeout = timeout or float(os.getenv("GEONET_TIMEOUT", "30"))
        self.retries = retries or int(os.getenv("GEONET_RETRIES", "3"))
        self.retry_min_wait = retry_min_wait or float(
            os.getenv("GEONET_RETRY_MIN_WAIT", "4")
        )
        self.retry_max_wait = retry_max_wait or float(
            os.getenv("GEONET_RETRY_MAX_WAIT", "10")
        )

        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "GeoNetClient":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=str(self.base_url),
            timeout=httpx.Timeout(self.timeout),
            headers={
                "Accept": "application/vnd.geo+json;version=2",
                "User-Agent": "quake-cli/0.1.0",
            },
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    def _create_retry_decorator(self) -> Any:
        """Create tenacity retry decorator with configured settings."""
        return retry(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(
                multiplier=1, min=self.retry_min_wait, max=self.retry_max_wait
            ),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
            reraise=True,
        )

    async def _make_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the GeoNet API with retry logic.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            GeoNetConnectionError: If connection fails after retries
            GeoNetTimeoutError: If request times out after retries
            GeoNetAPIError: If API returns an error response
        """
        if not self.client:
            raise GeoNetError("Client not initialized. Use async context manager.")

        @self._create_retry_decorator()  # type: ignore[misc]
        async def _request() -> httpx.Response:
            try:
                assert self.client is not None  # For mypy
                response = await self.client.get(endpoint, params=params or {})
                return response
            except httpx.TimeoutException as e:
                raise GeoNetTimeoutError(f"Request timed out: {e}") from e
            except httpx.ConnectError as e:
                raise GeoNetConnectionError(f"Connection failed: {e}") from e

        try:
            response = await _request()
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            raise GeoNetAPIError(
                f"API returned {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except GeoNetError:
            # Re-raise our custom errors as-is
            raise
        except Exception as e:
            raise GeoNetError(f"Unexpected error: {e}") from e

    async def get_quakes(
        self,
        mmi: int | None = None,
        limit: int | None = None,
    ) -> QuakeResponse:
        """
        Get earthquake data from GeoNet API.

        Args:
            mmi: Modified Mercalli Intensity filter (-1 to 12)
            limit: Maximum number of results (applied client-side)

        Returns:
            QuakeResponse containing earthquake features

        Raises:
            GeoNetError: If request fails or data is invalid
        """
        params: dict[str, Any] = {}

        if mmi is not None:
            if not -1 <= mmi <= 12:
                raise ValueError("MMI must be between -1 and 12")
            params["MMI"] = mmi

        try:
            data = await self._make_request("quake", params)
            response = QuakeResponse.model_validate(data)

            # Apply client-side limit if specified
            if limit is not None and limit > 0:
                response.features = response.features[:limit]

            return response
        except Exception as e:
            if isinstance(e, GeoNetError):
                raise
            raise GeoNetError(f"Failed to parse quake response: {e}") from e

    async def get_quake(self, public_id: str) -> QuakeFeature:
        """
        Get a specific earthquake by its publicID.

        Args:
            public_id: Unique earthquake identifier

        Returns:
            QuakeFeature for the specified earthquake

        Raises:
            GeoNetError: If request fails or earthquake not found
            ValueError: If public_id is empty
        """
        if not public_id.strip():
            raise ValueError("public_id cannot be empty")

        try:
            data = await self._make_request(f"quake/{public_id.strip()}")
            return QuakeFeature.model_validate(data)
        except GeoNetAPIError as e:
            if e.status_code == 404:
                raise GeoNetError(f"Earthquake {public_id} not found") from e
            raise
        except Exception as e:
            if isinstance(e, GeoNetError):
                raise
            raise GeoNetError(f"Failed to parse quake response: {e}") from e

    async def get_quake_history(self, public_id: str) -> Any:
        """
        Get location history for a specific earthquake.

        Args:
            public_id: Unique earthquake identifier

        Returns:
            Location history records (raw data)

        Raises:
            GeoNetError: If request fails or earthquake not found
            ValueError: If public_id is empty
        """
        if not public_id.strip():
            raise ValueError("public_id cannot be empty")

        try:
            data = await self._make_request(f"quake/history/{public_id.strip()}")
            # Note: History endpoint structure may vary - returning raw data for now
            return data if isinstance(data, list) else [data]  # type: ignore[unreachable]
        except GeoNetAPIError as e:
            if e.status_code == 404:
                raise GeoNetError(
                    f"Earthquake history for {public_id} not found"
                ) from e
            raise
        except Exception as e:
            if isinstance(e, GeoNetError):
                raise
            raise GeoNetError(f"Failed to parse history response: {e}") from e

    async def get_quake_stats(self) -> dict[str, Any]:
        """
        Get earthquake statistics.

        Returns:
            Dictionary containing earthquake statistics

        Raises:
            GeoNetError: If request fails or data is invalid

        Note:
            The exact structure of stats response depends on the API implementation.
            This returns raw data for now until we can verify the actual structure.
        """
        try:
            return await self._make_request("quake/stats")
        except Exception as e:
            if isinstance(e, GeoNetError):
                raise
            raise GeoNetError(f"Failed to parse stats response: {e}") from e

    async def search_quakes(
        self,
        min_magnitude: float | None = None,
        max_magnitude: float | None = None,
        min_mmi: int | None = None,
        max_mmi: int | None = None,
        limit: int | None = None,
    ) -> QuakeResponse:
        """
        Search earthquakes with filtering options.

        This method gets all quakes and applies client-side filtering.
        For server-side MMI filtering, use get_quakes() with mmi parameter.

        Args:
            min_magnitude: Minimum magnitude threshold
            max_magnitude: Maximum magnitude threshold
            min_mmi: Minimum Modified Mercalli Intensity
            max_mmi: Maximum Modified Mercalli Intensity
            limit: Maximum number of results

        Returns:
            QuakeResponse with filtered earthquake features

        Raises:
            GeoNetError: If request fails
        """
        # Get all quakes first
        response = await self.get_quakes()

        # Apply magnitude filters
        if min_magnitude is not None or max_magnitude is not None:
            response.features = response.filter_by_magnitude(
                min_magnitude, max_magnitude
            )

        # Apply MMI filters
        if min_mmi is not None or max_mmi is not None:
            response.features = response.filter_by_mmi(min_mmi, max_mmi)

        # Apply limit
        if limit is not None and limit > 0:
            response.features = response.features[:limit]

        return response

    async def health_check(self) -> bool:
        """
        Check if the GeoNet API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            await self._make_request("")  # Try to get the root endpoint
            return True
        except Exception:
            return False


# Export public API
__all__ = [
    "GeoNetAPIError",
    "GeoNetClient",
    "GeoNetConnectionError",
    "GeoNetError",
    "GeoNetTimeoutError",
]

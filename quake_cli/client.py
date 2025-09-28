"""
Async HTTP client for GeoNet API.

This module provides an async client for interacting with the GeoNet API,
including retry logic with tenacity and comprehensive error handling.
"""

import os
from typing import Any

import httpx
from logerr import Err, Ok, Result
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from quake_cli.models import QuakeFeature, QuakeResponse

# Type aliases for Result types
type QuakeResult = Result[QuakeResponse, str]
type FeatureResult = Result[QuakeFeature, str]
type DataResult = Result[dict[str, Any], str]
type StatsResult = Result[dict[str, Any], str]
type HistoryResult = Result[list[Any], str]


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
    ) -> DataResult:
        """
        Make an HTTP request to the GeoNet API with retry logic.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Result containing JSON response data or error message
        """
        if not self.client:
            return Err("Client not initialized. Use async context manager.")

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

            # Check HTTP status
            if response.status_code >= 400:
                error_msg = f"API returned {response.status_code}: {response.text}"
                logger.error(error_msg)
                return Err(error_msg)

            return Ok(response.json())
        except GeoNetTimeoutError as e:
            logger.error(f"Request timeout: {e!s}")
            return Err(f"Request timed out: {e!s}")
        except GeoNetConnectionError as e:
            logger.error(f"Connection error: {e!s}")
            return Err(f"Connection failed: {e!s}")
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e!s}")
            return Err(f"Unexpected error: {e!s}")

    async def get_quakes(
        self,
        mmi: int | None = None,
        limit: int | None = None,
    ) -> QuakeResult:
        """
        Get earthquake data from GeoNet API.

        Args:
            mmi: Modified Mercalli Intensity filter (-1 to 8, API range)
            limit: Maximum number of results (applied client-side)

        Returns:
            Result containing QuakeResponse or error message
        """
        params: dict[str, Any] = {}

        # MMI parameter is required by the API
        if mmi is not None:
            if not -1 <= mmi <= 8:
                return Err("MMI must be between -1 and 8")
            params["MMI"] = mmi
        else:
            # Default to MMI=-1 to get all earthquakes
            params["MMI"] = -1

        # Make the API request and chain operations
        result = await self._make_request("quake", params)

        def parse_and_limit_response(data: dict[str, Any]) -> QuakeResult:
            try:
                response = QuakeResponse.model_validate(data)
                # Apply client-side limit if specified
                if limit is not None and limit > 0:
                    response.features = response.features[:limit]
                return Ok(response)
            except Exception as e:
                return Err(f"Failed to parse response: {e!s}")

        return result.then(parse_and_limit_response)

    async def get_quake(self, public_id: str) -> FeatureResult:
        """
        Get a specific earthquake by its publicID.

        Args:
            public_id: Unique earthquake identifier

        Returns:
            Result containing QuakeFeature or error message
        """
        # Make the API request and chain operations
        # Trust type system: public_id is typed as str and validated at boundaries
        result = await self._make_request(f"quake/{public_id.strip()}")

        def parse_and_extract_feature(data: dict[str, Any]) -> FeatureResult:
            try:
                response = QuakeResponse.model_validate(data)
                match response.is_empty:
                    case True:
                        return Err(f"Earthquake {public_id} not found")
                    case False:
                        return Ok(response.features[0])
            except Exception as e:
                return Err(f"Failed to parse response: {e!s}")

        return result.then(parse_and_extract_feature)

    async def get_quake_history(self, public_id: str) -> HistoryResult:
        """
        Get location history for a specific earthquake.

        Args:
            public_id: Unique earthquake identifier

        Returns:
            Result containing location history records or error message
        """
        # Make the API request and process data
        # Trust type system: public_id is typed as str and validated at boundaries
        result = await self._make_request(f"quake/history/{public_id.strip()}")

        def normalize_history_data(data: dict[str, Any] | list[Any]) -> HistoryResult:
            history = data if isinstance(data, list) else [data]
            return Ok(history)

        return result.then(normalize_history_data)

    async def get_quake_stats(self) -> StatsResult:
        """
        Get earthquake statistics.

        Returns:
            Result containing earthquake statistics or error message

        Note:
            The exact structure of stats response depends on the API implementation.
            This returns raw data for now until we can verify the actual structure.
        """
        return await self._make_request("quake/stats")

    async def search_quakes(
        self,
        min_magnitude: float | None = None,
        max_magnitude: float | None = None,
        min_mmi: int | None = None,
        max_mmi: int | None = None,
        limit: int | None = None,
    ) -> QuakeResult:
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
            Result containing filtered QuakeResponse or error message
        """
        # Get all quakes first and apply filters
        result = await self.get_quakes()

        def apply_filters(response: QuakeResponse) -> QuakeResult:
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

            return Ok(response)

        return result.then(apply_filters)

    async def health_check(self) -> Result[bool, str]:
        """
        Check if the GeoNet API is accessible.

        Returns:
            Result containing True if API is accessible, error message otherwise
        """
        # Use the quake endpoint with a minimal request for health check
        result = await self._make_request("quake", {"MMI": -1})

        # Use functional approach with .then() for better type safety
        return result.then(lambda _: Ok(True)).map_err(
            lambda error: f"Health check failed: {error}"
        )


# Export public API
__all__ = [
    "DataResult",
    "FeatureResult",
    "GeoNetClient",
    "GeoNetConnectionError",
    "GeoNetError",
    "GeoNetTimeoutError",
    "HistoryResult",
    "QuakeResult",
    "StatsResult",
]

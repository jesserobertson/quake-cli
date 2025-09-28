"""
Async HTTP client for GeoNet API.

This module provides an async client for interacting with the GeoNet API,
including retry logic with tenacity and comprehensive error handling.
"""

import os
from datetime import datetime
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

from gnet.models import cap, intensity, quake, strong_motion, volcano
from gnet.models.common import Point

# Simplified type aliases for commonly used Result patterns
type DataResult = Result[dict[str, Any], str]


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
    ) -> Result[quake.Response, str]:
        """
        Get earthquake data from GeoNet API.

        Args:
            mmi: Modified Mercalli Intensity filter (-1 to 8, API range)
            limit: Maximum number of results (applied client-side)

        Returns:
            Result containing quake.Response or error message
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

        def parse_and_limit_response(data: dict[str, Any]) -> Result[quake.Response, str]:
            try:
                # Parse GeoJSON response and convert to clean structure
                features = []
                for feature_data in data.get("features", []):
                    props = feature_data.get("properties", {})
                    geom = feature_data.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])

                    # Create feature using the clean new structure
                    properties = quake.Properties.from_legacy_api(
                        publicID=props.get("publicID", ""),
                        time=datetime.fromisoformat(props.get("time", "").replace("Z", "+00:00")),
                        magnitude=props.get("magnitude", 0.0),
                        depth=props.get("depth", 0.0),
                        locality=props.get("locality", ""),
                        MMI=props.get("MMI"),
                        quality=props.get("quality", "unknown"),
                        longitude=coords[0],
                        latitude=coords[1],
                    )

                    feature = quake.Feature(
                        properties=properties,
                        geometry=Point(coordinates=coords)
                    )
                    features.append(feature)

                response = quake.Response(features=features)

                # Apply client-side limit if specified
                if limit is not None and limit > 0:
                    response.features = response.features[:limit]
                return Ok(response)
            except Exception as e:
                return Err(f"Failed to parse response: {e!s}")

        return result.then(parse_and_limit_response)

    async def get_quake(self, public_id: str) -> Result[quake.Feature, str]:
        """
        Get a specific earthquake by its publicID.

        Args:
            public_id: Unique earthquake identifier

        Returns:
            Result containing quake.Feature or error message
        """
        # Make the API request and chain operations
        # Trust type system: public_id is typed as str and validated at boundaries
        result = await self._make_request(f"quake/{public_id.strip()}")

        def parse_and_extract_feature(data: dict[str, Any]) -> Result[quake.Feature, str]:
            try:
                # Parse GeoJSON response and convert to clean structure (same as get_quakes)
                features = []
                for feature_data in data.get("features", []):
                    props = feature_data.get("properties", {})
                    geom = feature_data.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])

                    # Create feature using the clean new structure
                    properties = quake.Properties.from_legacy_api(
                        publicID=props.get("publicID", ""),
                        time=datetime.fromisoformat(props.get("time", "").replace("Z", "+00:00")),
                        magnitude=props.get("magnitude", 0.0),
                        depth=props.get("depth", 0.0),
                        locality=props.get("locality", ""),
                        MMI=props.get("MMI"),
                        quality=props.get("quality", "unknown"),
                        longitude=coords[0],
                        latitude=coords[1],
                    )

                    feature = quake.Feature(
                        properties=properties,
                        geometry=Point(coordinates=coords)
                    )
                    features.append(feature)

                if not features:
                    return Err(f"Earthquake {public_id} not found")

                return Ok(features[0])
            except Exception as e:
                return Err(f"Failed to parse response: {e!s}")

        return result.then(parse_and_extract_feature)

    async def get_quake_history(self, public_id: str) -> Result[list[Any], str]:
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

        def normalize_history_data(data: dict[str, Any] | list[Any]) -> Result[list[Any], str]:
            history = data if isinstance(data, list) else [data]
            return Ok(history)

        return result.then(normalize_history_data)

    async def get_quake_stats(self) -> Result[dict[str, Any], str]:
        """
        Get earthquake statistics.

        Returns:
            Result containing earthquake statistics or error message

        Note:
            The stats endpoint requires regular JSON, not geo+json format.
        """
        if not self.client:
            return Err("Client not initialized. Use async context manager.")

        @self._create_retry_decorator()  # type: ignore[misc]
        async def _request() -> httpx.Response:
            try:
                assert self.client is not None  # For mypy
                # Stats endpoint needs regular JSON headers, not geo+json
                response = await self.client.get(
                    "quake/stats", headers={"Accept": "application/json;version=2"}
                )
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

    async def search_quakes(
        self,
        min_magnitude: float | None = None,
        max_magnitude: float | None = None,
        min_mmi: int | None = None,
        max_mmi: int | None = None,
        limit: int | None = None,
    ) -> Result[quake.Response, str]:
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
            Result containing filtered quake.Response or error message
        """
        # Get all quakes first and apply filters
        result = await self.get_quakes()

        def apply_filters(response: quake.Response) -> Result[quake.Response, str]:
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

    async def get_intensity(
        self,
        intensity_type: str,
        publicid: str | None = None,
        aggregation: str | None = None,
    ) -> Result[intensity.Response, str]:
        """
        Get earthquake intensity data.

        Args:
            intensity_type: Type of intensity data ('reported' or 'measured')
            publicid: Optional earthquake public ID
            aggregation: Optional aggregation method for reported data ('max' or 'median')

        Returns:
            Result containing intensity.Response or error message
        """
        params: dict[str, Any] = {"type": intensity_type}

        if publicid:
            params["publicID"] = publicid.strip()

        if aggregation and intensity_type == "reported":
            params["aggregation"] = aggregation

        result = await self._make_request("intensity", params)

        def parse_intensity_response(data: dict[str, Any]) -> Result[intensity.Response, str]:
            try:
                # Parse GeoJSON response and convert to clean structure
                features = []
                for feature_data in data.get("features", []):
                    props = feature_data.get("properties", {})
                    geom = feature_data.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])

                    # Create feature using the clean new structure
                    properties = intensity.Properties.from_legacy(
                        mmi=props.get("mmi", 0),
                        count=props.get("count"),
                        longitude=coords[0],
                        latitude=coords[1],
                    )

                    feature = intensity.Feature(
                        properties=properties,
                        geometry=Point(coordinates=coords)
                    )
                    features.append(feature)

                response = intensity.Response(
                    features=features,
                    count_mmi=data.get("count_mmi")
                )
                return Ok(response)
            except Exception as e:
                return Err(f"Failed to parse intensity response: {e!s}")

        return result.then(parse_intensity_response)

    async def get_volcano_alerts(
        self, volcano_id: str | None = None
    ) -> Result[volcano.Response, str]:
        """
        Get volcanic alert levels.

        Args:
            volcano_id: Optional specific volcano ID to filter by

        Returns:
            Result containing volcano.Response or error message
        """
        result = await self._make_request("volcano/val")

        def parse_and_filter_alerts(data: dict[str, Any]) -> Result[volcano.Response, str]:
            try:
                # Parse GeoJSON response and convert to clean structure
                features = []
                for feature_data in data.get("features", []):
                    props = feature_data.get("properties", {})
                    geom = feature_data.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])

                    # Create feature using the clean new structure
                    properties = volcano.Properties.from_legacy_api(
                        volcanoID=props.get("volcanoID", ""),
                        volcanoTitle=props.get("volcanoTitle", ""),
                        level=props.get("level", 0),
                        acc=props.get("acc", ""),
                        activity=props.get("activity", ""),
                        hazards=props.get("hazards", ""),
                        longitude=coords[0],
                        latitude=coords[1],
                    )

                    feature = volcano.Feature(
                        properties=properties,
                        geometry=Point(coordinates=coords)
                    )
                    features.append(feature)

                response = volcano.Response(features=features)

                # Filter by volcano ID if specified
                if volcano_id:
                    filtered_features = [
                        f for f in response.features
                        if f.properties.id.upper() == volcano_id.upper()
                    ]
                    response.features = filtered_features

                return Ok(response)
            except Exception as e:
                return Err(f"Failed to parse volcano alerts response: {e!s}")

        return result.then(parse_and_filter_alerts)

    async def get_volcano_quakes(
        self,
        volcano_id: str | None = None,
        limit: int | None = None,
        min_magnitude: float | None = None,
    ) -> Result[volcano.quake.Response, str]:
        """
        Get earthquakes near volcanoes.

        Args:
            volcano_id: Optional specific volcano ID to filter by
            limit: Maximum number of results
            min_magnitude: Minimum magnitude threshold

        Returns:
            Result containing volcano.quake.Response or error message
        """
        # The volcano/quake endpoint requires a volcanoID parameter
        if not volcano_id:
            return Ok(volcano.quake.Response(features=[]))

        params: dict[str, Any] = {"volcanoID": volcano_id}
        result = await self._make_request("volcano/quake", params)

        def parse_and_filter_volcano_quakes(data: dict[str, Any]) -> Result[volcano.quake.Response, str]:
            try:
                response = volcano.quake.Response.model_validate(data)

                # Apply magnitude filter
                if min_magnitude is not None:
                    filtered_features = [
                        f for f in response.features
                        if f.properties.magnitude >= min_magnitude
                    ]
                    response.features = filtered_features

                # Apply limit
                if limit is not None and limit > 0:
                    response.features = response.features[:limit]

                return Ok(response)
            except Exception as e:
                return Err(f"Failed to parse volcano quakes response: {e!s}")

        return result.then(parse_and_filter_volcano_quakes)

    async def get_cap_feed(self) -> Result[cap.CapFeed, str]:
        """
        Get CAP (Common Alerting Protocol) feed of recent significant earthquakes.

        Returns:
            Result containing cap.CapFeed or error message
        """
        if not self.client:
            return Err("Client not initialized. Use async context manager.")

        @self._create_retry_decorator()  # type: ignore[misc]
        async def _request() -> httpx.Response:
            try:
                assert self.client is not None  # For mypy
                # CAP feed is XML format, not JSON
                response = await self.client.get(
                    "cap/1.2/GPA1.0/feed/atom1.0/quake",
                    headers={"Accept": "application/atom+xml, application/xml, text/xml"}
                )
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

            # Parse XML response
            try:
                import xml.etree.ElementTree as ET

                root = ET.fromstring(response.text)

                # Extract namespace
                ns = {"atom": "http://www.w3.org/2005/Atom"}

                # Build feed data structure
                feed_data = {
                    "feed": {
                        "id": getattr(root.find("atom:id", ns), "text", ""),
                        "title": getattr(root.find("atom:title", ns), "text", ""),
                        "updated": getattr(root.find("atom:updated", ns), "text", ""),
                        "author": {},
                        "entry": []
                    }
                }

                # Parse author
                author_elem = root.find("atom:author", ns)
                if author_elem is not None:
                    author_name = author_elem.find("atom:name", ns)
                    author_email = author_elem.find("atom:email", ns)
                    author_uri = author_elem.find("atom:uri", ns)

                    feed_data["feed"]["author"] = {
                        "name": getattr(author_name, "text", None),
                        "email": getattr(author_email, "text", None),
                        "uri": getattr(author_uri, "text", None),
                    }

                # Parse entries
                entries = root.findall("atom:entry", ns)
                for entry in entries:
                    entry_data = {
                        "id": getattr(entry.find("atom:id", ns), "text", ""),
                        "title": getattr(entry.find("atom:title", ns), "text", ""),
                        "updated": getattr(entry.find("atom:updated", ns), "text", ""),
                        "published": getattr(entry.find("atom:published", ns), "text", ""),
                        "summary": getattr(entry.find("atom:summary", ns), "text", None),
                    }

                    # Parse link
                    link_elem = entry.find("atom:link", ns)
                    if link_elem is not None:
                        entry_data["link"] = {"@href": link_elem.get("href")}

                    # Parse author
                    entry_author = entry.find("atom:author", ns)
                    if entry_author is not None:
                        entry_author_name = entry_author.find("atom:name", ns)
                        if entry_author_name is not None:
                            entry_data["author"] = {"name": entry_author_name.text}

                    feed_data["feed"]["entry"].append(entry_data)

                cap_feed = cap.CapFeed.from_atom_feed(feed_data)
                return Ok(cap_feed)

            except Exception as e:
                return Err(f"Failed to parse CAP feed XML: {e!s}")

        except GeoNetTimeoutError as e:
            logger.error(f"Request timeout: {e!s}")
            return Err(f"Request timed out: {e!s}")
        except GeoNetConnectionError as e:
            logger.error(f"Connection error: {e!s}")
            return Err(f"Connection failed: {e!s}")
        except Exception as e:
            logger.error(f"Unexpected error in CAP feed request: {e!s}")
            return Err(f"Unexpected error: {e!s}")

    async def get_cap_alert(self, cap_id: str) -> Result[str, str]:
        """
        Get individual CAP alert document for a specific earthquake.

        Args:
            cap_id: CAP alert identifier

        Returns:
            Result containing raw CAP XML content or error message

        Note:
            Returns raw XML as the CAP format is complex and primarily consumed by
            automated systems. Use get_cap_feed() for parsed feed entries.
        """
        if not self.client:
            return Err("Client not initialized. Use async context manager.")

        @self._create_retry_decorator()  # type: ignore[misc]
        async def _request() -> httpx.Response:
            try:
                assert self.client is not None  # For mypy
                # CAP alert is XML format
                response = await self.client.get(
                    f"cap/1.2/GPA1.0/quake/{cap_id.strip()}",
                    headers={"Accept": "application/xml, text/xml"}
                )
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

            # Return raw XML for CAP documents
            return Ok(response.text)

        except GeoNetTimeoutError as e:
            logger.error(f"Request timeout: {e!s}")
            return Err(f"Request timed out: {e!s}")
        except GeoNetConnectionError as e:
            logger.error(f"Connection error: {e!s}")
            return Err(f"Connection failed: {e!s}")
        except Exception as e:
            logger.error(f"Unexpected error in CAP alert request: {e!s}")
            return Err(f"Unexpected error: {e!s}")

    async def get_strong_motion(self, public_id: str) -> Result[strong_motion.Response, str]:
        """
        Get strong motion data for a specific earthquake.

        Args:
            public_id: Earthquake public ID

        Returns:
            Result containing strong_motion.Response or error message
        """
        if not self.client:
            return Err("Client not initialized. Use async context manager.")

        @self._create_retry_decorator()  # type: ignore[misc]
        async def _request() -> httpx.Response:
            try:
                assert self.client is not None  # For mypy
                # Strong motion endpoint uses standard JSON format
                response = await self.client.get(
                    f"intensity/strong/processed/{public_id.strip()}",
                    headers={"Accept": "application/json"}
                )
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

            # Parse JSON response
            try:
                data = response.json()

                # Extract metadata
                metadata_data = data.get("metadata", {})
                metadata = strong_motion.Metadata.from_legacy_api(
                    author=metadata_data.get("author"),
                    depth=metadata_data.get("depth"),
                    description=metadata_data.get("description"),
                    latitude=metadata_data.get("latitude"),
                    longitude=metadata_data.get("longitude"),
                    magnitude=metadata_data.get("magnitude"),
                    version=metadata_data.get("version"),
                )

                # Parse station features
                features = []
                for feature_data in data.get("features", []):
                    props = feature_data.get("properties", {})
                    geom = feature_data.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])

                    # Create station properties
                    station_props = strong_motion.StationProperties.from_legacy_api(
                        station=props.get("station", ""),
                        network=props.get("network", ""),
                        location=props.get("location", ""),
                        distance=props.get("distance"),
                        mmi=props.get("mmi"),
                        pga_horizontal=props.get("pga_horizontal"),
                        pga_vertical=props.get("pga_vertical"),
                        pgv_horizontal=props.get("pgv_horizontal"),
                        pgv_vertical=props.get("pgv_vertical"),
                    )

                    feature = strong_motion.StationFeature(
                        id=feature_data.get("id", ""),
                        properties=station_props,
                        geometry=Point(coordinates=coords)
                    )
                    features.append(feature)

                strong_motion_response = strong_motion.Response(
                    metadata=metadata,
                    features=features
                )
                return Ok(strong_motion_response)

            except Exception as e:
                return Err(f"Failed to parse strong motion response: {e!s}")

        except GeoNetTimeoutError as e:
            logger.error(f"Request timeout: {e!s}")
            return Err(f"Request timed out: {e!s}")
        except GeoNetConnectionError as e:
            logger.error(f"Connection error: {e!s}")
            return Err(f"Connection failed: {e!s}")
        except Exception as e:
            logger.error(f"Unexpected error in strong motion request: {e!s}")
            return Err(f"Unexpected error: {e!s}")


# Export public API
__all__ = [
    "DataResult",
    "GeoNetClient",
    "GeoNetConnectionError",
    "GeoNetError",
    "GeoNetTimeoutError",
]

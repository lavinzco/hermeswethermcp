"""Dependency-injectable shared HTTP client infrastructure."""

import asyncio
import logging
import time
from collections.abc import Callable, Mapping
from typing import TypeAlias

import httpx

from weather_mcp.infrastructure.http.exceptions import (
    HTTPError,
    NetworkError,
    ResponseDecodeError,
)
from weather_mcp.infrastructure.http.middleware import RateLimitPolicy, TimeoutPolicy
from weather_mcp.infrastructure.http.retry import RetryPolicy

JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
Headers: TypeAlias = Mapping[str, str]
ClientFactory: TypeAlias = Callable[..., httpx.AsyncClient]


class HTTPClient:
    """Shared async HTTP client for future weather providers.

    Providers should depend on this abstraction instead of constructing their own
    transport clients directly.
    """

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        client_factory: ClientFactory = httpx.AsyncClient,
        retry_policy: RetryPolicy | None = None,
        timeout_policy: TimeoutPolicy | None = None,
        rate_limit_policy: RateLimitPolicy | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._retry_policy = retry_policy or RetryPolicy()
        self._timeout_policy = timeout_policy or TimeoutPolicy()
        self._rate_limit_policy = rate_limit_policy or RateLimitPolicy()
        self._logger = logger or logging.getLogger(__name__)
        self._client_owned = client is None
        self._client = client or client_factory(
            timeout=self._timeout_policy.to_httpx_timeout(),
        )
        self._rate_limit_lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the owned HTTP transport client."""

        if self._client_owned:
            await self._client.aclose()

    async def get(
        self,
        url: str,
        *,
        headers: Headers | None = None,
        timeout: httpx.Timeout | float | None = None,
    ) -> JSONValue:
        """Send a GET request and decode the JSON response."""

        return await self.request("GET", url, headers=headers, timeout=timeout)

    async def post(
        self,
        url: str,
        *,
        json: JSONValue | None = None,
        headers: Headers | None = None,
        timeout: httpx.Timeout | float | None = None,
    ) -> JSONValue:
        """Send a POST request with an optional JSON body and decode JSON response."""

        return await self.request(
            "POST",
            url,
            json=json,
            headers=headers,
            timeout=timeout,
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: JSONValue | None = None,
        headers: Headers | None = None,
        timeout: httpx.Timeout | float | None = None,
    ) -> JSONValue:
        """Send an HTTP request with retry, timeout, rate-limit, and logging support."""

        last_network_error: NetworkError | None = None
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            await self._apply_rate_limit()
            await self._sleep_before_retry(attempt)
            self._logger.debug(
                "Sending HTTP request",
                extra={"method": method, "url": url, "attempt": attempt},
            )
            try:
                response = await self._client.request(
                    method,
                    url,
                    json=json,
                    headers=headers,
                    timeout=timeout,
                )
            except httpx.TransportError as exc:
                last_network_error = NetworkError(str(exc))
                if attempt == self._retry_policy.max_attempts:
                    raise last_network_error from exc
                continue

            if self._retry_policy.should_retry_status(response.status_code):
                if attempt == self._retry_policy.max_attempts:
                    self._raise_http_error(response)
                continue

            if response.is_error:
                self._raise_http_error(response)

            return self._decode_json(response)

        if last_network_error is not None:
            raise last_network_error
        msg = "HTTP request failed after retries"
        raise NetworkError(msg)

    async def _apply_rate_limit(self) -> None:
        interval = self._rate_limit_policy.min_interval_seconds
        if interval == 0:
            return

        async with self._rate_limit_lock:
            elapsed = time.monotonic() - self._last_request_at
            sleep_seconds = interval - elapsed
            if sleep_seconds > 0:
                await asyncio.sleep(sleep_seconds)
            self._last_request_at = time.monotonic()

    async def _sleep_before_retry(self, attempt: int) -> None:
        delay = self._retry_policy.delay_for_attempt(attempt)
        if delay > 0:
            await asyncio.sleep(delay)

    def _decode_json(self, response: httpx.Response) -> JSONValue:
        try:
            decoded = response.json()
        except ValueError as exc:
            msg = "HTTP response body could not be decoded as JSON"
            raise ResponseDecodeError(msg) from exc
        return decoded  # type: ignore[no-any-return]

    def _raise_http_error(self, response: httpx.Response) -> None:
        msg = f"HTTP request failed with status {response.status_code}"
        raise HTTPError(
            status_code=response.status_code,
            message=msg,
            response_text=response.text,
        )

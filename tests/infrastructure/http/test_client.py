"""Unit tests for shared HTTP client infrastructure."""

import asyncio
import logging
from collections.abc import Coroutine
from typing import TypeVar

import httpx
import pytest

from weather_mcp.infrastructure.http import (
    HTTPClient,
    HTTPError,
    NetworkError,
    RateLimitPolicy,
    ResponseDecodeError,
    RetryPolicy,
    TimeoutPolicy,
)

T = TypeVar("T")


def run_async(coro: Coroutine[object, object, T]) -> T:
    """Run an async test coroutine without requiring pytest plugins."""

    return asyncio.run(coro)


def make_client(handler: httpx.MockTransport) -> httpx.AsyncClient:
    """Create an injected async client using a mock transport."""

    return httpx.AsyncClient(transport=handler, base_url="https://example.test")


def test_get_decodes_json_response() -> None:
    """GET requests decode JSON responses."""

    async def scenario() -> None:
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json={"ok": True}),
        )
        async with make_client(transport) as injected_client:
            client = HTTPClient(client=injected_client)

            result = await client.get(
                "/weather",
                headers={"Accept": "application/json"},
            )

            assert result == {"ok": True}

    run_async(scenario())


def test_post_sends_json_body_and_headers() -> None:
    """POST requests send JSON payloads and headers through injected client."""

    captured: dict[str, str] = {}

    async def scenario() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            captured["content_type"] = request.headers["content-type"]
            captured["body"] = request.content.decode()
            return httpx.Response(200, json={"created": True})

        async with make_client(httpx.MockTransport(handler)) as injected_client:
            client = HTTPClient(client=injected_client)

            result = await client.post(
                "/weather",
                json={"station": "WSSS"},
                headers={"X-Test": "1"},
            )

            assert result == {"created": True}
            assert captured == {
                "method": "POST",
                "content_type": "application/json",
                "body": '{"station":"WSSS"}',
            }

    run_async(scenario())


def test_retries_retryable_status_before_success() -> None:
    """Retry policy retries retryable status codes before returning success."""

    calls = [0]

    async def scenario() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            del request
            calls[0] += 1
            if calls[0] == 1:
                return httpx.Response(503, json={"error": "temporary"})
            return httpx.Response(200, json={"ok": True})

        async with make_client(httpx.MockTransport(handler)) as injected_client:
            client = HTTPClient(
                client=injected_client,
                retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=0),
            )

            result = await client.get("/weather")

            assert result == {"ok": True}
            assert calls[0] == 2

    run_async(scenario())


def test_raises_http_error_after_retry_exhaustion() -> None:
    """HTTPError is raised after retry attempts are exhausted."""

    async def scenario() -> None:
        transport = httpx.MockTransport(
            lambda request: httpx.Response(503, text="nope"),
        )
        async with make_client(transport) as injected_client:
            client = HTTPClient(
                client=injected_client,
                retry_policy=RetryPolicy(max_attempts=1),
            )

            with pytest.raises(HTTPError) as exc_info:
                await client.get("/weather")

            assert exc_info.value.status_code == 503
            assert exc_info.value.response_text == "nope"

    run_async(scenario())


def test_raises_network_error_for_transport_failure() -> None:
    """Transport failures are normalized to NetworkError."""

    async def scenario() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("boom", request=request)

        async with make_client(httpx.MockTransport(handler)) as injected_client:
            client = HTTPClient(
                client=injected_client,
                retry_policy=RetryPolicy(max_attempts=1),
            )

            with pytest.raises(NetworkError):
                await client.get("/weather")

    run_async(scenario())


def test_raises_decode_error_for_invalid_json() -> None:
    """Invalid JSON responses are normalized to ResponseDecodeError."""

    async def scenario() -> None:
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, text="no-json"),
        )
        async with make_client(transport) as injected_client:
            client = HTTPClient(client=injected_client)

            with pytest.raises(ResponseDecodeError):
                await client.get("/weather")

    run_async(scenario())


def test_policy_validation() -> None:
    """HTTP policies validate invalid configuration values."""

    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        TimeoutPolicy(connect_seconds=0)
    with pytest.raises(ValueError):
        RateLimitPolicy(requests_per_second=0)


def test_logging_receives_request_context(caplog: pytest.LogCaptureFixture) -> None:
    """HTTPClient emits debug logging with request context."""

    async def scenario() -> None:
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json={"ok": True}),
        )
        async with make_client(transport) as injected_client:
            logger = logging.getLogger("tests.http")
            client = HTTPClient(client=injected_client, logger=logger)

            with caplog.at_level(logging.DEBUG, logger="tests.http"):
                await client.get("/weather")

            assert "Sending HTTP request" in caplog.text

    run_async(scenario())

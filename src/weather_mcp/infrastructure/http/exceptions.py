"""HTTP infrastructure exception hierarchy."""


class HTTPClientError(Exception):
    """Base exception for HTTP client failures."""


class NetworkError(HTTPClientError):
    """Raised when a network transport failure occurs."""


class HTTPError(HTTPClientError):
    """Raised when an HTTP response has an unsuccessful status code."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class RetryableError(HTTPClientError):
    """Raised when a request failure is eligible for retry."""


class ResponseDecodeError(HTTPClientError):
    """Raised when an HTTP response body cannot be decoded as JSON."""

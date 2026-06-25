"""Retry policy definitions for shared HTTP infrastructure."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Immutable retry policy for transient HTTP failures."""

    max_attempts: int = 3
    backoff_seconds: float = 0.25
    retryable_status_codes: tuple[int, ...] = (408, 429, 500, 502, 503, 504)

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            msg = "max_attempts must be greater than or equal to 1"
            raise ValueError(msg)
        if self.backoff_seconds < 0:
            msg = "backoff_seconds must be greater than or equal to 0"
            raise ValueError(msg)

    def should_retry_status(self, status_code: int) -> bool:
        """Return whether a status code is retryable."""

        return status_code in self.retryable_status_codes

    def delay_for_attempt(self, attempt: int) -> float:
        """Return exponential backoff delay for an attempt number."""

        if attempt <= 1:
            return 0.0
        return float(self.backoff_seconds * (2 ** (attempt - 2)))

"""HTTP policy helpers used by the shared client."""

from dataclasses import dataclass

import httpx


@dataclass(frozen=True, slots=True)
class TimeoutPolicy:
    """Immutable timeout policy for HTTP requests."""

    connect_seconds: float = 5.0
    read_seconds: float = 10.0
    write_seconds: float = 10.0
    pool_seconds: float = 5.0

    def __post_init__(self) -> None:
        values = (
            self.connect_seconds,
            self.read_seconds,
            self.write_seconds,
            self.pool_seconds,
        )
        if any(value <= 0 for value in values):
            msg = "timeout values must be greater than 0"
            raise ValueError(msg)

    def to_httpx_timeout(self) -> httpx.Timeout:
        """Convert policy values to an httpx timeout object."""

        return httpx.Timeout(
            connect=self.connect_seconds,
            read=self.read_seconds,
            write=self.write_seconds,
            pool=self.pool_seconds,
        )


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    """Immutable rate-limit policy for shared outbound HTTP access."""

    requests_per_second: float | None = None

    def __post_init__(self) -> None:
        if self.requests_per_second is not None and self.requests_per_second <= 0:
            msg = "requests_per_second must be greater than 0 when configured"
            raise ValueError(msg)

    @property
    def min_interval_seconds(self) -> float:
        """Return minimum seconds between requests for this policy."""

        if self.requests_per_second is None:
            return 0.0
        return 1.0 / self.requests_per_second

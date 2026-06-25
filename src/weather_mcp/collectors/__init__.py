"""Collector framework public API."""

from weather_mcp.collectors.base import (
    BaseCollector,
    CollectorIdentity,
    CollectorProtocol,
)
from weather_mcp.collectors.exceptions import (
    CollectorError,
    CollectorTimeout,
    CollectorUnavailable,
    InvalidObservation,
)
from weather_mcp.collectors.registry import CollectorRegistry

__all__ = [
    "BaseCollector",
    "CollectorError",
    "CollectorIdentity",
    "CollectorProtocol",
    "CollectorRegistry",
    "CollectorTimeout",
    "CollectorUnavailable",
    "InvalidObservation",
]

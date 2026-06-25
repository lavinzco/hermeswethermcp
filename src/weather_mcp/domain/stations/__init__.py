"""Airport station domain API."""

from weather_mcp.domain.stations.airport import Airport
from weather_mcp.domain.stations.registry import (
    DEFAULT_AIRPORTS,
    DEFAULT_STATION_REGISTRY,
    StationRegistry,
    StationRegistryError,
)

__all__ = [
    "DEFAULT_AIRPORTS",
    "DEFAULT_STATION_REGISTRY",
    "Airport",
    "StationRegistry",
    "StationRegistryError",
]

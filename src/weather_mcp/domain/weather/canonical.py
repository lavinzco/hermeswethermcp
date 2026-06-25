"""Canonical weather model definitions."""

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from weather_mcp.domain.value_objects import (
    Humidity,
    ObservationTime,
    Pressure,
    Station,
    Temperature,
)
from weather_mcp.domain.weather.enums import ObservationType
from weather_mcp.domain.weather.quality import DataQuality
from weather_mcp.domain.weather.source import WeatherSource

Metadata = Mapping[str, Any]


class WeatherCanonical(BaseModel):
    """Immutable canonical weather observation model."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    station: Station
    source: WeatherSource
    observation_time: ObservationTime
    observation_type: ObservationType = ObservationType.OBSERVATION
    temperature: Temperature | None = None
    humidity: Humidity | None = None
    pressure: Pressure | None = None
    dewpoint: Temperature | None = None
    wind_speed: Decimal | None = Field(default=None, ge=Decimal("0"))
    wind_direction: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("360"),
    )
    visibility: Decimal | None = Field(default=None, ge=Decimal("0"))
    cloud_cover: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
    )
    precipitation: Decimal | None = Field(default=None, ge=Decimal("0"))
    quality: DataQuality
    metadata: Metadata = Field(default_factory=lambda: MappingProxyType({}))

    @field_validator("metadata", mode="before")
    @classmethod
    def freeze_metadata(cls, value: object) -> Metadata:
        """Convert metadata mappings to an immutable mapping proxy."""

        if isinstance(value, MappingProxyType):
            return value
        if isinstance(value, Mapping):
            return MappingProxyType(dict(value))
        msg = "metadata must be a mapping"
        raise TypeError(msg)

"""Consensus weather entity definitions."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from weather_mcp.domain.value_objects import (
    Humidity,
    ObservationTime,
    Pressure,
    Station,
    Temperature,
)


class ConsensusWeather(BaseModel):
    """Immutable consensus weather observation across collector sources."""

    model_config = ConfigDict(frozen=True)

    station: Station
    observation_time: ObservationTime
    temperature: Temperature | None = None
    humidity: Humidity | None = None
    pressure: Pressure | None = None
    confidence: Decimal | None = Field(default=None, ge=Decimal("0"), le=Decimal("1"))
    sources: tuple[str, ...] = Field(default_factory=tuple)

"""Weather observation entity definitions."""

from pydantic import BaseModel, ConfigDict, Field

from weather_mcp.domain.value_objects import (
    Humidity,
    ObservationTime,
    Pressure,
    Station,
    Temperature,
)


class WeatherObservation(BaseModel):
    """Immutable weather observation from a single collector source."""

    model_config = ConfigDict(frozen=True)

    station: Station
    observation_time: ObservationTime
    temperature: Temperature | None = None
    humidity: Humidity | None = None
    pressure: Pressure | None = None
    source: str = Field(min_length=1)

"""Station value object definitions."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StationCodeSystem(StrEnum):
    """Supported weather station code systems."""

    ICAO = "ICAO"
    IATA = "IATA"


class Station(BaseModel):
    """Immutable weather station identifier."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    code: str = Field(min_length=3, max_length=4, pattern=r"^[A-Z0-9]+$")
    code_system: StationCodeSystem = StationCodeSystem.ICAO

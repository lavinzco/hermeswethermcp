"""Temperature value object definitions."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TemperatureUnit(StrEnum):
    """Supported temperature units."""

    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class Temperature(BaseModel):
    """Immutable temperature measurement."""

    model_config = ConfigDict(frozen=True)

    value: Decimal = Field(description="Temperature numeric value.")
    unit: TemperatureUnit = TemperatureUnit.CELSIUS

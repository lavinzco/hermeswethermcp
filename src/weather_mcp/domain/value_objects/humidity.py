"""Humidity value object definitions."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Humidity(BaseModel):
    """Immutable relative humidity measurement."""

    model_config = ConfigDict(frozen=True)

    percent: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))

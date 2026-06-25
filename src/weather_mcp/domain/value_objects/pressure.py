"""Pressure value object definitions."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Pressure(BaseModel):
    """Immutable atmospheric pressure measurement."""

    model_config = ConfigDict(frozen=True)

    hpa: Decimal = Field(gt=Decimal("0"))

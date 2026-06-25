"""Canonical weather data quality model."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DataQuality(BaseModel):
    """Immutable quality signals for canonical weather data."""

    model_config = ConfigDict(frozen=True)

    score: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    official: bool = False
    estimated: bool = False
    latency_seconds: int | None = Field(default=None, ge=0)
    agreement: Decimal | None = Field(default=None, ge=Decimal("0"), le=Decimal("1"))

"""Observation time value object definitions."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ObservationTime(BaseModel):
    """Immutable UTC observation timestamp."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def normalize_to_utc(cls, value: datetime) -> datetime:
        """Normalize timezone-aware and naive datetimes to UTC."""

        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

"""Unit tests for canonical weather domain models."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from weather_mcp.domain.value_objects import ObservationTime, Station, Temperature
from weather_mcp.domain.weather import (
    DataQuality,
    ObservationType,
    WeatherCanonical,
    WeatherSource,
)


def test_weather_source_supports_required_sources() -> None:
    """WeatherSource contains every required upstream source name."""

    assert {source.value for source in WeatherSource} == {
        "CheckWX",
        "DWD",
        "JMA",
        "KMA",
        "NOAA",
        "OpenMeteo",
        "SingaporeGov",
        "WeatherUnderground",
    }


def test_data_quality_validates_score_bounds() -> None:
    """DataQuality enforces normalized score boundaries."""

    with pytest.raises(ValidationError):
        DataQuality(score=Decimal("1.1"))


def test_weather_canonical_is_immutable_and_uses_value_objects() -> None:
    """WeatherCanonical is immutable and stores canonical value objects."""

    canonical = WeatherCanonical(
        station=Station(code="WSSS"),
        source=WeatherSource.SINGAPORE_GOV,
        observation_time=ObservationTime(observed_at=datetime(2026, 1, 1, tzinfo=UTC)),
        observation_type=ObservationType.OBSERVATION,
        temperature=Temperature(value=Decimal("28.3")),
        dewpoint=Temperature(value=Decimal("24.1")),
        quality=DataQuality(score=Decimal("1"), official=True),
        metadata={"provider_station": "WSSS"},
    )

    assert canonical.station.code == "WSSS"
    assert canonical.temperature is not None
    assert canonical.temperature.value == Decimal("28.3")
    assert canonical.metadata["provider_station"] == "WSSS"

    with pytest.raises(ValidationError):
        canonical.source = WeatherSource.NOAA

    with pytest.raises(TypeError):
        canonical.metadata["provider_station"] = "RJTT"


def test_weather_canonical_validates_physical_bounds() -> None:
    """WeatherCanonical validates canonical weather field boundaries."""

    with pytest.raises(ValidationError):
        WeatherCanonical(
            station=Station(code="RJTT"),
            source=WeatherSource.JMA,
            observation_time=ObservationTime(
                observed_at=datetime(2026, 1, 1, tzinfo=UTC),
            ),
            wind_direction=Decimal("361"),
            cloud_cover=Decimal("101"),
            quality=DataQuality(score=Decimal("0.9")),
        )

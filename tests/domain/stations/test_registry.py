"""Unit tests for airport station registry domain behavior."""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest
from pydantic import ValidationError

from weather_mcp.domain.stations import (
    DEFAULT_AIRPORTS,
    DEFAULT_STATION_REGISTRY,
    Airport,
    StationRegistry,
    StationRegistryError,
)


def test_default_registry_contains_required_airports() -> None:
    """Default registry contains all required ICAO stations."""

    assert {airport.icao for airport in DEFAULT_STATION_REGISTRY.list()} == {
        "EDDM",
        "EFHK",
        "EPWA",
        "LTAC",
        "RJTT",
        "RKSI",
        "WSSS",
    }


def test_get_by_icao_returns_airport() -> None:
    """Airports can be retrieved by ICAO code."""

    airport = DEFAULT_STATION_REGISTRY.get_by_icao("WSSS")

    assert airport is not None
    assert airport.iata == "SIN"
    assert airport.name == "Singapore Changi Airport"


def test_get_by_iata_returns_airport() -> None:
    """Airports can be retrieved by IATA code."""

    airport = DEFAULT_STATION_REGISTRY.get_by_iata("HND")

    assert airport is not None
    assert airport.icao == "RJTT"
    assert airport.country == "Japan"


def test_list_returns_airports_sorted_by_icao() -> None:
    """Registry list output is stable and sorted by ICAO code."""

    icao_codes = [airport.icao for airport in DEFAULT_STATION_REGISTRY.list()]

    assert icao_codes == sorted(icao_codes)


def test_register_returns_new_registry_without_mutating_original() -> None:
    """Registering an airport preserves registry immutability."""

    airport = Airport(
        icao="TEST",
        iata="TST",
        name="Test Airport",
        country="Testland",
        timezone="Etc/UTC",
        latitude=Decimal("0"),
        longitude=Decimal("0"),
        elevation_meters=0,
    )
    original = StationRegistry.empty()

    updated = original.register(airport)

    assert original.get_by_icao("TEST") is None
    assert updated.get_by_icao("TEST") == airport
    assert updated.get_by_iata("TST") == airport


def test_register_rejects_duplicate_icao() -> None:
    """Registry rejects duplicate ICAO codes."""

    registry = StationRegistry.empty().register(DEFAULT_AIRPORTS[0])

    with pytest.raises(StationRegistryError, match="ICAO already registered"):
        registry.register(DEFAULT_AIRPORTS[0])


def test_register_rejects_duplicate_iata() -> None:
    """Registry rejects duplicate IATA codes."""

    registry = StationRegistry.empty().register(DEFAULT_AIRPORTS[0])
    duplicate_iata = DEFAULT_AIRPORTS[0].model_copy(update={"icao": "ZZZZ"})

    with pytest.raises(StationRegistryError, match="IATA already registered"):
        registry.register(duplicate_iata)


def test_airport_entity_is_immutable() -> None:
    """Airport entities are immutable Pydantic models."""

    airport = DEFAULT_AIRPORTS[0]

    with pytest.raises(ValidationError):
        airport.name = "Changed Airport"


def test_registry_object_is_immutable() -> None:
    """Station registry objects are immutable dataclasses."""

    with pytest.raises(FrozenInstanceError):
        DEFAULT_STATION_REGISTRY._by_icao = {}


def test_airport_validates_codes_and_coordinates() -> None:
    """Airport entity validates code and coordinate boundaries."""

    with pytest.raises(ValidationError):
        Airport(
            icao="BAD",
            iata="TOOLONG",
            name="Invalid Airport",
            country="Nowhere",
            timezone="Etc/UTC",
            latitude=Decimal("91"),
            longitude=Decimal("181"),
            elevation_meters=0,
        )

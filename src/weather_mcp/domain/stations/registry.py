"""Immutable airport station registry."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType

from weather_mcp.domain.stations.airport import Airport


class StationRegistryError(ValueError):
    """Raised when an airport station registry operation is invalid."""


DEFAULT_AIRPORTS: tuple[Airport, ...] = (
    Airport(
        icao="WSSS",
        iata="SIN",
        name="Singapore Changi Airport",
        country="Singapore",
        timezone="Asia/Singapore",
        latitude=Decimal("1.3644"),
        longitude=Decimal("103.9915"),
        elevation_meters=7,
    ),
    Airport(
        icao="RJTT",
        iata="HND",
        name="Tokyo Haneda Airport",
        country="Japan",
        timezone="Asia/Tokyo",
        latitude=Decimal("35.5494"),
        longitude=Decimal("139.7798"),
        elevation_meters=6,
    ),
    Airport(
        icao="RKSI",
        iata="ICN",
        name="Incheon International Airport",
        country="South Korea",
        timezone="Asia/Seoul",
        latitude=Decimal("37.4602"),
        longitude=Decimal("126.4407"),
        elevation_meters=7,
    ),
    Airport(
        icao="EFHK",
        iata="HEL",
        name="Helsinki Airport",
        country="Finland",
        timezone="Europe/Helsinki",
        latitude=Decimal("60.3172"),
        longitude=Decimal("24.9633"),
        elevation_meters=55,
    ),
    Airport(
        icao="LTAC",
        iata="ESB",
        name="Ankara Esenboga Airport",
        country="Turkey",
        timezone="Europe/Istanbul",
        latitude=Decimal("40.1281"),
        longitude=Decimal("32.9951"),
        elevation_meters=953,
    ),
    Airport(
        icao="EPWA",
        iata="WAW",
        name="Warsaw Chopin Airport",
        country="Poland",
        timezone="Europe/Warsaw",
        latitude=Decimal("52.1657"),
        longitude=Decimal("20.9671"),
        elevation_meters=110,
    ),
    Airport(
        icao="EDDM",
        iata="MUC",
        name="Munich Airport",
        country="Germany",
        timezone="Europe/Berlin",
        latitude=Decimal("48.3538"),
        longitude=Decimal("11.7861"),
        elevation_meters=453,
    ),
)


def _build_icao_index(airports: Iterable[Airport]) -> Mapping[str, Airport]:
    return MappingProxyType({airport.icao: airport for airport in airports})


def _build_iata_index(airports: Iterable[Airport]) -> Mapping[str, Airport]:
    return MappingProxyType({airport.iata: airport for airport in airports})


@dataclass(frozen=True, slots=True)
class StationRegistry:
    """Immutable in-memory registry for airport stations."""

    _by_icao: Mapping[str, Airport] = field(default_factory=dict)
    _by_iata: Mapping[str, Airport] = field(default_factory=dict)

    @classmethod
    def empty(cls) -> "StationRegistry":
        """Create an empty station registry."""

        return cls(
            _by_icao=MappingProxyType({}),
            _by_iata=MappingProxyType({}),
        )

    @classmethod
    def with_default_airports(cls) -> "StationRegistry":
        """Create a station registry preloaded with known airport stations."""

        return cls.from_airports(DEFAULT_AIRPORTS)

    @classmethod
    def from_airports(cls, airports: Iterable[Airport]) -> "StationRegistry":
        """Create a station registry from airport entities."""

        registry = cls.empty()
        for airport in airports:
            registry = registry.register(airport)
        return registry

    def register(self, airport: Airport) -> "StationRegistry":
        """Return a new registry containing the airport entity."""

        if airport.icao in self._by_icao:
            msg = f"Airport ICAO already registered: {airport.icao}"
            raise StationRegistryError(msg)
        if airport.iata in self._by_iata:
            msg = f"Airport IATA already registered: {airport.iata}"
            raise StationRegistryError(msg)

        airports = (*self.list(), airport)
        return type(self)(
            _by_icao=_build_icao_index(airports),
            _by_iata=_build_iata_index(airports),
        )

    def get_by_icao(self, icao: str) -> Airport | None:
        """Return an airport by ICAO code, if registered."""

        return self._by_icao.get(icao)

    def get_by_iata(self, iata: str) -> Airport | None:
        """Return an airport by IATA code, if registered."""

        return self._by_iata.get(iata)

    def list(self) -> tuple[Airport, ...]:
        """Return registered airports sorted by ICAO code."""

        return tuple(sorted(self._by_icao.values(), key=lambda airport: airport.icao))


DEFAULT_STATION_REGISTRY = StationRegistry.with_default_airports()

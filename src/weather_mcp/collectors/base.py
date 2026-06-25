"""Base abstractions for weather data collectors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar, runtime_checkable

from weather_mcp.domain.value_objects import Station

RawObservationT = TypeVar("RawObservationT")
NormalizedObservationT = TypeVar("NormalizedObservationT")
ProtocolRawObservationT = TypeVar("ProtocolRawObservationT", contravariant=True)
ProtocolNormalizedObservationT = TypeVar(
    "ProtocolNormalizedObservationT",
    covariant=True,
)


@dataclass(frozen=True, slots=True)
class CollectorIdentity:
    """Immutable identity metadata shared by all collectors."""

    name: str
    priority: int = 100


@runtime_checkable
class CollectorProtocol(
    Protocol[ProtocolRawObservationT, ProtocolNormalizedObservationT],
):
    """Structural interface that every collector implementation must satisfy."""

    @property
    def name(self) -> str:
        """Return the unique collector name."""

    @property
    def priority(self) -> int:
        """Return the collector priority; lower values run first."""

    def supports(self, station: Station) -> bool:
        """Return whether this collector supports a station identifier."""

    async def collect(self, station: Station) -> ProtocolNormalizedObservationT:
        """Collect and return a normalized observation for a station."""

    def validate(self, observation: ProtocolRawObservationT) -> None:
        """Validate a raw observation before normalization."""

    def normalize(
        self,
        observation: ProtocolRawObservationT,
    ) -> ProtocolNormalizedObservationT:
        """Normalize a validated raw observation."""


class BaseCollector(ABC, Generic[RawObservationT, NormalizedObservationT]):
    """Abstract base class for all weather collectors.

    Concrete collectors must inherit from this class and provide all collection,
    validation, normalization, and station support behavior in infrastructure
    adapters outside the core registry framework.
    """

    def __init__(self, identity: CollectorIdentity) -> None:
        self._identity = identity

    @property
    def name(self) -> str:
        """Return the unique collector name."""

        return self._identity.name

    @property
    def priority(self) -> int:
        """Return the collector priority; lower values run first."""

        return self._identity.priority

    @abstractmethod
    def supports(self, station: Station) -> bool:
        """Return whether this collector supports a station identifier."""

    @abstractmethod
    async def collect(self, station: Station) -> NormalizedObservationT:
        """Collect and return a normalized observation for a station."""

    @abstractmethod
    def validate(self, observation: RawObservationT) -> None:
        """Validate a raw observation before normalization."""

    @abstractmethod
    def normalize(
        self,
        observation: RawObservationT,
    ) -> NormalizedObservationT:
        """Normalize a validated raw observation."""

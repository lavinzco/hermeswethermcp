"""Collector registry for weather observation sources."""

from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from weather_mcp.collectors.base import BaseCollector
from weather_mcp.collectors.exceptions import CollectorError

CollectorT = TypeVar("CollectorT", bound=BaseCollector[Any, Any])


class CollectorRegistry(Generic[CollectorT]):
    """In-memory registry for collector implementations.

    The registry depends only on the collector abstraction and keeps collection
    source selection separate from concrete infrastructure implementations.
    """

    def __init__(self, collectors: Iterable[CollectorT] | None = None) -> None:
        self._collectors: dict[str, CollectorT] = {}
        for collector in collectors or ():
            self.register(collector)

    def register(self, collector: CollectorT) -> None:
        """Register a collector by its unique name."""

        if collector.name in self._collectors:
            msg = f"Collector already registered: {collector.name}"
            raise CollectorError(msg)
        self._collectors[collector.name] = collector

    def unregister(self, name: str) -> CollectorT:
        """Remove and return a collector by name."""

        try:
            return self._collectors.pop(name)
        except KeyError as exc:
            msg = f"Collector is not registered: {name}"
            raise CollectorError(msg) from exc

    def get(self, name: str) -> CollectorT | None:
        """Return a collector by name, if registered."""

        return self._collectors.get(name)

    def list(self) -> tuple[CollectorT, ...]:
        """Return all collectors ordered by ascending priority and name."""

        return tuple(
            sorted(
                self._collectors.values(),
                key=lambda collector: (collector.priority, collector.name),
            )
        )

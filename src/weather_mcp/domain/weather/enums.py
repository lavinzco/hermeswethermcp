"""Canonical weather enumerations."""

from enum import StrEnum


class ObservationType(StrEnum):
    """Supported canonical weather observation categories."""

    OBSERVATION = "observation"
    METAR = "metar"
    SYNOP = "synop"
    FORECAST = "forecast"
    NOWCAST = "nowcast"

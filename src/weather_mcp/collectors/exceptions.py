"""Collector framework exceptions."""


class CollectorError(Exception):
    """Base exception for collector framework failures."""


class CollectorTimeout(CollectorError):  # noqa: N818
    """Raised when a collector cannot complete within its timeout budget."""


class CollectorUnavailable(CollectorError):  # noqa: N818
    """Raised when a collector is unavailable for collection."""


class InvalidObservation(CollectorError):  # noqa: N818
    """Raised when a collected observation cannot be validated or normalized."""

"""Logging configuration for the Weather MCP Server."""

import logging
import sys
from collections.abc import Mapping
from typing import Any

from weather_mcp.settings import LogLevel

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


class ContextFilter(logging.Filter):
    """Attach static context fields to every log record."""

    def __init__(self, context: Mapping[str, Any] | None = None) -> None:
        super().__init__()
        self._context = dict(context or {})

    def filter(self, record: logging.LogRecord) -> bool:
        """Populate configured context attributes on a log record."""

        for key, value in self._context.items():
            setattr(record, key, value)
        return True


def configure_logging(
    level: LogLevel = "INFO",
    context: Mapping[str, Any] | None = None,
) -> None:
    """Configure root logging for console output."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(ContextFilter(context))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""

    return logging.getLogger(name)

"""Application configuration bootstrap."""

from weather_mcp.logger import configure_logging, get_logger
from weather_mcp.settings import Settings, get_settings


def bootstrap(settings: Settings | None = None) -> Settings:
    """Initialize application-wide configuration concerns."""

    active_settings = settings or get_settings()
    configure_logging(
        level=active_settings.log_level,
        context={"app_name": active_settings.app_name},
    )
    get_logger(__name__).debug("Configuration bootstrap completed")
    return active_settings


if __name__ == "__main__":
    bootstrap()

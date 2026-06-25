"""Application settings for the Weather MCP Server."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "development", "staging", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WEATHER_MCP_",
        extra="ignore",
        validate_assignment=True,
    )

    app_name: str = Field(default="weather-mcp", min_length=1)
    environment: Environment = "local"
    debug: bool = False
    log_level: LogLevel = "INFO"
    database_url: str = "sqlite:///data/weather_mcp.db"
    sqlite_path: Path = Path("data/weather_mcp.db")
    request_timeout_seconds: float = Field(default=10.0, gt=0.0)
    external_api_key: SecretStr | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

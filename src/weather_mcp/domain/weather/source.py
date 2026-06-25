"""Weather source definitions."""

from enum import StrEnum


class WeatherSource(StrEnum):
    """Supported canonical weather data sources."""

    SINGAPORE_GOV = "SingaporeGov"
    CHECK_WX = "CheckWX"
    OPEN_METEO = "OpenMeteo"
    DWD = "DWD"
    JMA = "JMA"
    KMA = "KMA"
    WEATHER_UNDERGROUND = "WeatherUnderground"
    NOAA = "NOAA"

"""Airport entity definitions."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Airport(BaseModel):
    """Immutable airport station entity."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    icao: str = Field(min_length=4, max_length=4, pattern=r"^[A-Z0-9]{4}$")
    iata: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z0-9]{3}$")
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    timezone: str = Field(min_length=1)
    latitude: Decimal = Field(ge=Decimal("-90"), le=Decimal("90"))
    longitude: Decimal = Field(ge=Decimal("-180"), le=Decimal("180"))
    elevation_meters: int

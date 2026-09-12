from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import CamelModel


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "airline": "WN",
                "airportFrom": "DAL",
                "airportTo": "HOU",
                "dayOfWeek": 3,
                "time": 840,
                "length": 60,
            }
        },
    )

    airline: str = Field(..., description="Codigo IATA de la aerolinea, p.ej. 'WN'.")
    airport_from: str = Field(..., alias="airportFrom", description="Aeropuerto de origen (IATA).")
    airport_to: str = Field(..., alias="airportTo", description="Aeropuerto de destino (IATA).")
    day_of_week: int = Field(..., alias="dayOfWeek", ge=1, le=7)
    time: int = Field(..., ge=0, le=1439, description="Minutos desde medianoche.")
    length: int = Field(..., gt=0, description="Duracion estimada del vuelo, en minutos.")

    @field_validator("airport_to")
    @classmethod
    def airports_must_differ(cls, value: str, info) -> str:
        if info.data.get("airport_from") == value:
            raise ValueError("airportFrom y airportTo no pueden ser el mismo aeropuerto")
        return value


class ReferenceRate(CamelModel):
    label: str
    rate: float


class PredictionResult(CamelModel):
    probability: float
    band: str
    threshold: float
    high_band_threshold: float
    references: list[ReferenceRate]
    model_version: str

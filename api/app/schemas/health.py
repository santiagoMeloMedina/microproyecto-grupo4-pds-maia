from app.schemas.base import CamelModel


class Health(CamelModel):
    name: str
    api_version: str
    model_family: str
    threshold: float
    high_band_threshold: float

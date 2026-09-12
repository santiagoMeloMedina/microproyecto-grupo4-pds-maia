from app.schemas.base import CamelModel


class Health(CamelModel):
    name: str
    api_version: str
    # Version del paquete model_riesgo_retraso que se esta sirviendo. Es distinta
    # de api_version: la API puede cambiar sin que cambie el modelo, y al reves.
    model_version: str
    model_family: str
    threshold: float
    high_band_threshold: float

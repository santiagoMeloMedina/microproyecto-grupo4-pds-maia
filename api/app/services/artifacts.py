from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from model_riesgo_retraso import __version__ as model_version
from model_riesgo_retraso.predict import get_metadata
from model_riesgo_retraso.processing.data_manager import load_pipeline

ROOT = Path(__file__).resolve().parents[3]

CLAVE_FRANJA = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Franja"]


def _ruta_historico() -> Path:
    """Ubica el parquet con el historico de vuelos.

    Se resuelve por variable de entorno para que el contenedor pueda montarlo
    donde quiera, y contra el repositorio cuando se corre en local.
    """
    ruta_env = os.getenv("AIRLINES_PARQUET")
    if ruta_env:
        return Path(ruta_env)
    return ROOT / "dashboard" / "data" / "vuelos.parquet"


def _franja_de(minutos: int) -> str:
    for tope, etiqueta in [(360, "00-06"), (720, "06-12"), (1080, "12-18")]:
        if minutos < tope:
            return etiqueta
    return "18-24"


class Artifacts:
    """Modelo, metadata y datos historicos, cargados una sola vez por proceso.

    El modelo no se deserializa desde un archivo suelto del repositorio: se toma
    del paquete `model_riesgo_retraso`, instalado con pip desde el wheel que
    construye model-pkg/. Asi la API no necesita que airlines_ml este en el
    PYTHONPATH ni que exista models/modelo_ganador.joblib, y la version del
    modelo que sirve queda registrada en su propia metadata.
    """

    def __init__(self) -> None:
        self.model = load_pipeline()
        self.metadata: dict[str, Any] = get_metadata()
        self.model_version = model_version

        ruta = _ruta_historico()
        if not ruta.exists():
            raise RuntimeError(
                f"Falta el historico de vuelos en {ruta}. Generalo con "
                "`python scripts/generar_datos_tablero.py` o define la variable "
                "de entorno AIRLINES_PARQUET."
            )
        self.flights = pd.read_parquet(ruta)

        self.threshold = float(self.metadata.get("umbral", 0.5))
        self.high_band_threshold = float(
            self.metadata.get("banda_alta", self.threshold + 0.15)
        )
        self.model_family = self.metadata.get("familia", "desconocido")

        self.slots = self._build_slots()

    def _build_slots(self) -> pd.DataFrame:
        """Una fila por franja de itinerario, con su riesgo estimado por el modelo.

        El riesgo se toma del modelo y no de la tasa observada porque cada franja
        tiene pocos vuelos en el periodo: la tasa observada de una franja con
        cuatro vuelos es ruido, mientras que el modelo comparte fuerza entre
        franjas parecidas.
        """
        grouped = (
            self.flights.groupby(CLAVE_FRANJA, observed=True)
            .agg(
                Time=("Time", "median"),
                Length=("Length", "median"),
                vuelos=("Delay", "size"),
                tasa_observada=("Delay", "mean"),
            )
            .reset_index()
        )
        grouped["Time"] = grouped["Time"].astype(int)
        grouped["Length"] = grouped["Length"].astype(int)
        grouped["Ruta"] = (
            grouped["AirportFrom"].astype(str) + "-" + grouped["AirportTo"].astype(str)
        )
        grouped["riesgo"] = self.model.predict_proba(grouped)[:, 1]
        return grouped

    def band(self, probability: float) -> str:
        if probability >= self.high_band_threshold:
            return "alto"
        if probability >= self.threshold:
            return "medio"
        return "bajo"

    def slot_of(self, minutes: int) -> str:
        return _franja_de(minutes)


_artifacts: Artifacts | None = None


def get_artifacts() -> Artifacts:
    """Punto unico de acceso, cargado de forma perezosa (lazy) y cacheado."""
    global _artifacts
    if _artifacts is None:
        _artifacts = Artifacts()
    return _artifacts

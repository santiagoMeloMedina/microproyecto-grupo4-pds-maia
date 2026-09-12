from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CLAVE_FRANJA = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Franja"]


def _franja_de(minutos: int) -> str:
    for tope, etiqueta in [(360, "00-06"), (720, "06-12"), (1080, "12-18")]:
        if minutos < tope:
            return etiqueta
    return "18-24"


class Artifacts:
    """Modelo, metadata y datos historicos, cargados una sola vez por proceso."""

    def __init__(self) -> None:
        try:
            self.model = joblib.load(ROOT / "models" / "modelo_ganador.joblib")
            self.metadata: dict[str, Any] = json.loads(
                (ROOT / "models" / "metadata.json").read_text(encoding="utf-8")
            )
            self.flights = pd.read_parquet(ROOT / "dashboard" / "data" / "vuelos.parquet")
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Falta un artefacto del modelo: {exc}. Ejecuta "
                "modeling/katherin-modelos-entrega2.ipynb para generarlos (ver "
                "dashboard/app.py, que depende de los mismos archivos)."
            ) from exc

        self.threshold = float(self.metadata.get("umbral", 0.5))
        self.high_band_threshold = float(
            self.metadata.get("banda_alta", self.threshold + 0.15)
        )
        self.model_family = self.metadata.get("familia", "desconocido")

        self.slots = self._build_slots()

    def _build_slots(self) -> pd.DataFrame:
        """Una fila por franja de itinerario, con su riesgo estimado por el modelo.

        Ver dashboard/app.py::construir_franjas: el riesgo se toma del modelo y no
        de la tasa observada porque cada franja tiene pocos vuelos en el periodo.
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

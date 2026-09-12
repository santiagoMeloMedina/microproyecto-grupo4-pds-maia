"""Interfaz de prediccion del paquete.

Es el unico punto de entrada que la API necesita: recibe itinerarios, los valida,
los pasa por el pipeline entrenado y devuelve probabilidad y banda de riesgo.
"""
from __future__ import annotations

import json
import typing as t

import pandas as pd

from model_riesgo_retraso import __version__
from model_riesgo_retraso.config.core import TRAINED_MODEL_DIR, config
from model_riesgo_retraso.processing.data_manager import load_pipeline
from model_riesgo_retraso.processing.validation import validate_inputs

_pipeline = None
_metadata: dict | None = None


def _get_pipeline():
    """Carga perezosa: el modelo se deserializa una vez por proceso."""
    global _pipeline
    if _pipeline is None:
        _pipeline = load_pipeline()
    return _pipeline


def get_metadata() -> dict:
    """Umbral, banda alta y metricas con las que se entreno este modelo."""
    global _metadata
    if _metadata is None:
        ruta = TRAINED_MODEL_DIR / "metadata.json"
        if ruta.exists():
            _metadata = json.loads(ruta.read_text(encoding="utf-8"))
        else:
            _metadata = {
                "version": __version__,
                "umbral": config.modelo.umbral,
                "banda_alta": config.modelo.banda_alta,
            }
    return _metadata


def banda(probabilidad: float) -> str:
    """Traduce la probabilidad a la accion de planeacion que le corresponde."""
    meta = get_metadata()
    if probabilidad >= float(meta.get("banda_alta", config.modelo.banda_alta)):
        return "alto"
    if probabilidad >= float(meta.get("umbral", config.modelo.umbral)):
        return "medio"
    return "bajo"


def make_prediction(*, input_data: t.Union[pd.DataFrame, t.List[dict]]) -> dict:
    """Riesgo de retraso para uno o varios itinerarios.

    Devuelve siempre la misma estructura, con `errors` en None cuando todo salio
    bien. La API traduce ese campo a un 400 con el detalle.
    """
    data = pd.DataFrame(input_data)
    validated_data, errors = validate_inputs(input_data=data)

    results: dict = {
        "predictions": None,
        "bands": None,
        "version": __version__,
        "errors": errors,
    }

    if errors:
        return results

    if validated_data.empty:
        results["predictions"] = []
        results["bands"] = []
        return results

    pipeline = _get_pipeline()
    probabilidades = pipeline.predict_proba(validated_data[config.modelo.features])[:, 1]

    results["predictions"] = [float(p) for p in probabilidades]
    results["bands"] = [banda(float(p)) for p in probabilidades]
    return results

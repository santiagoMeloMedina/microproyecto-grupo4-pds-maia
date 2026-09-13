"""Entrenamiento reproducible del modelo de produccion.

Se ejecuta con `tox run -e train` desde model-pkg/. Ajusta el pipeline sobre la
ventana 0-24 (entrenamiento + validacion, igual que el reajuste final de la
Entrega 2), lo evalua una sola vez sobre el bloque de prueba 25-30 y lo guarda
dentro del paquete para que viaje en el wheel.
"""
from __future__ import annotations

import json
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)

from model_riesgo_retraso import __version__
from model_riesgo_retraso.config.core import TRAINED_MODEL_DIR, config
from model_riesgo_retraso.pipeline import crear_pipeline, dispositivo
from model_riesgo_retraso.processing.data_manager import cargar_particionado, save_pipeline

CAMPOS = config.modelo.features
OBJETIVO = config.modelo.target


def evaluar(pipeline, datos) -> dict:
    """Metricas sobre el bloque de prueba, al umbral de operacion configurado."""
    proba = pipeline.predict_proba(datos[CAMPOS])[:, 1]
    y = datos[OBJETIVO]
    pred = (proba >= config.modelo.umbral).astype(int)

    return {
        "roc_auc": float(roc_auc_score(y, proba)),
        "pr_auc": float(average_precision_score(y, proba)),
        "brier": float(brier_score_loss(y, proba)),
        "log_loss": float(log_loss(y, proba)),
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "umbral": config.modelo.umbral,
        "tasa_predicha": float(pred.mean()),
        "prob_media": float(proba.mean()),
    }


def run_training() -> None:
    """Entrena y persiste el pipeline."""
    print(f"Entrenando {config.app_config.package_name} v{__version__}")
    print(f"Dispositivo XGBoost: {dispositivo()}")

    particion = cargar_particionado()
    entrenamiento = particion.entrenamiento_completo
    prueba = particion.prueba

    print(
        f"  entrenamiento (dias 0-{config.modelo.dia_fin_validacion - 1}): "
        f"{len(entrenamiento):,} vuelos, tasa {entrenamiento[OBJETIVO].mean():.4f}"
    )
    print(
        f"  prueba        (dias {config.modelo.dia_fin_validacion}-"
        f"{config.modelo.total_dias - 1}): "
        f"{len(prueba):,} vuelos, tasa {prueba[OBJETIVO].mean():.4f}"
    )

    pipeline = crear_pipeline()
    # DiaCalendario entra al fit porque DensidadProgramada lo necesita para
    # promediar vuelos por dia; no es una caracteristica del modelo.
    pipeline.fit(entrenamiento[CAMPOS + ["DiaCalendario"]], entrenamiento[OBJETIVO])

    metricas = evaluar(pipeline, prueba)
    print("\n  Metricas sobre el bloque de prueba:")
    for nombre, valor in metricas.items():
        print(f"    {nombre:15} {valor:.4f}")

    save_pipeline(pipeline_to_persist=pipeline)

    # La metadata viaja junto al modelo: la API lee de aqui el umbral y la banda
    # alta en vez de tenerlos escritos en el codigo.
    metadata = {
        "version": __version__,
        "familia": "xgboost",
        "calibrado": False,
        "umbral": config.modelo.umbral,
        "banda_alta": config.modelo.banda_alta,
        "criterio_umbral": "presupuesto de refuerzo del 20% de las franjas",
        "campos_entrada": CAMPOS,
        "ventana_entrenamiento": f"dias 0-{config.modelo.dia_fin_validacion - 1}",
        "metricas_prueba": metricas,
        "tasa_base_entrenamiento": float(entrenamiento[OBJETIVO].mean()),
        "tasa_base_prueba": float(prueba[OBJETIVO].mean()),
    }
    ruta_metadata = TRAINED_MODEL_DIR / "metadata.json"
    ruta_metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"\n  Modelo guardado en {TRAINED_MODEL_DIR}")


if __name__ == "__main__":
    run_training()

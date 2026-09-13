"""Definicion del pipeline de produccion.

Un solo objeto encapsula preprocesamiento y estimador, de modo que la API
aplique en prediccion exactamente las mismas transformaciones que se ajustaron
en entrenamiento. Es la garantia de que no haya deriva entre entrenar y servir.
"""
from __future__ import annotations

import os

from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from model_riesgo_retraso.config.core import config
from model_riesgo_retraso.processing.features import ACategoricas, DensidadProgramada


def dispositivo() -> str:
    """'cuda' si se pide explicitamente por variable de entorno, 'cpu' si no.

    La GPU acelera el entrenamiento de XGBoost pero no mejora su desempeno:
    sobre estos datos el AUC sale identico y solo cambia el tiempo. Por eso el
    valor por defecto es cpu, que es lo que corre en el contenedor de la API.
    """
    return "cuda" if os.getenv("XGBOOST_DEVICE", "").lower() == "cuda" else "cpu"


def crear_pipeline() -> Pipeline:
    """Arma el pipeline con los hiperparametros del ganador de la Entrega 2."""
    modelo = config.modelo

    return Pipeline(
        [
            # Proxy de congestion: se aprende como tabla de consulta para poder
            # calcularse sobre un itinerario futuro, sin conocer la fecha real.
            ("densidad", DensidadProgramada()),
            # Categoricas nativas: XGBoost hace particiones de conjunto sobre los
            # 293 aeropuertos en vez de imponerles un orden inexistente.
            ("codificador", ACategoricas()),
            (
                "modelo",
                XGBClassifier(
                    n_estimators=modelo.n_estimators,
                    max_depth=modelo.max_depth,
                    learning_rate=modelo.learning_rate,
                    subsample=modelo.subsample,
                    colsample_bytree=modelo.colsample_bytree,
                    min_child_weight=modelo.min_child_weight,
                    reg_lambda=modelo.reg_lambda,
                    random_state=modelo.random_state,
                    tree_method="hist",
                    device=dispositivo(),
                    enable_categorical=True,
                    eval_metric="logloss",
                    n_jobs=-1,
                ),
            ),
        ]
    )

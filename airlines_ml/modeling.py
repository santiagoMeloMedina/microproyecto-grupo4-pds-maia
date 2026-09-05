"""Familias de modelos, espacios de busqueda y metricas de evaluacion."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from scipy.stats import loguniform
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
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
from sklearn.model_selection import ParameterSampler
from xgboost import XGBClassifier

SEMILLA = 42


@dataclass(frozen=True)
class Familia:
    """Une un algoritmo con el preprocesamiento que necesita."""

    nombre: str
    preprocesamiento: str
    constructor: Callable[..., Any]
    espacio: dict


# --- Espacios de busqueda -------------------------------------------------
#
# Se recorren por muestreo aleatorio y no por malla exhaustiva: con 6 o 7
# hiperparametros una malla obligaria a miles de combinaciones, mientras que 30
# muestras aleatorias cubren mejor el espacio con el presupuesto disponible.

ESPACIO_LOGISTICA = {
    # (solver, penalty) van juntos porque no todas las combinaciones son validas.
    "solver_penalty": [("lbfgs", "l2"), ("liblinear", "l2"), ("liblinear", "l1")],
    "C": loguniform(1e-3, 1e2),
    "class_weight": [None, "balanced"],
    "max_iter": [200, 500],
}

ESPACIO_RANDOM_FOREST = {
    "n_estimators": [100, 150, 200, 300],
    "max_depth": [8, 12, 16, 20, 24],
    "min_samples_leaf": [1, 5, 20, 50],
    "max_features": ["sqrt", "log2", 0.5],
    "class_weight": [None, "balanced"],
}

ESPACIO_XGBOOST = {
    "n_estimators": [200, 400, 600, 800],
    "max_depth": [4, 6, 8, 10],
    "learning_rate": loguniform(0.01, 0.3),
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0],
    "min_child_weight": [1, 5, 20, 50],
    "reg_lambda": [0.1, 1.0, 10.0],
}


def _crear_logistica(**params):
    solver, penalty = params.pop("solver_penalty")
    return LogisticRegression(solver=solver, penalty=penalty, random_state=SEMILLA, **params)


def _crear_random_forest(**params):
    return RandomForestClassifier(random_state=SEMILLA, n_jobs=-1, **params)


def dispositivo_xgboost() -> str:
    """Devuelve 'cuda' si hay una GPU NVIDIA visible, 'cpu' si no.

    Se consulta `nvidia-smi` y no se prueba un ajuste con device='cuda': XGBoost
    acepta esa opcion aunque no haya tarjeta, cae a CPU con una advertencia y no
    lanza excepcion, de modo que un ajuste de prueba siempre "funciona" y no
    distingue nada. `nvidia-smi` solo existe donde hay driver instalado, que es
    justo la condicion que interesa.

    Ojo con la expectativa: la GPU acelera el entrenamiento de XGBoost, no mejora
    su desempeno. Sobre estos datos el AUC sale identico; lo que cambia es el
    tiempo. La regresion logistica y Random Forest no la usan en absoluto.
    """
    global _DISPOSITIVO
    if _DISPOSITIVO is not None:
        return _DISPOSITIVO

    _DISPOSITIVO = "cpu"
    if shutil.which("nvidia-smi"):
        try:
            salida = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=20,
            )
            if salida.returncode == 0 and salida.stdout.strip():
                _DISPOSITIVO = "cuda"
        except Exception:
            pass
    return _DISPOSITIVO


_DISPOSITIVO: str | None = None


def _crear_xgboost(**params):
    return XGBClassifier(
        tree_method="hist",
        device=dispositivo_xgboost(),
        enable_categorical=True,
        eval_metric="logloss",
        random_state=SEMILLA,
        n_jobs=-1,
        **params,
    )


FAMILIAS = {
    "logistica": Familia("logistica", "lineal", _crear_logistica, ESPACIO_LOGISTICA),
    "random_forest": Familia("random_forest", "ordinal", _crear_random_forest, ESPACIO_RANDOM_FOREST),
    "xgboost": Familia("xgboost", "categorico", _crear_xgboost, ESPACIO_XGBOOST),
}


def muestrear_configuraciones(familia: str, n: int = 30, semilla: int = SEMILLA) -> list[dict]:
    """Genera n configuraciones reproducibles para una familia."""
    espacio = FAMILIAS[familia].espacio
    return list(ParameterSampler(espacio, n_iter=n, random_state=semilla))


def params_para_registro(params: dict) -> dict:
    """Aplana la tupla (solver, penalty) para que MLflow la registre legible."""
    salida = dict(params)
    if "solver_penalty" in salida:
        solver, penalty = salida.pop("solver_penalty")
        salida["solver"] = solver
        salida["penalty"] = penalty
    return salida


# --- Metricas -------------------------------------------------------------


def elegir_umbral(y_true: np.ndarray, proba: np.ndarray) -> float:
    """Umbral que maximiza F1, buscado sobre validacion y nunca sobre prueba.

    La tasa base se desplaza entre periodos, asi que 0,5 deja de ser un corte
    razonable: hay que fijarlo explicitamente y con datos que el modelo no use
    para entrenar.
    """
    candidatos = np.linspace(0.2, 0.8, 61)
    puntajes = [f1_score(y_true, (proba >= u).astype(int), zero_division=0) for u in candidatos]
    return float(candidatos[int(np.argmax(puntajes))])


def evaluar(y_true: np.ndarray, proba: np.ndarray, umbral: float = 0.5) -> dict:
    """Metricas de ranking, de calibracion y de decision.

    - Ranking (roc_auc, pr_auc): independientes del umbral y de la tasa base. Son
      las adecuadas para comparar modelos bajo deriva temporal.
    - Calibracion (brier, log_loss): el tablero muestra una probabilidad, no solo
      una clase, asi que importa que ese numero signifique lo que dice.
    - Decision (accuracy, precision, recall, f1): dependen del umbral elegido y
      describen el comportamiento operativo.
    """
    pred = (proba >= umbral).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, proba)),
        "pr_auc": float(average_precision_score(y_true, proba)),
        "brier": float(brier_score_loss(y_true, proba)),
        "log_loss": float(log_loss(y_true, proba)),
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "umbral": float(umbral),
        "tasa_predicha": float(pred.mean()),
        "prob_media": float(proba.mean()),
    }

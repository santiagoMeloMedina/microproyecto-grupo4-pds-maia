"""Carga del dataset, particion temporal y persistencia del pipeline."""
from __future__ import annotations

import typing as t
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from model_riesgo_retraso import __version__ as _version
from model_riesgo_retraso.config.core import (
    TRAINED_MODEL_DIR,
    config,
    training_data_path,
)


def cargar_dataset(ruta: str | Path | None = None) -> pd.DataFrame:
    """Lee el CSV corrigiendo el espacio inicial de los campos de texto."""
    ruta = Path(ruta) if ruta is not None else training_data_path()
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro {ruta}. Ejecuta 'dvc pull', define la variable de "
            "entorno AIRLINES_CSV, o consulta scripts/windows/README.md."
        )
    return pd.read_csv(ruta, skipinitialspace=True)


def reconstruir_dia(df: pd.DataFrame) -> pd.Series:
    """Reconstruye el dia calendario relativo (0..30) desde el orden de las filas.

    El dataset no trae fecha, pero las filas estan ordenadas cronologicamente:
    DayOfWeek forma 31 bloques consecutivos que recorren la semana en orden. El
    numero de bloque es entonces el dia relativo.
    """
    dia_semana = df["DayOfWeek"].to_numpy()
    cambios = np.flatnonzero(dia_semana[1:] != dia_semana[:-1]) + 1
    marcas = np.zeros(len(df), dtype=np.int32)
    marcas[cambios] = 1
    return pd.Series(marcas.cumsum(), index=df.index, name="DiaCalendario")


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica la limpieza acordada y agrega el dia reconstruido.

    Los 216.618 duplicados exactos se conservan: el 51,4% de las claves de
    itinerario repetidas tiene Delay contradictorio, prueba de que son
    ocurrencias distintas de vuelos recurrentes y no errores de captura.
    """
    df = df.copy()
    df["DiaCalendario"] = reconstruir_dia(df)

    invalidos = df["Length"] <= 0
    if invalidos.any():
        df = df.loc[~invalidos].reset_index(drop=True)

    return df


@dataclass
class ParticionTemporal:
    """Tres bloques temporales disjuntos y consecutivos."""

    entrenamiento: pd.DataFrame
    validacion: pd.DataFrame
    prueba: pd.DataFrame

    @property
    def entrenamiento_completo(self) -> pd.DataFrame:
        """Entrenamiento + validacion: la ventana del reajuste final."""
        return pd.concat([self.entrenamiento, self.validacion], ignore_index=True)


def particionar(df: pd.DataFrame) -> ParticionTemporal:
    """Divide por dia calendario. Nunca aleatoriamente.

    La tasa de retraso se desplaza de 41,0% a 53,1% a lo largo del mes, asi que
    una particion aleatoria repartiria los mismos dias entre entrenamiento y
    prueba y el modelo evaluaria sobre un periodo que ya conoce.
    """
    dia = df["DiaCalendario"]
    return ParticionTemporal(
        entrenamiento=df.loc[dia < config.modelo.dia_fin_entrenamiento].reset_index(drop=True),
        validacion=df.loc[
            (dia >= config.modelo.dia_fin_entrenamiento)
            & (dia < config.modelo.dia_fin_validacion)
        ].reset_index(drop=True),
        prueba=df.loc[dia >= config.modelo.dia_fin_validacion].reset_index(drop=True),
    )


def cargar_particionado(ruta: str | Path | None = None) -> ParticionTemporal:
    """Carga, limpia y particiona en un solo paso."""
    return particionar(limpiar(cargar_dataset(ruta)))


def save_pipeline(*, pipeline_to_persist: Pipeline) -> None:
    """Guarda el pipeline versionado y borra los anteriores.

    Dejar una sola version dentro del paquete evita que el wheel quede con dos
    modelos y que la API cargue el que no es.
    """
    save_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
    save_path = TRAINED_MODEL_DIR / save_file_name

    remove_old_pipelines(files_to_keep=[save_file_name])
    TRAINED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline_to_persist, save_path)


def load_pipeline(*, file_name: str | None = None) -> Pipeline:
    """Carga el pipeline entrenado que viaja dentro del paquete."""
    if file_name is None:
        file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"

    file_path = TRAINED_MODEL_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo entrenado en {file_path}. "
            "Ejecuta 'tox run -e train' desde model-pkg/ antes de construir el wheel."
        )
    return joblib.load(filename=file_path)


def remove_old_pipelines(*, files_to_keep: t.List[str]) -> None:
    """Deja solo el modelo vigente y el __init__.py del directorio."""
    do_not_delete = list(files_to_keep) + ["__init__.py", "metadata.json"]
    if not TRAINED_MODEL_DIR.exists():
        return
    for model_file in TRAINED_MODEL_DIR.iterdir():
        if model_file.name not in do_not_delete:
            model_file.unlink()

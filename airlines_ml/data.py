"""Carga, limpieza y particion temporal del dataset Airlines.

Las decisiones implementadas aqui provienen del analisis exploratorio
(exploration/katherin-airlines.ipynb) y estan justificadas en
docs/2nd_delivery/borrador_entrega2.md:

- El CSV arrastra un espacio inicial en los campos de texto -> skipinitialspace.
- Los 4 registros con Length <= 0 son invalidos -> se eliminan.
- Los 216.618 duplicados exactos son vuelos recurrentes -> se conservan.
- Las filas estan en orden cronologico (31 dias) -> se reconstruye el dia y la
  particion es temporal, nunca aleatoria.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNAS_ITINERARIO = [
    "Airline",
    "Flight",
    "AirportFrom",
    "AirportTo",
    "DayOfWeek",
    "Time",
    "Length",
]

OBJETIVO = "Delay"

# Cortes de la particion temporal, en dias reconstruidos (0..30).
# Entrenamiento 0-19, validacion 20-24, prueba 25-30.
DIA_FIN_ENTRENAMIENTO = 20
DIA_FIN_VALIDACION = 25
TOTAL_DIAS = 31


def ruta_dataset() -> Path:
    """Ubica data/airlines.csv respetando la variable AIRLINES_CSV si existe."""
    ruta_env = os.getenv("AIRLINES_CSV")
    if ruta_env:
        return Path(ruta_env)
    return Path(__file__).resolve().parents[1] / "data" / "airlines.csv"


def cargar_crudo(ruta: str | Path | None = None) -> pd.DataFrame:
    """Lee el CSV corrigiendo el espacio inicial de los campos de texto."""
    ruta = Path(ruta) if ruta is not None else ruta_dataset()
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro {ruta}. Ejecuta 'dvc pull' o consulta "
            "scripts/windows/README.md para obtener los datos."
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
    """Aplica la limpieza acordada y agrega el dia reconstruido."""
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
        """Entrenamiento + validacion, para el reajuste final del modelo elegido."""
        return pd.concat([self.entrenamiento, self.validacion], ignore_index=True)

    def resumen(self) -> pd.DataFrame:
        filas = []
        for nombre, parte in [
            ("Entrenamiento", self.entrenamiento),
            ("Validacion", self.validacion),
            ("Prueba", self.prueba),
        ]:
            filas.append(
                {
                    "Particion": nombre,
                    "Dias": f"{parte['DiaCalendario'].min()}-{parte['DiaCalendario'].max()}",
                    "Filas": len(parte),
                    "Tasa de retraso": parte[OBJETIVO].mean(),
                }
            )
        return pd.DataFrame(filas)


def particionar(df: pd.DataFrame) -> ParticionTemporal:
    """Divide por dia calendario. Nunca aleatoriamente.

    La tasa de retraso se desplaza de 34,5% a 51,6% a lo largo del mes, asi que
    una particion aleatoria reparte los mismos dias entre entrenamiento y prueba
    y el modelo evalua sobre un periodo que ya conoce.
    """
    dia = df["DiaCalendario"]
    return ParticionTemporal(
        entrenamiento=df.loc[dia < DIA_FIN_ENTRENAMIENTO].reset_index(drop=True),
        validacion=df.loc[
            (dia >= DIA_FIN_ENTRENAMIENTO) & (dia < DIA_FIN_VALIDACION)
        ].reset_index(drop=True),
        prueba=df.loc[dia >= DIA_FIN_VALIDACION].reset_index(drop=True),
    )


def cargar_particionado(ruta: str | Path | None = None) -> ParticionTemporal:
    """Atajo: carga, limpia y particiona en un solo paso."""
    return particionar(limpiar(cargar_crudo(ruta)))

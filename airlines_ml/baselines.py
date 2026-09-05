"""Lineas base heredadas del analisis exploratorio.

Fijan el piso que un modelo debe superar para justificar su complejidad. Sin
ellas, un accuracy de 0,60 parece aceptable cuando en realidad una tabla de
frecuencias historicas ya lo alcanza.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import OBJETIVO
from .features import agregar_derivadas

CLAVE_ITINERARIO = ["Airline", "Flight", "AirportFrom", "AirportTo", "DayOfWeek", "Time", "Length"]


class ClaseMayoritaria:
    """Predice siempre la clase mas frecuente del entrenamiento.

    Bajo deriva temporal esta linea base puede caer por debajo del azar, que es
    justamente lo que la hace informativa.
    """

    nombre = "base_clase_mayoritaria"

    def fit(self, df: pd.DataFrame):
        self.tasa_ = float(df[OBJETIVO].mean())
        self.clase_ = int(self.tasa_ >= 0.5)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        return np.full(len(df), self.tasa_)


class MemoriaItinerario:
    """Memoriza el resultado historico de cada itinerario exacto.

    Mide cuanto se puede lograr sin generalizar en absoluto, solo recordando.
    """

    nombre = "base_memoria_itinerario"

    def fit(self, df: pd.DataFrame):
        self.tabla_ = df.groupby(CLAVE_ITINERARIO, sort=False)[OBJETIVO].mean()
        self.defecto_ = float(df[OBJETIVO].mean())
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        idx = pd.MultiIndex.from_frame(df[CLAVE_ITINERARIO])
        valores = self.tabla_.reindex(idx).to_numpy()
        return np.where(np.isnan(valores), self.defecto_, valores)


class TasaAerolineaFranja:
    """Tasa historica de retraso por aerolinea y franja horaria.

    Es la regla de negocio mas simple que un analista escribiria a mano, y en la
    exploracion resulto la linea base mas exigente.
    """

    nombre = "base_aerolinea_franja"

    def fit(self, df: pd.DataFrame):
        datos = agregar_derivadas(df)
        self.tabla_ = datos.groupby(["Airline", "Franja"], observed=True)[OBJETIVO].mean()
        self.defecto_ = float(df[OBJETIVO].mean())
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        datos = agregar_derivadas(df)
        idx = pd.MultiIndex.from_frame(datos[["Airline", "Franja"]])
        valores = self.tabla_.reindex(idx).to_numpy()
        return np.where(np.isnan(valores), self.defecto_, valores)


LINEAS_BASE = [ClaseMayoritaria, MemoriaItinerario, TasaAerolineaFranja]

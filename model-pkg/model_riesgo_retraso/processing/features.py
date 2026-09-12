"""Ingenieria de caracteristicas del modelo de produccion.

Restriccion de diseno: toda caracteristica debe poder calcularse a partir de los
seis campos que el tablero pide al usuario (aerolinea, origen, destino, dia de la
semana, hora programada y duracion). Una variable que dependa del dia calendario
concreto seria imposible de construir al servir una prediccion sobre un vuelo
futuro, asi que la densidad programada se resuelve como una tabla de consulta
aprendida en entrenamiento y no como un conteo sobre la fila.

Este modulo reproduce el camino de la familia ganadora (XGBoost con categoricas
nativas). La version de experimentacion, con las tres familias y sus tres
preprocesadores, vive en airlines_ml/features.py y no se empaqueta.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

CAMPOS_ENTRADA = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Time", "Length"]

CATEGORICAS = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Franja", "Ruta"]
NUMERICAS = [
    "Time",
    "Length",
    "Hora",
    "TimeSin",
    "TimeCos",
    "DensidadOrigen",
    "DensidadDestino",
]

LIMITES_FRANJA = [0, 360, 720, 1080, 1441]
ETIQUETAS_FRANJA = ["00-06", "06-12", "12-18", "18-24"]


def agregar_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Variables derivadas fila a fila, sin necesidad de ajuste previo."""
    salida = df.copy()
    salida["Hora"] = salida["Time"] // 60

    # La hora es ciclica: las 23:50 y las 00:10 estan a 20 minutos, no a 23 horas.
    angulo = 2 * np.pi * salida["Time"] / 1440.0
    salida["TimeSin"] = np.sin(angulo)
    salida["TimeCos"] = np.cos(angulo)

    salida["Franja"] = pd.cut(
        salida["Time"], bins=LIMITES_FRANJA, labels=ETIQUETAS_FRANJA, right=False
    ).astype(str)

    # astype(str) explicito: al servir, los aeropuertos pueden llegar con dtype
    # 'category' (asi los guarda el parquet del tablero) y la concatenacion de
    # categorias con texto no esta definida en pandas. Sobre texto es inocuo.
    salida["Ruta"] = salida["AirportFrom"].astype(str) + "-" + salida["AirportTo"].astype(str)
    return salida


class DensidadProgramada(BaseEstimator, TransformerMixin):
    """Cuantos vuelos suele haber en ese aeropuerto, ese dia y esa hora.

    Es un proxy de congestion construido solo con el itinerario, disponible antes
    del despegue. Se aprende en entrenamiento como promedio de vuelos por dia y
    se consulta en prediccion, de modo que no requiere conocer la fecha real.
    """

    def fit(self, X: pd.DataFrame, y=None):
        datos = agregar_derivadas(X)
        n_dias = max(datos["DiaCalendario"].nunique(), 1) if "DiaCalendario" in datos else 1

        self.tabla_origen_ = (
            datos.groupby(["AirportFrom", "DayOfWeek", "Hora"]).size() / n_dias
        )
        self.tabla_destino_ = (
            datos.groupby(["AirportTo", "DayOfWeek", "Hora"]).size() / n_dias
        )
        self.defecto_origen_ = float(self.tabla_origen_.median())
        self.defecto_destino_ = float(self.tabla_destino_.median())
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        datos = agregar_derivadas(X)

        idx_origen = pd.MultiIndex.from_frame(datos[["AirportFrom", "DayOfWeek", "Hora"]])
        idx_destino = pd.MultiIndex.from_frame(datos[["AirportTo", "DayOfWeek", "Hora"]])

        datos["DensidadOrigen"] = self.tabla_origen_.reindex(idx_origen).to_numpy()
        datos["DensidadDestino"] = self.tabla_destino_.reindex(idx_destino).to_numpy()

        # Un aeropuerto, dia y hora nunca vistos caen a la mediana: es la mejor
        # estimacion de congestion disponible sin informacion propia.
        datos["DensidadOrigen"] = datos["DensidadOrigen"].fillna(self.defecto_origen_)
        datos["DensidadDestino"] = datos["DensidadDestino"].fillna(self.defecto_destino_)

        return datos[CATEGORICAS + NUMERICAS]


class ACategoricas(BaseEstimator, TransformerMixin):
    """Fija las categorias vistas en entrenamiento como dtype 'category'.

    XGBoost trata asi las variables nominales con particiones de conjunto en vez
    de imponerles un orden artificial, que es lo que ocurriria con una
    codificacion ordinal sobre 293 aeropuertos.
    """

    def fit(self, X: pd.DataFrame, y=None):
        self.categorias_ = {
            col: pd.Index(sorted(X[col].dropna().unique())) for col in CATEGORICAS
        }
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        salida = X.copy()
        for col, categorias in self.categorias_.items():
            # Una categoria no vista queda como NaN, que XGBoost maneja de forma
            # nativa. Es preferible a fallar: el tablero no puede caerse porque
            # alguien consulte una ruta nueva.
            salida[col] = pd.Categorical(salida[col], categories=categorias)
        return salida

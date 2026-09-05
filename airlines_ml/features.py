"""Ingenieria de caracteristicas y preprocesadores.

Restriccion de diseno: toda caracteristica debe poder calcularse a partir de los
seis campos que el tablero pide al usuario (aerolinea, origen, destino, dia de la
semana, hora programada y duracion). Cualquier variable que dependa del dia
calendario concreto seria imposible de construir al servir una prediccion, asi
que la densidad programada se resuelve como una tabla de consulta aprendida en
entrenamiento y no como un conteo sobre la fila.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

CAMPOS_ENTRADA = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Time", "Length"]

CATEGORICAS = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Franja", "Ruta"]
NUMERICAS = ["Time", "Length", "Hora", "TimeSin", "TimeCos", "DensidadOrigen", "DensidadDestino"]

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

    def __init__(self, numericas_extra: tuple = ()):
        self.numericas_extra = numericas_extra

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

        datos["DensidadOrigen"] = (
            self.tabla_origen_.reindex(idx_origen).to_numpy()
        )
        datos["DensidadDestino"] = (
            self.tabla_destino_.reindex(idx_destino).to_numpy()
        )
        datos["DensidadOrigen"] = datos["DensidadOrigen"].fillna(self.defecto_origen_)
        datos["DensidadDestino"] = datos["DensidadDestino"].fillna(self.defecto_destino_)

        # getattr con defecto: un pipeline serializado antes de que existiera este
        # parametro debe seguir cargando. Agregar un argumento al constructor de un
        # transformador rompe los modelos ya empaquetados si no se contempla.
        extra = list(getattr(self, "numericas_extra", ()))
        return datos[CATEGORICAS + NUMERICAS + extra]


class RiesgoHistoricoVuelo(BaseEstimator, TransformerMixin):
    """Codificacion por objetivo del numero de vuelo, con suavizado.

    `Flight` es un identificador de alta cardinalidad (6.585 niveles): en one-hot
    dispara la dimensionalidad y como entero impone un orden que no existe. La
    tercera via es codificarlo por su tasa historica de retraso.
 
    El dataset original proviene de un flujo donde el
    orden de las filas cargaba informacion temporal, y al perderse la marca de
    tiempo se perdio la variable mas predictiva del problema: si la aeronave
    venia retrasada del vuelo anterior. Como un numero de vuelo se asocia de
    forma estable a una rotacion de aeronave, su tasa historica es el proxy mas
    cercano a ese efecto que los datos permiten reconstruir.

    El suavizado evita que un numero de vuelo con tres apariciones y dos retrasos
    entre como si tuviera 67% de riesgo: la media del grupo se mezcla con la
    global en proporcion a cuantas observaciones lo respaldan.
    """

    def __init__(self, suavizado: float = 20.0):
        self.suavizado = suavizado

    def fit(self, X: pd.DataFrame, y=None):
        if y is None:
            raise ValueError("RiesgoHistoricoVuelo necesita la variable objetivo para ajustarse.")

        objetivo = pd.Series(np.asarray(y), index=X.index)
        self.prior_ = float(objetivo.mean())

        agrupado = objetivo.groupby(X["Flight"]).agg(["sum", "count"])
        self.tabla_ = (
            (agrupado["sum"] + self.prior_ * self.suavizado)
            / (agrupado["count"] + self.suavizado)
        )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        salida = X.copy()
        # Un numero de vuelo no visto en entrenamiento cae al prior global, que es
        # la mejor estimacion disponible sin informacion propia.
        salida["RiesgoVuelo"] = (
            X["Flight"].map(self.tabla_).astype(float).fillna(self.prior_)
        )
        return salida


class ACategoricas(BaseEstimator, TransformerMixin):
    """Fija las categorias vistas en entrenamiento como dtype 'category'.

    XGBoost trata asi las variables nominales con splits de conjunto en vez de
    imponerles un orden artificial, que es lo que ocurriria con una codificacion
    ordinal sobre 293 aeropuertos.
    """

    def fit(self, X: pd.DataFrame, y=None):
        self.categorias_ = {col: pd.Index(sorted(X[col].dropna().unique())) for col in CATEGORICAS}
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        salida = X.copy()
        for col, categorias in self.categorias_.items():
            salida[col] = pd.Categorical(salida[col], categories=categorias)
        return salida


def construir_preprocesador(familia: str, incluir_riesgo_vuelo: bool = False) -> Pipeline:
    """Devuelve el preprocesador adecuado a cada familia de modelo.

    - 'lineal'     one-hot disperso y escalado. La regresion logistica necesita
                   variables indicadoras y escalas comparables.
    - 'ordinal'    enteros. Random Forest de scikit-learn no acepta categorias
                   nativas, asi que se codifican como enteros.
    - 'categorico' dtype category. XGBoost con enable_categorical.

    `incluir_riesgo_vuelo` agrega la codificacion por objetivo de `Flight`. Se
    deja como bandera y no por defecto porque el numero de vuelo no es parte de
    la unidad de analisis del tablero: sirve para medir su aporte en un
    experimento controlado antes de decidir si entra al modelo de produccion.
    """
    extras = ("RiesgoVuelo",) if incluir_riesgo_vuelo else ()
    numericas = NUMERICAS + list(extras)

    if familia == "lineal":
        # Ruta tiene 4.190 niveles: en one-hot dispararia la dimensionalidad sin
        # aportar sobre Airline y los dos aeropuertos, que ya estan incluidos.
        categoricas = [c for c in CATEGORICAS if c != "Ruta"]
        codificador = ColumnTransformer(
            [
                ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=20), categoricas),
                ("num", StandardScaler(), numericas),
            ],
            remainder="drop",
        )
    elif familia == "ordinal":
        codificador = ColumnTransformer(
            [
                (
                    "cat",
                    OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                    CATEGORICAS,
                ),
                ("num", "passthrough", numericas),
            ],
            remainder="drop",
        )
    elif familia == "categorico":
        codificador = ACategoricas()
    else:
        raise ValueError(f"Familia desconocida: {familia}")

    pasos = []
    if incluir_riesgo_vuelo:
        pasos.append(("riesgo_vuelo", RiesgoHistoricoVuelo()))
    pasos.append(("densidad", DensidadProgramada(numericas_extra=extras)))
    pasos.append(("codificador", codificador))
    return Pipeline(pasos)

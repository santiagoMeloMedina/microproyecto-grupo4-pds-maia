"""Validacion de las entradas de prediccion.

Equivale a processing/validation.py del taller 5: un esquema para un itinerario
(DataInputSchema) y otro para un lote (MultipleDataInputs). La API delega aqui,
de modo que la regla de que Time va en minutos desde medianoche se define una
sola vez y no en cada capa.
"""
from __future__ import annotations

import typing as t

import pandas as pd
from pydantic import BaseModel, Field, ValidationError

from model_riesgo_retraso.processing.features import CAMPOS_ENTRADA


class DataInputSchema(BaseModel):
    """Un itinerario: los seis campos que el tablero le pide al usuario."""

    Airline: str = Field(..., description="Codigo de la aerolinea, por ejemplo WN.")
    AirportFrom: str = Field(..., description="Codigo IATA del aeropuerto de origen.")
    AirportTo: str = Field(..., description="Codigo IATA del aeropuerto de destino.")
    DayOfWeek: int = Field(..., ge=1, le=7, description="1 = lunes, 7 = domingo.")
    Time: int = Field(
        ..., ge=0, le=1439, description="Hora programada, en minutos desde medianoche."
    )
    Length: int = Field(..., gt=0, description="Duracion programada, en minutos.")


class MultipleDataInputs(BaseModel):
    """Un lote de itinerarios."""

    inputs: t.List[DataInputSchema]


def drop_na_inputs(*, input_data: pd.DataFrame) -> pd.DataFrame:
    """Descarta filas sin alguno de los campos requeridos."""
    validated_data = input_data.copy()
    return validated_data.dropna(subset=CAMPOS_ENTRADA)


def validate_inputs(
    *, input_data: pd.DataFrame
) -> t.Tuple[pd.DataFrame, t.Optional[dict]]:
    """Valida el lote y devuelve los datos limpios junto con los errores.

    Nunca lanza: devuelve los errores para que la capa que llama decida el codigo
    de respuesta. Es lo que permite a la API contestar 400 con el detalle en vez
    de un 500 opaco.
    """
    faltantes = [c for c in CAMPOS_ENTRADA if c not in input_data.columns]
    if faltantes:
        return input_data, {
            "faltan_columnas": (
                f"El itinerario debe traer {CAMPOS_ENTRADA}; faltan {faltantes}."
            )
        }

    relevant_data = drop_na_inputs(input_data=input_data[CAMPOS_ENTRADA].copy())
    errors = None

    try:
        MultipleDataInputs(
            inputs=relevant_data.replace({pd.NA: None}).to_dict(orient="records")
        )
    except ValidationError as error:
        errors = error.json()

    return relevant_data, errors

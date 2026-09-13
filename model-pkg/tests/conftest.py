"""Configuracion de las pruebas del paquete."""
import pandas as pd
import pytest

from model_riesgo_retraso.config.core import config
from model_riesgo_retraso.processing.data_manager import cargar_particionado


@pytest.fixture(scope="session")
def sample_input_data() -> pd.DataFrame:
    """Una muestra del bloque de prueba: dias 25-30, nunca vistos al entrenar."""
    particion = cargar_particionado()
    return particion.prueba.sample(n=2000, random_state=config.modelo.random_state)


@pytest.fixture
def un_itinerario() -> dict:
    """Un itinerario valido, con los seis campos que pide el tablero."""
    return {
        "Airline": "WN",
        "AirportFrom": "LAS",
        "AirportTo": "PHX",
        "DayOfWeek": 3,
        "Time": 480,
        "Length": 65,
    }

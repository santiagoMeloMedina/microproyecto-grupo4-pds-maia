"""Pruebas de la funcion de prediccion del paquete.

No se limitan a comprobar que el modelo "responde algo": verifican que el
contrato de entrada se respete, que el umbral configurado y las bandas sean
coherentes, y que el desempeno no haya caido por debajo de la linea base que la
Entrega 2 fijo como referencia.
"""
import math

import pandas as pd
from sklearn.metrics import roc_auc_score

from model_riesgo_retraso import __version__
from model_riesgo_retraso.config.core import config
from model_riesgo_retraso.predict import banda, make_prediction

# Tasa por aerolinea x franja sobre el bloque de prueba: la regla que un analista
# escribiria a mano en una tarde. Si el modelo no la supera, no se justifica.
LINEA_BASE_AUC = 0.6763


def test_make_prediction_un_itinerario(un_itinerario):
    resultado = make_prediction(input_data=[un_itinerario])

    assert resultado["errors"] is None
    assert resultado["version"] == __version__
    assert len(resultado["predictions"]) == 1

    probabilidad = resultado["predictions"][0]
    assert isinstance(probabilidad, float)
    assert 0.0 <= probabilidad <= 1.0
    assert resultado["bands"][0] in {"bajo", "medio", "alto"}


def test_make_prediction_lote(sample_input_data):
    resultado = make_prediction(input_data=sample_input_data)

    assert resultado["errors"] is None
    assert len(resultado["predictions"]) == len(sample_input_data)
    assert all(0.0 <= p <= 1.0 for p in resultado["predictions"])
    assert not any(math.isnan(p) for p in resultado["predictions"])


def test_bandas_coherentes_con_el_umbral():
    """La banda debe seguir exactamente los cortes configurados."""
    umbral = config.modelo.umbral
    banda_alta = config.modelo.banda_alta

    assert banda(umbral - 0.01) == "bajo"
    assert banda(umbral) == "medio"
    assert banda(banda_alta - 0.01) == "medio"
    assert banda(banda_alta) == "alto"


def test_desempeno_sobre_el_bloque_de_prueba(sample_input_data):
    """El modelo empaquetado debe superar la linea base del proyecto."""
    resultado = make_prediction(input_data=sample_input_data)
    auc = roc_auc_score(
        sample_input_data[config.modelo.target], resultado["predictions"]
    )
    assert auc > LINEA_BASE_AUC


def test_entrada_invalida_devuelve_errores(un_itinerario):
    """Un dia de la semana fuera de 1..7 no debe llegar al modelo."""
    invalido = dict(un_itinerario, DayOfWeek=9)
    resultado = make_prediction(input_data=[invalido])

    assert resultado["errors"] is not None
    assert resultado["predictions"] is None


def test_columna_faltante_devuelve_errores(un_itinerario):
    """Si falta uno de los seis campos, se reporta en vez de fallar."""
    incompleto = {k: v for k, v in un_itinerario.items() if k != "Length"}
    resultado = make_prediction(input_data=[incompleto])

    assert resultado["errors"] is not None
    assert "faltan_columnas" in resultado["errors"]


def test_categoria_no_vista_no_rompe(un_itinerario):
    """Una aerolinea inexistente cae a NaN y XGBoost la maneja de forma nativa.

    El tablero no puede caerse porque alguien consulte un codigo que no estaba
    en el periodo de entrenamiento.
    """
    desconocida = dict(un_itinerario, Airline="ZZ", AirportFrom="XXX")
    resultado = make_prediction(input_data=[desconocida])

    assert resultado["errors"] is None
    assert 0.0 <= resultado["predictions"][0] <= 1.0

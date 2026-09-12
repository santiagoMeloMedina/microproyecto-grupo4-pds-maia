"""Modelo de riesgo de retraso por franja de itinerario, empaquetado para servir.

Este paquete contiene el camino de produccion del modelo ganador de los 90
experimentos de la Entrega 2: la ingenieria de caracteristicas, el pipeline, el
entrenamiento reproducible y la funcion de prediccion. Se empaqueta como wheel
para que la API lo instale con pip en vez de deserializar un archivo suelto.

No confundir con `airlines_ml`, que es el paquete de experimentacion: alli viven
las tres familias, las lineas base y los espacios de busqueda. Aqui vive una sola
configuracion, la que gano, sin dependencias del repositorio.
"""
import logging
from pathlib import Path

VERSION_PATH = Path(__file__).resolve().parent / "VERSION"

with open(VERSION_PATH, encoding="utf-8") as version_file:
    __version__ = version_file.read().strip()

# La libreria no debe imponer configuracion de logging a quien la importa.
logging.getLogger(__name__).addHandler(logging.NullHandler())

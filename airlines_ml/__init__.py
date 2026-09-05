"""Codigo compartido entre el notebook de modelado, la API y el tablero.

Mantener la preparacion de datos y el preprocesamiento en un solo lugar evita
que el modelo entrenado en el notebook reciba en produccion columnas construidas
de forma distinta, que es la causa mas comun de que un modelo empaquetado
prediga distinto al desplegarse.
"""

__version__ = "0.1.0"

"""Carga de datos compartida por el dashboard descriptivo estratégico."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from airlines_ml.data import cargar_crudo, limpiar
from airlines_ml.features import agregar_derivadas

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def load_data() -> pd.DataFrame:
    """Carga y prepara los datos con las reglas compartidas del proyecto."""
    data = agregar_derivadas(limpiar(cargar_crudo()))
    required = {"Delay"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")
    return data

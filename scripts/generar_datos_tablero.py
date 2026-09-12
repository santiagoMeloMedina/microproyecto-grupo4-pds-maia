"""Genera el historico de vuelos que consumen la API y el tablero.

    python scripts/generar_datos_tablero.py

Lee data/airlines.csv, aplica la misma limpieza del modelo, agrega las variables
derivadas que las vistas descriptivas necesitan y lo guarda como parquet. El
resultado se versiona porque la API y el contenedor lo requieren, y reconstruirlo
exige el CSV de 19 MB que vive en DVC.

Requiere el paquete del modelo instalado:

    pip install api/model-package/model_riesgo_retraso-0.0.1-py3-none-any.whl
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

try:
    from model_riesgo_retraso.processing.data_manager import cargar_dataset, limpiar
    from model_riesgo_retraso.processing.features import agregar_derivadas
except ModuleNotFoundError:
    # Respaldo: si el wheel no esta instalado, se usa el paquete de
    # experimentacion del repositorio, que aplica la misma limpieza.
    sys.path.insert(0, str(RAIZ))
    from airlines_ml.data import cargar_crudo as cargar_dataset
    from airlines_ml.data import limpiar
    from airlines_ml.features import agregar_derivadas

SALIDA = RAIZ / "dashboard" / "data" / "vuelos.parquet"

COLUMNAS = [
    "Airline",
    "AirportFrom",
    "AirportTo",
    "DayOfWeek",
    "Time",
    "Length",
    "Franja",
    "Ruta",
    "DiaCalendario",
    "Delay",
]

# Las nominales van como 'category': sobre 539 mil filas baja el parquet de
# varias decenas de MB a unos 3 MB y acelera los groupby del tablero.
CATEGORICAS = ["Airline", "AirportFrom", "AirportTo", "Franja", "Ruta"]


def main() -> None:
    print("Leyendo data/airlines.csv ...")
    df = limpiar(cargar_dataset())

    print("Agregando variables derivadas ...")
    df = agregar_derivadas(df)

    salida = df[COLUMNAS].copy()
    for col in CATEGORICAS:
        salida[col] = salida[col].astype("category")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    salida.to_parquet(SALIDA, index=False)

    tamano_mb = SALIDA.stat().st_size / 1_000_000
    print(f"\n{len(salida):,} vuelos -> {SALIDA} ({tamano_mb:.1f} MB)")
    print(f"  dias        : {salida['DiaCalendario'].min()}-{salida['DiaCalendario'].max()}")
    print(f"  aerolineas  : {salida['Airline'].nunique()}")
    print(f"  rutas       : {salida['Ruta'].nunique()}")
    print(f"  tasa retraso: {salida['Delay'].mean():.4f}")


if __name__ == "__main__":
    main()

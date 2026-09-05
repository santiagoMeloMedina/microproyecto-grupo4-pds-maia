"""Empaqueta lo minimo que el notebook de modelado necesita para correr en Colab.

Sirve para llevar el codigo a Colab sin tener que publicar la rama en GitHub.
No incluye el dataset (el notebook lo reconstruye desde OpenML), ni el entorno
virtual, ni los artefactos: solo codigo, unos pocos kilobytes.

Uso, desde la raiz del repositorio:

    python scripts/empaquetar_colab.py

Genera proyecto.zip en el directorio padre del repositorio. En Colab hay que
subirlo a /content/ y la celda de arranque lo descomprime sola.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NOMBRE_RAIZ = RAIZ.name
DESTINO = RAIZ.parent / "proyecto.zip"

ARCHIVOS = [
    "airlines_ml/__init__.py",
    "airlines_ml/data.py",
    "airlines_ml/features.py",
    "airlines_ml/modeling.py",
    "airlines_ml/baselines.py",
    "airlines_ml/tracking.py",
    "modeling/requirements.txt",
    "scripts/windows/rebuild_dataset.py",
]

# Carpetas que el notebook espera encontrar al guardar sus salidas.
CARPETAS = ["data", "models", "dashboard/data", "docs/2nd_delivery/images"]


def main() -> int:
    faltantes = [r for r in ARCHIVOS if not (RAIZ / r).exists()]
    if faltantes:
        print("Faltan archivos:", ", ".join(faltantes))
        return 1

    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as z:
        for relativo in ARCHIVOS:
            z.write(RAIZ / relativo, f"{NOMBRE_RAIZ}/{relativo}")
        for carpeta in CARPETAS:
            z.writestr(f"{NOMBRE_RAIZ}/{carpeta}/.gitkeep", "")

    print(f"{DESTINO}  ({DESTINO.stat().st_size / 1024:.0f} KB, {len(ARCHIVOS)} archivos)")
    print("Subirlo a /content/ en Colab, junto con el notebook.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

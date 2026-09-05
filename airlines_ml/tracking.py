"""Configuracion de MLflow.

El servidor de seguimiento se resuelve por variable de entorno, de modo que el
mismo notebook corra sin cambios contra SQLite local durante el desarrollo y
contra la instancia EC2 cuando se quiere consolidar resultados.

Tres formas de configurarlo, en orden de precedencia:

    1. Variable de entorno ya definida en la sesion:
       export MLFLOW_TRACKING_URI="http://<ip-ec2>:5000"   # macOS / Linux / Git Bash
       $env:MLFLOW_TRACKING_URI = "http://<ip-ec2>:5000"   # PowerShell, sesion actual
       setx MLFLOW_TRACKING_URI "http://<ip-ec2>:5000"     # Windows, terminal nueva

    2. Un archivo `.env` en la raiz del repositorio (recomendado, ver .env.example).
       Esta en .gitignore, asi que la IP de cada quien no viaja al repositorio.

    3. Si no hay ninguna, SQLite local en `mlflow.db`.
"""
from __future__ import annotations

import os
from pathlib import Path

import mlflow

EXPERIMENTO_POR_DEFECTO = "airlines-retrasos"


def cargar_env(ruta: Path | None = None) -> dict[str, str]:
    """Lee un `.env` sencillo (CLAVE=valor por linea) y lo pasa al entorno.

    Se implementa a mano en vez de usar python-dotenv para no sumar una
    dependencia por diez lineas. Las variables ya definidas en el entorno tienen
    precedencia: el archivo es el valor por defecto, no una imposicion.
    """
    ruta = ruta or Path(__file__).resolve().parents[1] / ".env"
    leidas: dict[str, str] = {}
    if not ruta.exists():
        return leidas

    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        clave, valor = clave.strip(), valor.strip().strip('"').strip("'")
        if clave and not os.getenv(clave):
            os.environ[clave] = valor
            leidas[clave] = valor
    return leidas


def configurar(experimento: str = EXPERIMENTO_POR_DEFECTO) -> str:
    """Apunta MLflow al servidor configurado y devuelve la URI en uso.

    Sin variable de entorno se usa SQLite local. MLflow 3 dejo en mantenimiento
    el backend de archivos plano ('./mlruns'), y SQLite ademas replica el tipo de
    backend que corre el servidor en EC2, asi que lo que se prueba localmente se
    comporta igual al consolidar.
    """
    cargar_env()
    uri = os.getenv("MLFLOW_TRACKING_URI")

    if not uri:
        raiz = Path(__file__).resolve().parents[1]
        (raiz / "mlartifacts").mkdir(exist_ok=True)
        uri = f"sqlite:///{(raiz / 'mlflow.db').as_posix()}"

    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(experimento)
    return uri


def es_remoto() -> bool:
    uri = mlflow.get_tracking_uri()
    return uri.startswith("http://") or uri.startswith("https://")

"""Carga y validacion de config.yml.

El YAML se valida contra un esquema de pydantic al importarse: si falta un campo
o cambia de tipo, el paquete falla al arrancar y no a mitad de un entrenamiento.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import BaseModel
from strictyaml import YAML, load

import model_riesgo_retraso

PACKAGE_ROOT = Path(model_riesgo_retraso.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_models"


class AppConfig(BaseModel):
    """Configuracion de nivel aplicacion: nombres de archivos y paquete."""

    package_name: str
    training_data_file: str
    pipeline_save_file: str


class ModelConfig(BaseModel):
    """Configuracion del modelo: variables, particion y punto de operacion."""

    target: str
    features: List[str]
    temp_features: List[str]

    dia_fin_entrenamiento: int
    dia_fin_validacion: int
    total_dias: int

    umbral: float
    banda_alta: float

    random_state: int
    n_estimators: int
    max_depth: int
    learning_rate: float
    subsample: float
    colsample_bytree: float
    min_child_weight: int
    reg_lambda: float


class Config(BaseModel):
    """Objeto de configuracion maestro.

    El campo se llama `modelo` y no `model_config` porque pydantic v2 reserva el
    prefijo `model_` para sus propios atributos de clase.
    """

    app_config: AppConfig
    modelo: ModelConfig


def find_config_file() -> Path:
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise OSError(f"No se encontro el archivo de configuracion en {CONFIG_FILE_PATH!r}")


def fetch_config_from_yaml(cfg_path: Path | None = None) -> YAML:
    """Lee config.yml y lo devuelve como objeto YAML."""
    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, encoding="utf-8") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config
    raise OSError(f"No se pudo leer la configuracion en {cfg_path!r}")


def create_and_validate_config(parsed_config: YAML | None = None) -> Config:
    """Valida los valores del YAML contra el esquema."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    # strictyaml devuelve todo como texto: pydantic hace la conversion de tipos.
    return Config(
        app_config=AppConfig(**parsed_config.data),
        modelo=ModelConfig(**parsed_config.data),
    )


def training_data_path() -> Path:
    """Ubica data/airlines.csv.

    El dataset no viaja dentro del wheel: son 19 MB versionados con DVC. La ruta
    se resuelve en tres pasos porque el paquete se usa de dos formas distintas.
    Desde el codigo fuente, `ROOT.parent` es la raiz del repositorio; pero una
    vez instalado con pip, ROOT apunta a site-packages y esa ruta no existe, asi
    que se prueba tambien contra el directorio de trabajo.
    """
    ruta_env = os.getenv("AIRLINES_CSV")
    if ruta_env:
        return Path(ruta_env)

    nombre = config.app_config.training_data_file
    candidatos = [
        ROOT.parent / "data" / nombre,        # ejecutando desde model-pkg/
        Path.cwd() / "data" / nombre,         # ejecutando desde la raiz del repo
        Path.cwd().parent / "data" / nombre,  # ejecutando desde un subdirectorio
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato

    # Ninguno existe: se devuelve el primero para que el mensaje de error de
    # cargar_dataset apunte a una ruta comprensible.
    return candidatos[0]


config = create_and_validate_config()

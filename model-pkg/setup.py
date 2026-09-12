"""Construccion del wheel del modelo de riesgo de retraso.

    python -m build

produce dist/model_riesgo_retraso-<VERSION>-py3-none-any.whl, que incluye el
pipeline ya entrenado. Instalarlo basta para predecir: no hace falta el
repositorio, ni el CSV, ni tener airlines_ml en el PYTHONPATH.
"""
from pathlib import Path

from setuptools import find_packages, setup

NAME = "model_riesgo_retraso"
DESCRIPTION = "Modelo de riesgo de retraso por franja de itinerario."
URL = "https://github.com/santiagoMeloMedina/microproyecto-grupo4-pds-maia"
EMAIL = "k.rodriguezs2@uniandes.edu.co"
AUTHOR = "Grupo 4 - MAIA Proyecto de Desarrollo de Soluciones"
REQUIRES_PYTHON = ">=3.10.0"

here = Path(__file__).resolve().parent

try:
    long_description = (here / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = DESCRIPTION

# La version vive en un solo archivo, que tambien lee el paquete en tiempo de
# ejecucion. Asi el wheel y model_riesgo_retraso.__version__ nunca se separan.
ROOT_DIR = here
PACKAGE_DIR = ROOT_DIR / NAME
about: dict = {}
about["__version__"] = (PACKAGE_DIR / "VERSION").read_text(encoding="utf-8").strip()


def list_reqs(fname="requirements.txt"):
    with open(ROOT_DIR / "requirements" / fname, encoding="utf-8") as fd:
        return [
            line.strip()
            for line in fd.readlines()
            if line.strip() and not line.startswith("#")
        ]


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests",)),
    package_data={
        NAME: [
            "VERSION",
            "config.yml",
            "trained_models/*.pkl",
            "trained_models/metadata.json",
        ]
    },
    install_requires=list_reqs(),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

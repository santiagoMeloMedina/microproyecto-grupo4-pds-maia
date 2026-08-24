# Microproyecto

## Instalación

Requisitos: Python 3.

```bash
make install
```

Esto crea un entorno virtual en `.venv/` e instala `dvc[s3]` dentro de él.

`make install` no deja el entorno activado en tu shell. Para poder usar los comandos instalados (por ejemplo `dvc`), actívalo manualmente después:

```bash
source .venv/bin/activate
```

Repite este `source .venv/bin/activate` cada vez que abras una terminal nueva y quieras seguir usando el proyecto. Para salir del entorno virtual: `deactivate`.

## Actualizar datos

Cuando se agregue nueva data que deba ser versionada como datos (archivos grandes), debe:

1. Incluirse dentro de la carpeta `data/`.
2. Versionarse con `dvc add <archivo>`.
3. Subirse al remote con `dvc push`.

Esto se puede hacer automáticamente con el siguiente comando de Makefile:

```bash
make update-data
```

Este comando corre `scripts/update_data.sh`, que:

1. Lista los archivos que hay en `data/`.
2. Pregunta, uno por uno, si se quiere versionar cada archivo con DVC (`dvc add`).
3. Al final, pregunta si se quiere hacer `dvc push` de todo lo versionado en esa corrida.

## Exploración

Ver [exploration/README.md](exploration/README.md) para cómo importar los datos y correr notebooks de exploración.

## Datos y licencia

El dataset `data/airlines.csv` proviene de [OpenML - Airlines dataset](https://www.openml.org/search?type=data&sort=runs&id=1169&status=active) y está distribuido bajo licencia **ODC-PDDL** (Open Data Commons Public Domain Dedication and License v1.0), según lo verificado en [datahub.io/core/openml-datasets/data/airlines](https://datahub.io/core/openml-datasets/data/airlines). Esta licencia permite el uso, copia, modificación y distribución de los datos sin restricciones.

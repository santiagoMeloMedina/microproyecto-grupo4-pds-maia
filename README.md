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

### Windows

Los comandos de arriba son para macOS y Linux. En Windows `install.sh` no funciona: `python3` no existe como comando y el entorno virtual se crea en `.venv\Scripts\` y no en `.venv/bin/`. Hay equivalentes en PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\install.ps1
.\.venv\Scripts\Activate.ps1
```

Quien tenga GNU Make en Windows puede conservar el mismo flujo con `make -f scripts/windows/Makefile install`.

Ver [scripts/windows/README.md](scripts/windows/README.md) para el detalle, incluidas las alternativas para obtener el dataset.

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

En Windows el equivalente es:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\update_data.ps1
```

O bien `make -f scripts/windows/Makefile update-data`.

## Documentación de la entrega

Los reportes y soportes de cada entrega viven en `docs/`:

- [docs/1st_delivery/reporte_entrega1.md](docs/1st_delivery/reporte_entrega1.md) — reporte entregado en la Entrega 1.
- [docs/1st_delivery/repository_configuration.md](docs/1st_delivery/repository_configuration.md) — evidencia de la creación del repositorio GitHub, el bucket S3 y la configuración de DVC, con capturas en `docs/1st_delivery/images/`.
- [docs/2nd_delivery/borrador_entrega2.md](docs/2nd_delivery/borrador_entrega2.md) — borrador con hallazgos posteriores a la Entrega 1, insumo para la Entrega 2.

## Exploración

Ver [exploration/README.md](exploration/README.md) para cómo importar los datos y correr notebooks de exploración.

## Datos y licencia

El dataset `data/airlines.csv` proviene de [OpenML - Airlines dataset](https://www.openml.org/search?type=data&sort=runs&id=1169&status=active) y está distribuido bajo licencia **ODC-PDDL** (Open Data Commons Public Domain Dedication and License v1.0), según lo verificado en [datahub.io/core/openml-datasets/data/airlines](https://datahub.io/core/openml-datasets/data/airlines). Esta licencia permite el uso, copia, modificación y distribución de los datos sin restricciones.

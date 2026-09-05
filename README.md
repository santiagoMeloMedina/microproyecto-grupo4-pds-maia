# Microproyecto

## Instalación

Requisitos: Python 3.

```bash
make install
```

En sistemas basados en Ubuntu (24.04), `make install` primero instala las dependencias de sistema necesarias vía `apt` (`make`, `python3-pip`, `python3-venv`, `libgomp1` — esta última requerida por LightGBM) antes de crear el entorno virtual. Este paso se salta automáticamente si `apt-get` no está disponible.

Luego crea un entorno virtual en `.venv/` e instala `dvc[s3]` dentro de él.

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
- [docs/2nd_delivery/reporte_entrega2.md](docs/2nd_delivery/reporte_entrega2.md) — reporte de la Entrega 2: modelos, evaluación y tablero.
- [docs/2nd_delivery/reporte_trabajo_equipo.md](docs/2nd_delivery/reporte_trabajo_equipo.md) — reporte de trabajo en equipo de la Entrega 2.
- [docs/2nd_delivery/borrador_entrega2.md](docs/2nd_delivery/borrador_entrega2.md) — hallazgos de EDA posteriores a la Entrega 1.
- [docs/2nd_delivery/mlflow_ec2.md](docs/2nd_delivery/mlflow_ec2.md) — montaje del servidor de MLflow en EC2 y capturas requeridas.
- [docs/2nd_delivery/ejecutar_en_colab.md](docs/2nd_delivery/ejecutar_en_colab.md) — cómo correr el notebook de modelado en Google Colab con GPU.
- [docs/3rd_delivery/borrador_entrega3.md](docs/3rd_delivery/borrador_entrega3.md) — borrador de la Entrega 3: API, contenedores y pendientes.

## Exploración

Ver [exploration/README.md](exploration/README.md) para cómo importar los datos y correr notebooks de exploración.

## Modelado y tablero

El código de preparación de datos vive en [airlines_ml/](airlines_ml/), que comparten el notebook de
entrenamiento y el tablero. Así el modelo recibe al servir exactamente las mismas columnas con las
que se entrenó.

```
airlines_ml/     preparación de datos, features, modelos y líneas base
modeling/        notebook de entrenamiento y experimentos (MLflow)
dashboard/       tablero Dash
```

### 1. Entrenar

```bash
pip install -r modeling/requirements.txt
jupyter lab modeling/katherin-modelos-entrega2.ipynb
```

Ejecuta 90 experimentos, los registra en MLflow y produce `models/modelo_ganador.joblib`,
`models/metadata.json` y `dashboard/data/vuelos.parquet`. Para consolidar los experimentos en el
servidor del equipo, exporta `MLFLOW_TRACKING_URI` antes de abrir el notebook — ver
[docs/2nd_delivery/mlflow_ec2.md](docs/2nd_delivery/mlflow_ec2.md).

### 2. Levantar el tablero

```bash
pip install -r dashboard/requirements.txt
python dashboard/app.py
```

Queda en http://localhost:8050. Requiere haber ejecutado antes el notebook, que es el que genera el
modelo y el parquet.

## Datos y licencia

El dataset `data/airlines.csv` proviene de [OpenML - Airlines dataset](https://www.openml.org/search?type=data&sort=runs&id=1169&status=active) y está distribuido bajo licencia **ODC-PDDL** (Open Data Commons Public Domain Dedication and License v1.0), según lo verificado en [datahub.io/core/openml-datasets/data/airlines](https://datahub.io/core/openml-datasets/data/airlines). Esta licencia permite el uso, copia, modificación y distribución de los datos sin restricciones.

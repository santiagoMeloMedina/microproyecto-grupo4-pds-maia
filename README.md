# Microproyecto

## Instalación

Requisitos: Python 3.

```bash
make install
```

En sistemas basados en Ubuntu (24.04), `make install` primero instala las dependencias de sistema necesarias vía `apt` (`make`, `python3-pip`, `python3-venv`, `libgomp1` — esta última requerida por las bibliotecas de árboles usadas en los experimentos y por XGBoost en la solución final) antes de crear el entorno virtual. Este paso se salta automáticamente si `apt-get` no está disponible.

Luego crea un entorno virtual en `.venv/` e instala las dependencias de
exploración, modelado y `dvc[s3]` dentro de él.

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
- [docs/3rd_delivery/reporte_entrega3.md](docs/3rd_delivery/reporte_entrega3.md) — reporte de la Entrega Final: modelos, empaquetamiento, API, tablero y despliegue.
- [docs/3rd_delivery/manual_usuario.md](docs/3rd_delivery/manual_usuario.md) — manual de usuario del tablero.
- [docs/3rd_delivery/manual_instalacion.md](docs/3rd_delivery/manual_instalacion.md) — manual de instalación y despliegue.
- [docs/3rd_delivery/reporte_trabajo_equipo.md](docs/3rd_delivery/reporte_trabajo_equipo.md) — reporte de trabajo en equipo de la Entrega Final.
- [docs/api_endpoints.md](docs/api_endpoints.md) — documentación de los endpoints de la API: descripción, payload y respuesta de ejemplo.

## Exploración

Ver [exploration/README.md](exploration/README.md) para cómo importar los datos y correr notebooks de exploración.

## Modelado y tablero

El código de preparación de datos vive en [airlines_ml/](airlines_ml/), que comparten el notebook de
entrenamiento y el tablero. Así el modelo recibe al servir exactamente las mismas columnas con las
que se entrenó.

```
airlines_ml/     experimentación: preparación de datos, features, familias y líneas base
modeling/        notebook de entrenamiento y 90 experimentos (MLflow)
model-pkg/       producción: paquete instalable con el modelo ganador
api/             API de inferencia (FastAPI)
ui/              tablero React que consume la API
dashboard/       tablero Dash de la Entrega 2 y tableros descriptivos
```

`airlines_ml` y `model-pkg` tienen propósitos distintos: el primero responde *qué modelo elegir* y
contiene las tres familias; el segundo responde *cuál es el riesgo de este itinerario* y contiene
solo la configuración ganadora, sin depender del repositorio, de modo que se instale en un
contenedor con un único `pip install`.

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

### 3. Levantar el prototipo desplegable (API + tablero React)

Es el entregable de la Entrega Final. No requiere ejecutar el notebook ni descargar el dataset: el
modelo entrenado viaja dentro del wheel en `api/model-package/` y el histórico está versionado en
`dashboard/data/vuelos.parquet`.

```bash
docker compose up --build
```

| Servicio | Dirección |
|---|---|
| Tablero | http://localhost:8080 |
| API | http://localhost:8002/docs |

Si el puerto 8080 está ocupado, `UI_PORT=8088 docker compose up --build`.

Para desarrollar sin Docker:

Terminal 1:

```bash
(cd api && tox run -e run)    # API en http://localhost:8002
```

Terminal 2:

```bash
(cd ui && npm ci && npm run dev)  # tablero en http://localhost:5173
```

Ver el [manual de instalación](docs/3rd_delivery/manual_instalacion.md), [api/README.md](api/README.md)
y [docs/api_endpoints.md](docs/api_endpoints.md).

### 4. Desplegar en AWS con Terraform y ECS

El PR #13 incorporó infraestructura como código para crear repositorios ECR, un
clúster ECS sobre EC2, servicios independientes para API y tablero, IP elástica
y logs en CloudWatch.

```bash
cd infra
cp .env.example .env
# editar VPC_ID y SUBNET_ID
cd ..
./infra/scripts/build_and_push.sh
```

Requiere Terraform 1.5+, AWS CLI autenticada y Docker. Ver el procedimiento,
las verificaciones, evidencias y limpieza de recursos en el
[manual de instalación](docs/3rd_delivery/manual_instalacion.md) y los detalles
técnicos en [infra/README.md](infra/README.md).

### 5. Reentrenar y reempaquetar el modelo

El modelo de producción se distribuye como paquete instalable, construido en
[`model-pkg/`](model-pkg/). Solo hace falta si se quiere regenerar el artefacto.

```bash
dvc pull                                 # descarga data/airlines.csv

cd model-pkg
python -m pip install tox build
tox run -e test_package                  # entrena y valida
python -m build                          # genera dist/*.whl
cp dist/*.whl ../api/model-package/
```

Ver [model-pkg/README.md](model-pkg/README.md).

## Datos y licencia

El dataset `data/airlines.csv` proviene de [OpenML - Airlines dataset](https://www.openml.org/search?type=data&sort=runs&id=1169&status=active) y está distribuido bajo licencia **ODC-PDDL** (Open Data Commons Public Domain Dedication and License v1.0), según lo verificado en [datahub.io/core/openml-datasets/data/airlines](https://datahub.io/core/openml-datasets/data/airlines). Esta licencia permite el uso, copia, modificación y distribución de los datos sin restricciones.

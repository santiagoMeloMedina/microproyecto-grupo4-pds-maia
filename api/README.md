# API de riesgo de retraso

FastAPI que sirve el modelo empaquetado y la analítica histórica mediante
endpoints REST. Es el backend del tablero React en [`ui/`](../ui/), que consume
la predicción y los endpoints de priorización. El tablero Dash de
[`dashboard/app.py`](../dashboard/app.py) se conserva como antecedente de la
Entrega 2.

Estructura adaptada a este proyecto y a pydantic v2:

```
api/
  app/
    main.py, config.py, api.py   FastAPI app, settings, rutas
    schemas/                     modelos de request/response (pydantic)
    services/
      artifacts.py                carga el modelo, metadata.json y vuelos.parquet
      slots.py                    filtrado y agregacion de franjas de itinerario
  tests/                          pytest con artefactos falsos (no requieren el modelo real)
```

## Artefactos requeridos

Ninguno que haya que generar a mano. El modelo viaja dentro del paquete
`model_riesgo_retraso`, que se instala desde el wheel en `model-package/`, y el histórico de
vuelos está versionado en `dashboard/data/vuelos.parquet`.

Es lo que permite construir la imagen desde un clon limpio: antes la API deserializaba
`models/modelo_ganador.joblib` con `joblib.load` e insertaba la raíz del repositorio en `sys.path`
para que el pickle encontrara `airlines_ml`, de modo que dependía de archivos que no estaban en
git y de la estructura del repositorio.

Para regenerar el wheel, ver [model-pkg/README.md](../model-pkg/README.md). Para
regenerar el parquet, instalar el wheel recién construido y un motor parquet, y
ejecutar el script desde la raíz:

```bash
python -m pip install --force-reinstall model-pkg/dist/*.whl pyarrow
python scripts/generar_datos_tablero.py
```

## Levantar la API

Con tox, que crea su propio entorno virtual e instala el paquete del modelo:

```bash
cd api
pip install tox
tox run -e run
```

Queda en `http://localhost:8002`. Docs interactivas en `http://localhost:8002/docs`.

Para correr las pruebas:

```bash
tox run -e test_app
```

## Levantar la API con Docker

El contexto de build es la raíz del repositorio, no `api/`, porque la imagen necesita también
`dashboard/data/vuelos.parquet`. Este archivo está versionado y debe existir en
esa ruta; no se debe excluir ni ejecutar el build desde la carpeta `api/`.

```bash
docker build -f api/Dockerfile -t airlines-api .
docker run -p 8002:8002 airlines-api
```

Lo habitual es levantarla junto al tablero con Docker Compose desde la raíz:

```bash
docker compose up --build
```

Queda en `http://localhost:8002`, igual que con uvicorn local.

## Pruebas

```bash
pip install -r api/test_requirements.txt
cd api && PYTHONPATH=. pytest tests -v
```

Las pruebas sustituyen `get_artifacts()` por un stub en memoria (`tests/conftest.py`), así que
no requieren el modelo real ni el parquet.

## Endpoints

Prefijo `/api/v1`. Todas las respuestas usan camelCase (pensado para consumirse desde `ui/`).

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/health` | Versión de la API, **versión del paquete del modelo**, familia y umbrales de riesgo. |
| GET | `/catalog` | Aerolíneas, aeropuertos, rutas frecuentes y días válidos, derivados del histórico — alimenta el formulario de predicción. |
| POST | `/predict` | Riesgo estimado para un itinerario (`airline`, `airportFrom`, `airportTo`, `dayOfWeek`, `time`, `length`), con tasas históricas de referencia. Equivalente al callback `evaluar` de `dashboard/app.py`. |
| GET | `/schedule-slots` | Franjas de itinerario (aerolínea × ruta × día × franja horaria) ordenadas por riesgo, con los mismos cuatro filtros del tablero Dash (`airline`, `route`, `dayOfWeek`, `slot`). |
| GET | `/schedule-slots/summary` | KPIs de la selección activa: tasa de retraso, vuelos, franjas y AUC del modelo. |

`POST /predict` rechaza con `422` si `airportFrom == airportTo`. Los demás filtros son opcionales;
sin filtros, se calculan sobre todo el histórico.

## Qué consume el tablero y qué no

`ui/` consume `/catalog` y `/predict` en la página de predicción, y `/schedule-slots` con
`/schedule-slots/summary` en la vista de franjas a reforzar.

Las tres vistas descriptivas (`operational_prioritization`, `strategic_overview`,
`tactical_diagnosis`, en `ui/public/widgets/`) siguen siendo HTML estático generado por
`dashboard/descriptive/generate_all.py`: no las sirve esta API.

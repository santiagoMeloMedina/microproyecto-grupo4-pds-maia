# API de riesgo de retraso

FastAPI que disponibiliza, como endpoints REST, el modelo y la analítica que hoy vive en
[`dashboard/app.py`](../dashboard/app.py) (tablero Dash). Sirve al tablero React en
[`ui/`](../ui/), que consume `/predict` desde `ui/src/services/predictionService.ts`.

Estructura (basada en [`bankchurn-api/`](../bankchurn-api/), adaptada a este proyecto y a
pydantic v2):

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

La API carga los mismos artefactos que `dashboard/app.py`, y con la misma convención: no se
versionan en git (ver `.gitignore` en la raíz) y se generan ejecutando el notebook de modelado.

```bash
pip install -r modeling/requirements.txt
jupyter lab modeling/katherin-modelos-entrega2.ipynb
```

Esto produce `models/modelo_ganador.joblib`, `models/metadata.json` (versionado) y
`dashboard/data/vuelos.parquet`. Si faltan, la API falla al arrancar con un mensaje indicando
qué archivo falta.

## Levantar la API

```bash
python -m venv .venv-api && source .venv-api/bin/activate   # entorno propio, Python 3.10+
pip install -r api/requirements.txt
cd api && uvicorn app.main:app --reload --port 8002
```

Queda en `http://localhost:8002`. Docs interactivas en `http://localhost:8002/docs`.

`api/requirements.txt` fija `numpy`/`scipy`/`xgboost` en las mismas versiones que
`dashboard/requirements.txt`, que requieren Python 3.10+. El `.venv/` de la raíz del repo usa
Python 3.9 (ver `.venv/pyvenv.cfg`), por eso la API necesita su propio entorno virtual y no
puede compartir el de `make install`.

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
| GET | `/health` | Familia del modelo cargado y umbrales de riesgo. |
| GET | `/catalog` | Aerolíneas, aeropuertos, rutas frecuentes y días válidos, derivados del histórico — alimenta el formulario de predicción. |
| POST | `/predict` | Riesgo estimado para un itinerario (`airline`, `airportFrom`, `airportTo`, `dayOfWeek`, `time`, `length`), con tasas históricas de referencia. Equivalente al callback `evaluar` de `dashboard/app.py`. |
| GET | `/schedule-slots` | Franjas de itinerario (aerolínea × ruta × día × franja horaria) ordenadas por riesgo, con los mismos cuatro filtros del tablero Dash (`airline`, `route`, `dayOfWeek`, `slot`). |
| GET | `/schedule-slots/summary` | KPIs de la selección activa: tasa de retraso, vuelos, franjas y AUC del modelo. |
| GET | `/schedule-slots/breakdown` | Tasa de retraso agrupada por `by=airline\|slot\|day`, con volumen. |
| GET | `/schedule-slots/drift` | Evolución diaria de la tasa de retraso en la selección (deriva del modelo). |

`POST /predict` rechaza con `422` si `airportFrom == airportTo`. Los demás filtros son opcionales;
sin filtros, se calculan sobre todo el histórico.

## Qué no cambia todavía

Las tres vistas descriptivas de `ui/` (`operational_prioritization`, `strategic_overview`,
`tactical_diagnosis`, en `ui/public/widgets/`) siguen siendo HTML estático generado por
`dashboard/descriptive/generate_all.py`; no las sirve esta API. Los endpoints de
`/schedule-slots` cubren la analítica del tablero Dash, que hoy no tiene equivalente en `ui/`.

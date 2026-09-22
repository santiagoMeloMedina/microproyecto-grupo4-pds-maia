# API — Airline Delay Risk

Base URL local: `http://localhost:8002`
Prefijo de todos los endpoints listados: `/api/v1`
Documentación interactiva (Swagger): `/docs`

Todas las respuestas JSON usan **camelCase** (los modelos internos son snake_case, expuestos vía `CamelModel`).

---

## GET `/api/v1/health`

**Qué hace:** devuelve el estado de la API y del modelo de riesgo cargado (familia del modelo y umbrales de banda de riesgo).

**Payload:** ninguno (sin parámetros).

**Respuesta 200:**
```json
{
  "name": "Airline Delay Risk API",
  "apiVersion": "0.1.0",
  "modelVersion": "0.0.1",
  "modelFamily": "xgboost",
  "threshold": 0.5529,
  "highBandThreshold": 0.6891
}
```

---

## GET `/api/v1/catalog`

**Qué hace:** devuelve las aerolíneas, aeropuertos, rutas frecuentes (≥ 500 vuelos históricos) y días válidos, usados para poblar el formulario de predicción y los filtros del tablero.

**Payload:** ninguno (sin parámetros).

**Respuesta 200:**
```json
{
  "airlines": ["AA", "DL", "UA", "WN"],
  "airports": ["DAL", "HOU", "JFK", "LAX"],
  "routes": ["DAL-HOU", "JFK-LAX"],
  "days": [
    { "value": 1, "label": "Lunes" },
    { "value": 2, "label": "Martes" },
    { "value": 3, "label": "Miercoles" },
    { "value": 4, "label": "Jueves" },
    { "value": 5, "label": "Viernes" },
    { "value": 6, "label": "Sabado" },
    { "value": 7, "label": "Domingo" }
  ]
}
```

---

## POST `/api/v1/predict`

**Qué hace:** calcula la probabilidad de retraso para un itinerario puntual (aerolínea, ruta, día, hora, duración) y la clasifica en una banda de riesgo (`bajo` / `medio` / `alto`). Incluye tasas históricas de referencia (por aerolínea, ruta, franja horaria y media global) para contextualizar el número. Es el equivalente al callback `evaluar` de `dashboard/app.py`.

**Payload válido** (`PredictionRequest`):
```json
{
  "airline": "WN",
  "airportFrom": "DAL",
  "airportTo": "HOU",
  "dayOfWeek": 3,
  "time": 840,
  "length": 60
}
```

Campos:
- `airline` (string, requerido): código IATA de la aerolínea, p.ej. `"WN"`.
- `airportFrom` (string, requerido): aeropuerto de origen (IATA).
- `airportTo` (string, requerido): aeropuerto de destino (IATA). Debe ser distinto de `airportFrom`.
- `dayOfWeek` (int, requerido): 1 (lunes) a 7 (domingo).
- `time` (int, requerido): minutos desde medianoche, entre 0 y 1439.
- `length` (int, requerido): duración estimada del vuelo en minutos, > 0.

**Respuesta 200 ilustrativa** (`PredictionResult`):
```json
{
  "probability": 0.42,
  "band": "medio",
  "threshold": 0.5529,
  "highBandThreshold": 0.6891,
  "references": [
    { "label": "Historico WN", "rate": 0.38 },
    { "label": "Historico DAL-HOU", "rate": 0.35 },
    { "label": "Historico franja 12-18", "rate": 0.4 },
    { "label": "Media global", "rate": 0.37 }
  ],
  "modelVersion": "0.0.1"
}
```

**Errores:**
- `400 Bad Request` si ocurre un error durante la inferencia del modelo:
  ```json
  { "detail": "<mensaje del error original>" }
  ```
- `422 Unprocessable Entity` si falla la validación del payload (campo faltante, `airportFrom == airportTo`, rangos fuera de límite, etc.).

---

## GET `/api/v1/schedule-slots`

**Qué hace:** devuelve las franjas de itinerario (combinación aerolínea + ruta + día + franja horaria) con mayor riesgo estimado por el modelo, ordenadas de forma descendente. Es la vista operativa para priorizar sobre qué franjas reforzar.

**Query params** (todos opcionales salvo `limit` que tiene default):
- `airline` (string)
- `route` (string, formato `"ORIGEN-DESTINO"`, p.ej. `"DAL-HOU"`)
- `dayOfWeek` (int, 1–7)
- `slot` (string, uno de `"00-06"`, `"06-12"`, `"12-18"`, `"18-24"`)
- `limit` (int, 1–200, default `20`)

**Ejemplo de request:**
```
GET /api/v1/schedule-slots?airline=WN&route=DAL-HOU&dayOfWeek=3&limit=5
```

**Respuesta 200** (lista de `ScheduleSlot`):
```json
[
  {
    "airline": "WN",
    "route": "DAL-HOU",
    "airportFrom": "DAL",
    "airportTo": "HOU",
    "dayOfWeek": 3,
    "dayLabel": "Miercoles",
    "slot": "12-18",
    "time": 840,
    "length": 60,
    "flights": 32,
    "observedRate": 0.41,
    "risk": 0.58,
    "band": "medio"
  }
]
```
Si no hay coincidencias, devuelve `[]`.

---

## GET `/api/v1/schedule-slots/summary`

**Qué hace:** devuelve los KPIs agregados de la selección activa (misma combinación de filtros que `/schedule-slots`): tasa de retraso observada, vuelos en la selección, total de vuelos históricos, número de franjas, franjas sobre el umbral de riesgo y el AUC del modelo.

**Query params** (todos opcionales): `airline`, `route`, `dayOfWeek` (1–7), `slot`.

**Ejemplo de request:**
```
GET /api/v1/schedule-slots/summary?airline=WN
```

**Respuesta 200** (`SlotsSummary`):
```json
{
  "delayRate": 0.39,
  "flightsInSelection": 1520,
  "totalFlights": 58000,
  "scheduleSlots": 84,
  "slotsOverThreshold": 12,
  "slotsInSelection": 84,
  "rocAuc": 0.71,
  "threshold": 0.5
}
```
Si la selección no tiene vuelos, `delayRate` y `flightsInSelection`/`scheduleSlots`/`slotsInSelection` son `null`/`0`, manteniendo `totalFlights`, `rocAuc` y `threshold` globales.

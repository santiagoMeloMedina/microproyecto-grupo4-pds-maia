# Exploración propuesta - Entrega 2

Pregunta de negocio: ¿Qué combinaciones de aerolínea, ruta, día y franja horaria concentran el mayor riesgo de retraso, de modo que el equipo de planeación pueda reforzar recursos y ajustar márgenes de conexión en los itinerarios más expuestos?

## Variables a utilizar

- `Airline`
- `AirportFrom` + `AirportTo` → combinadas en una nueva variable `Ruta`
- `DayOfWeek`
- `Time` → discretizada en una nueva variable `FranjaHoraria` (bins, ej. madrugada / mañana / tarde / noche)
- `Delay` (variable objetivo)

`Length` y `Flight` no se usan en esta exploración (no están dentro de la pregunta de negocio).

No se usa matriz de correlación: la mayoría de variables son categóricas y la relación de `Time` con `Delay` no es lineal.

## Comparaciones a realizar

### 1. Tasa de retraso individual (con volumen)
- Tasa de retraso vs. volumen por `Airline`.
- Tasa de retraso vs. volumen por `DayOfWeek`.
- Tasa de retraso vs. volumen por `FranjaHoraria`.
- Tasa de retraso vs. volumen por `Ruta` (top-N rutas por volumen).

### 2. Tasa de retraso por combinaciones (heatmaps)
- `FranjaHoraria` × `Airline`
- `FranjaHoraria` × `DayOfWeek`
- `FranjaHoraria` × `Ruta` (top-N rutas por volumen)

### 3. Ranking de combinaciones de mayor riesgo
- Agrupar por (`Airline`, `Ruta`, `DayOfWeek`, `FranjaHoraria`).
- Calcular tasa de retraso y volumen por grupo.
- Filtrar grupos con volumen mínimo (evitar tasas ruidosas por pocos datos).
- Ordenar de mayor a menor tasa de retraso.

## Qué muestra la parte descriptiva del tablero

- Gráficas de tasa de retraso vs. volumen por aerolínea, día de la semana y franja horaria.
- Heatmaps de tasa de retraso cruzando franja horaria con aerolínea, día de la semana y ruta.
- Tabla/ranking de las combinaciones (aerolínea, ruta, día, franja horaria) con mayor tasa de retraso y su volumen respaldando el dato.

## Preguntas que resuelve cada comparación y cómo responden la pregunta de negocio

| Comparación | Pregunta que resuelve | Cómo responde la pregunta de negocio |
|---|---|---|
| Tasa de retraso por `Airline` | ¿Qué aerolíneas tienen mayor tasa de retraso? | Identifica un primer factor de riesgo aislado, insumo para las combinaciones. |
| Tasa de retraso por `DayOfWeek` | ¿Qué días de la semana concentran más retrasos? | Igual que arriba, para el factor día. |
| Tasa de retraso por `FranjaHoraria` | ¿En qué horas del día sube el riesgo de retraso? | Igual que arriba, para el factor horario. |
| Tasa de retraso por `Ruta` (top-N) | ¿Qué rutas de mayor volumen tienen más retrasos? | Igual que arriba, para el factor ruta, limitado a rutas con datos suficientes. |
| Heatmap `FranjaHoraria` × `Airline` | ¿Qué aerolíneas se retrasan más en qué horarios específicos? | Muestra una combinación concreta de riesgo, no visible mirando cada variable por separado. |
| Heatmap `FranjaHoraria` × `DayOfWeek` | ¿Qué días y horarios concentran más retraso juntos? | Igual, para la combinación día-horario. |
| Heatmap `FranjaHoraria` × `Ruta` | ¿Qué rutas se retrasan más en qué horarios? | Igual, para la combinación ruta-horario. |
| Ranking de combinaciones (`Airline`, `Ruta`, `DayOfWeek`, `FranjaHoraria`) | ¿Cuáles son, en conjunto, las combinaciones específicas de mayor riesgo con volumen suficiente para confiar en el dato? | Responde directamente la pregunta de negocio: entrega la lista de itinerarios más expuestos sobre los que el equipo de planeación debe reforzar recursos y ajustar márgenes de conexión. |

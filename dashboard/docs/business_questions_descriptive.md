# Preguntas de negocio de la suite descriptiva

## Propósito

La suite descriptiva transforma los registros históricos de vuelos en una narrativa ejecutiva de
tres niveles. Cada dashboard responde una pregunta distinta y utiliza el resultado anterior como
contexto:

1. **Panorama general:** ¿tenemos un problema?
2. **Patrones tácticos:** ¿dónde se manifiesta?
3. **Priorización:** ¿qué merece atención primero según la evidencia histórica?

El flujo avanza desde la magnitud global hasta los segmentos que concentran más retrasos. Sus
resultados describen patrones observados; no estiman riesgo futuro ni el efecto de una intervención.

## Dashboard 1: Panorama general de los retrasos

### Objetivo

Dimensionar la frecuencia de los retrasos y establecer una línea base a partir de la proporción de
vuelos retrasados y del volumen total de operaciones observadas.

### Pregunta principal

¿Tenemos un problema de retrasos relevante dentro de la operación observada?

### Preguntas de negocio

1. ¿Cuál es la tasa global de retrasos?
2. ¿Qué proporción de vuelos presenta retraso frente a los que no presentan retraso?
3. ¿Cuál es el volumen total de vuelos analizados?
4. ¿Qué diferencia existe entre el volumen de vuelos retrasados y vuelos sin retraso?

### Indicadores y evidencia

- Total de vuelos analizados.
- Total y proporción de vuelos con retraso.
- Total y proporción de vuelos sin retraso.
- Diferencia absoluta y porcentual entre ambos grupos.

### Decisión que informa

Establece la magnitud del problema y el benchmark global que se utiliza como referencia en los
análisis posteriores.

## Dashboard 2: Patrones tácticos de retraso

### Objetivo

Identificar dónde se manifiestan los retrasos y reconocer patrones por operador, momento y
ubicación, considerando conjuntamente la tasa observada y el volumen de vuelos.

### Pregunta principal

¿Dónde se manifiesta el problema de los retrasos?

### Preguntas de negocio

1. ¿Qué aerolíneas presentan mayor exposición a retrasos?
2. ¿En qué franjas horarias aparecen las mayores tasas y volúmenes de retrasos?
3. ¿Qué aeropuertos de origen concentran la mayor exposición y el mayor número de retrasos?
4. ¿Qué patrones de exposición e impacto presentan las rutas frecuentes?
5. ¿Coinciden los segmentos con mayor tasa de retraso con aquellos que acumulan más retrasos?

### Indicadores y evidencia

- Tasa global de retraso como benchmark común.
- Tasa, número de retrasos y volumen de vuelos por aerolínea.
- Tasa y participación de los retrasos por franja horaria.
- Exposición e impacto absoluto por aeropuerto de origen.
- Exposición e impacto absoluto por ruta frecuente.

### Criterios de interpretación

- Los aeropuertos y las rutas se incluyen cuando cuentan con al menos 500 vuelos.
- El día de la semana se excluye de la vista principal porque presenta una variación menor que las
  demás dimensiones analizadas.
- Una tasa alta señala exposición histórica; el volumen permite dimensionar cuántos retrasos se
  observaron.
- Los líderes por tasa y por número de retrasos no necesariamente coinciden.

### Decisión que informa

Orienta la atención hacia las dimensiones y segmentos donde el problema se manifiesta con mayor
intensidad o volumen, sin constituir todavía un orden de prioridad.

## Dashboard 3: Priorización de exposición e impacto

### Objetivo

Ordenar los segmentos de aerolínea y franja horaria que merecen atención por su tasa y volumen
histórico de retrasos, preservando una base muestral suficiente para la comparación.

### Pregunta principal

¿Qué merece atención primero según la evidencia histórica?

### Preguntas de negocio

1. ¿Qué segmentos combinan una tasa de retraso superior al benchmark con un volumen relevante?
2. ¿Qué segmento registra el mayor número histórico de retrasos entre los elegibles?
3. ¿Cuántos retrasos concentran los tres primeros segmentos?
4. ¿Qué proporción acumulada de los retrasos concentran los diez primeros segmentos?
5. ¿Cómo cambia la concentración observada al ampliar progresivamente el número de segmentos?

### Indicadores y evidencia

- Segmento con mayor volumen histórico de retrasos.
- Retrasos y participación acumulada del Top 3.
- Retrasos y participación acumulada del Top 10.
- Matriz de tasa de retraso y volumen absoluto.
- Ranking acumulado por aerolínea y franja horaria.

### Criterios de priorización

- Segmentos formados por la combinación de aerolínea y franja horaria.
- Mínimo de 100 vuelos por segmento.
- Tasa histórica de retraso superior al benchmark global.
- Orden descendente por número absoluto de retrasos observados.

### Decisión que informa

Establece una prioridad de atención analítica basada en concentración histórica. El orden ayuda a
enfocar la revisión ejecutiva, pero no constituye una recomendación operativa validada ni una
estimación de retrasos evitables.

## Alcance analítico

- Los tres dashboards utilizan datos históricos limpios y una definición común de retraso.
- La tasa global funciona como referencia transversal para comparar segmentos.
- **Exposición** significa tasa histórica de retraso.
- **Impacto** significa número absoluto de vuelos retrasados observados; no representa costo,
  severidad, pasajeros afectados ni beneficio atribuible a una acción.
- La priorización del Dashboard 3 ordena evidencia histórica y no representa probabilidad futura.
- Los resultados muestran asociaciones y concentraciones; no demuestran causalidad.

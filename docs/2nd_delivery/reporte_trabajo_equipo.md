# Reporte de trabajo en equipo — Entrega 2

**Micro-proyecto · Proyecto de Desarrollo de Soluciones · MAIA · Grupo 4**

## Distribución de actividades

| Actividad | Responsable | Evidencia |
|---|---|---|
| Replanteamiento de la pregunta de negocio y el alcance | María del Pilar Munoz · Santiago Melo Medina | §1 del reporte |
| Diseño experimental: partición temporal, métricas y líneas base | Katherin Rodríguez Sánchez · Edisson David Prieto | `airlines_ml/data.py`, `airlines_ml/modeling.py`, `airlines_ml/baselines.py` |
| Ingeniería de características | Katherin Rodríguez Sánchez · Edisson David Prieto | `airlines_ml/features.py` |
| Entrenamiento y búsqueda de hiperparámetros (90 experimentos) | Katherin Rodríguez Sánchez · Edisson David Prieto | `modeling/katherin-modelos-entrega2.ipynb` |
| Experimento sobre `Flight` (codificación por objetivo) | Katherin Rodríguez Sánchez · Edisson David Prieto | §12 del notebook, §4 del reporte |
| Montaje del servidor MLflow en EC2 | Katherin Rodríguez Sánchez · Edisson David Prieto | `docs/2nd_delivery/mlflow_ec2.md`, capturas de la UI |
| Registro y comparación de experimentos en MLflow | Katherin Rodríguez Sánchez · Edisson David Prieto | Experimento `airlines-retrasos` |
| Desarrollo del tablero en Dash | María del Pilar Munoz · Santiago Melo Medina | `dashboard/app.py` |
| Soporte de entorno para Windows | Katherin Rodríguez Sánchez | `scripts/windows/` |
| Redacción del reporte de la Entrega 2 | María del Pilar Munoz · Santiago Melo Medina · Katherin Rodríguez Sánchez · Edisson David Prieto | `docs/2nd_delivery/reporte_entrega2.md` |
| Revisión final | María del Pilar Munoz · Santiago Melo Medina · Katherin Rodríguez Sánchez · Edisson David Prieto | — |

## Organización del trabajo

El equipo mantiene una rama por integrante e integra a `main` mediante *pull request* con revisión
de al menos un compañero. Para esta entrega el trabajo se separó en dos ramas:
`feature/katherin-airlines-eda`, con la exploración, y `feature/katherin-modelos-entrega2`, con
modelos y tablero.

## Cómo se atendió la retroalimentación de la Entrega 1

La retroalimentación se convirtió en ítems de trabajo concretos, y cada uno tiene evidencia en el
repositorio:

| Observación recibida | Qué se hizo |
|---|---|
| Cerrar el argumento de para qué sirve el modelo; replantearlo como herramienta de planeación | Se reencuadró todo el producto: pregunta de negocio, punto de operación (presupuesto de refuerzo) y tablero. |
| La pregunta debe mostrar cliente y decisión | Se adoptó la formulación sugerida y se explicitó quién decide, cuándo y sobre qué. |
| Decidir `Flight` con criterio; probar *target encoding* | Se implementó y midió en un experimento controlado. Se documenta por qué se descarta, con evidencia. |
| La matriz de correlación no es la herramienta; usar tasas con volumen por grupo | Se reemplazó por cuatro vistas de tasa **con volumen anotado**, que además alimentan el tablero. |
| Aclarar qué devuelve el módulo de predicción | Devuelve probabilidad, banda de riesgo y acción sugerida, más comparación con el histórico. |
| El KPI de vuelos no debe mostrar el dataset entero | Los indicadores responden a los filtros activos. |
| Revisar el origen del `Delay` de OpenML #1169 | Se documenta la pérdida de la marca temporal y se cuantifica su efecto sobre el techo del modelo. |

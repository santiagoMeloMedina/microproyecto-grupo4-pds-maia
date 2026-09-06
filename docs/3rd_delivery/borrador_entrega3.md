# Borrador — Entrega 3

**Micro-proyecto · Proyecto de Desarrollo de Soluciones · MAIA · Grupo 4**

> **Qué es este documento.** Trabajo ya adelantado que **no forma parte de la Entrega 2** y que
> corresponde a los requisitos de la Entrega 3: empaquetado del modelo, API de inferencia y
> despliegue en contenedores. Se deja documentado para no perderlo y para que el equipo pueda
> repartirse lo que falta.
>
> **Estado del repositorio:** este borrador conserva una propuesta de implementación, pero los
> archivos de API, Streamlit y contenedores que menciona no están versionados en el repositorio
> actual. Las referencias siguientes describen trabajo pendiente y no componentes disponibles.

---

## 1. Qué pide la Entrega 3 y qué está listo

| Requisito | Estado | Dónde |
|---|---|---|
| Repositorio con pipelines de entrenamiento y procesamiento | **Listo** | `airlines_ml/`, `modeling/` |
| Datos versionados en DVC | Parcial | `data/airlines.csv.dvc`. Falta versionar modelo y parquet. |
| Modelos desarrollados | **Listo** | XGBoost seleccionado, 90 experimentos |
| Experimentos en MLflow | **Listo** | Experimento `airlines-retrasos` |
| Modelo empaquetado y desplegado en un API | Pendiente de incorporar | Propuesta: `api/main.py` |
| Artefactos para desplegar en contenedores | Pendiente de incorporar | Propuesta: `api/Dockerfile`, `dashboard/Dockerfile`, `docker-compose.yml` |
| Manual de usuario del tablero | Pendiente | — |
| Manual de instalación | Pendiente | — |
| Video de sustentación (máx. 10 min) | Pendiente | — |
| Reporte de trabajo en equipo | Pendiente | — |

---

## 2. API de inferencia

`api/main.py`, FastAPI con documentación OpenAPI automática en `/docs`.

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/health` | Liveness. Reporta por separado si cargó el modelo y si cargaron los datos, para diagnosticar cuál falta. |
| `GET` | `/metadata` | Ficha del modelo: familia, umbral, métricas, ventana de entrenamiento. |
| `GET` | `/opciones` | Valores válidos de los desplegables. |
| `GET` | `/descriptivo` | Agregados históricos con filtros opcionales. |
| `POST` | `/predecir` | Riesgo de una franja de itinerario, con su contexto histórico. |
| `POST` | `/predecir/lote` | Hasta 5.000 itinerarios, para evaluar una programación completa. |

**Decisiones de diseño**

1. **Los agregados se calculan al vuelo sobre un parquet compacto** (3,0 MB frente a 18,3 MB del
   CSV), no precalculados: los cuatro filtros del tablero se combinan entre sí y precalcular todas
   las combinaciones de aerolínea × ruta × día × franja no es viable.
2. **El modelo se resuelve por variable de entorno**: `MODELO_PATH` para disco o `MLFLOW_MODEL_URI`
   para cargarlo del registro de MLflow. Sustituir el modelo no requiere tocar código.
3. **Las tasas históricas de contexto se cachean**: recalcularlas en cada petición añadiría tres
   agrupaciones sobre 539 mil filas al camino crítico de inferencia.

Estado de pruebas: verificada de punta a punta. `DAL–HOU` de WN devuelve 76,8% (banda alta) y
`LGA–BOS` de DL devuelve 27,8% (banda baja), coherente con el histórico de esas rutas.

---

## 3. Tablero contra la API

La propuesta contemplaba `dashboard/streamlit_app.py` como una versión del tablero que no cargaría
el modelo y consumiría únicamente la API. Ese archivo no está versionado en el repositorio actual.
El enfoque permitiría sustituir el modelo empaquetado sin tocar el front.

Para la Entrega 3 queda por decidir e implementar si el tablero de Dash consumirá la API o si se
desarrollará una versión alternativa. Ninguna de las dos opciones está disponible actualmente como
integración versionada.

---

## 4. Contenedores

La propuesta de `docker-compose.yml` contempla dos servicios con *healthchecks* y versiones fijadas:

```bash
docker compose up --build
# Tablero:  http://localhost:8501
# API:      http://localhost:8000/docs
```

Los artefactos se montan como volúmenes en lugar de copiarse a la imagen: pesan demasiado y cambian
con cada reentrenamiento.

Estado actual: los archivos de contenedores no están versionados, por lo que esta integración no se
puede reproducir desde el repositorio.

---

## 5. Pendientes técnicos identificados

1. **Versionar con DVC** el modelo (`models/modelo_ganador.joblib`, 10,2 MB) y el parquet del
   tablero (3,0 MB). Hoy están en `.gitignore` por ser derivados; el curso pide modelos y datos
   versionados.
2. **Calibración con validación cruzada** (`CalibratedClassifierCV` con `cv=5` sobre los días 0–24).
   La recalibración isotónica se descartó en la Entrega 2 porque costaba 0,0164 de AUC, pero ese
   costo venía de perder días de entrenamiento, no de la calibración en sí. Con validación cruzada
   se corrige el sesgo de probabilidad sin sacrificar datos.
3. **Adelgazar la imagen de la API**, hoy en 2,13 GB. Buena parte viene de las ruedas de XGBoost,
   SciPy y PyArrow; una construcción multietapa reduciría bastante.
4. **Reentrenamiento periódico.** La deriva observada implica que el modelo caduca. Conviene definir
   la cadencia y dejar el procedimiento documentado en el manual de instalación.
5. **Migrar el tablero de Dash a consumir la API**, para cerrar la separación entre front y modelo.

---

## 6. Limitaciones que se arrastran

1. **El techo del problema es bajo**: +0,021 de AUC sobre una tabla de frecuencias. Sin clima ni
   estado de la aeronave, es lo que el itinerario permite. El experimento sobre `Flight` de la
   Entrega 2 lo confirmó: el efecto de rotación de aeronave no es recuperable con estos datos.
2. **31 días de una sola temporada.** No hay estacionalidad anual ni festivos.
3. **Las probabilidades subestiman el riesgo** (42,8% predicho frente a 53,1% real). El
   ordenamiento es correcto, pero el número absoluto debe leerse con reserva hasta recalibrar.
4. **El recall del punto de operación es 31%.** Reforzar el 20% del itinerario implica dejar pasar
   dos tercios de los retrasos. Es consecuencia de un presupuesto acotado, y dónde ponerlo es
   decisión del negocio.

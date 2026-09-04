# Predicción del riesgo de retraso en vuelos a partir del itinerario programado

**Micro-proyecto — Proyecto de Desarrollo de Soluciones · MAIA**
**Entrega 1 — Semana 3**

> Transcripción del reporte entregado. Este documento refleja lo que el equipo envió; se conserva
> tal cual para efectos de trazabilidad. Los hallazgos posteriores que corrigen o amplían algunos
> de sus puntos están en [`docs/2nd_delivery/borrador_entrega2.md`](../2nd_delivery/borrador_entrega2.md).

## Integrantes del equipo

| Integrante | Correo |
|---|---|
| María del Pilar Munoz | md.munoz@uniandes.edu.co |
| Santiago Melo Medina | s.melom23@uniandes.edu.co |
| Katherine Rodríguez Sanches | k.rodriguezs2@uniandes.edu.co |
| Edisson David Prieto | ed.prieto@uniandes.edu.co |

---

## 1. Problema y contexto

### 1.1 Contexto general

Los retrasos aéreos constituyen uno de los problemas más estudiados en analítica de transporte y
ciencia de datos aplicada a la aviación debido a su impacto operativo y económico sobre
aerolíneas, aeropuertos y pasajeros [1][2]. La literatura destaca que las demoras afectan la
utilización de aeronaves, la programación de tripulaciones, la gestión de conexiones, la
asignación de recursos aeroportuarios y la experiencia de los pasajeros [1]. Como resultado, la
predicción temprana de retrasos se ha convertido en una línea relevante de investigación dentro de
la ciencia de datos aplicada a la aviación [1].

Asimismo, la literatura ha evaluado numerosos algoritmos de aprendizaje automático para abordar
este problema, incluyendo Regresión Logística, Árboles de Decisión, Random Forest, Gradient
Boosting, Support Vector Machines (SVM) y Redes Neuronales [2]. Tang et al. presentan una
comparación entre distintos enfoques de clasificación y muestran que los métodos basados en
árboles obtienen resultados especialmente competitivos para la predicción de retrasos aéreos [2].
Esto constituye un punto de partida importante para nuestro proyecto y una motivación para
experimentar con diferentes enfoques de modelado.

Finalmente, existe una motivación adicional desde la experiencia del usuario. Los retrasos en
vuelos son un fenómeno cotidiano y fácilmente reconocible para cualquier pasajero frecuente. Por
esta razón, el problema resulta especialmente atractivo como caso de estudio para este
microproyecto, ya que combina relevancia práctica, disponibilidad de datos históricos y la
oportunidad de aplicar técnicas de Machine Learning y MLOps sobre un problema real con impacto
operativo claramente identificable.

### 1.2 Desafíos y dimensiones del problema

A partir de la naturaleza del problema y de las características de la información disponible para
el análisis, se identifican los siguientes desafíos:

- **Anticipación:** la estimación debe realizarse utilizando únicamente información disponible
  antes del despegue, de manera que el resultado pueda apoyar decisiones operativas con suficiente
  antelación.
- **Impacto operativo:** una alerta temprana sobre el riesgo de retraso puede facilitar la
  asignación preventiva de personal, puertas de embarque, conexiones y recursos de atención al
  pasajero.
- **Incertidumbre:** dado que el retraso depende de múltiples factores operativos, el resultado
  debe interpretarse como una probabilidad o nivel de riesgo y no únicamente como una
  clasificación binaria.
- **Generalización:** el modelo debe mantener un desempeño consistente ante diferentes aerolíneas,
  rutas, horarios y días de operación.
- **Costo del error:** no detectar un vuelo con alta probabilidad de retraso puede afectar la
  planificación operativa, mientras que una falsa alarma puede generar asignaciones innecesarias
  de recursos. Por esta razón, ambos tipos de error deben evaluarse cuidadosamente durante la
  validación del modelo.

---

## 2. Pregunta de negocio y alcance del proyecto

### 2.1 Pregunta de negocio

> *"Dado el itinerario programado de un vuelo (aerolínea, ruta, día, hora y duración), ¿cuál es la
> probabilidad de que el vuelo se retrase, de manera que el equipo de operaciones pueda anticipar
> acciones de mitigación?"*

### 2.2 Objetivo del proyecto

Desarrollar y validar una solución analítica capaz de estimar la probabilidad de retraso de un
vuelo a partir de la información disponible en su itinerario programado, presentando el resultado
de forma comprensible y útil para apoyar la toma de decisiones operativas.

### 2.3 Alcance técnico y operativo

El alcance del proyecto contempla las siguientes actividades:

1. **Datos:** utilizar el conjunto histórico de vuelos y exclusivamente variables conocidas antes
   del despegue.
2. **Exploración:** analizar la calidad de los datos, sus distribuciones, posibles valores atípicos
   y asociaciones con la variable objetivo (`Delay`).
3. **Preparación:** realizar limpieza de datos, tratamiento de registros inválidos, codificación de
   variables categóricas y generación de características derivadas relacionadas con horario y ruta.
4. **Modelado:** seleccionar y comparar algoritmos de clasificación supervisada reportados en la
   literatura para la predicción de retrasos aéreos, incluyendo Regresión Logística como modelo
   base y modelos basados en árboles como Decision Tree, Random Forest y Gradient
   Boosting/XGBoost.
5. **Validación:** evaluar el desempeño de los modelos mediante métricas de clasificación como
   Accuracy, Precision, Recall y F1-Score, complementadas con AUC-ROC. Adicionalmente, se
   verificará la calibración de las probabilidades y se evitará la fuga de información entre
   particiones.
6. **Prototipo:** implementar una interfaz que permita ingresar un itinerario y obtener la
   probabilidad de retraso, junto con un nivel de riesgo y una alerta operativa.
7. **Viabilidad:** construir una prueba de concepto funcional, sin contemplar integración en tiempo
   real con sistemas aeroportuarios ni despliegue en entornos productivos.

El alcance del proyecto **no** incluye:

- Variables meteorológicas, características específicas de la aeronave o causas operativas
  detalladas del retraso. Dado que el dataset corresponde a vuelos de Estados Unidos en 2008, el
  modelo debe entenderse como un **prototipo demostrativo** y no como una herramienta calibrada
  para operaciones actuales.
- Información de fecha calendario completa. El conjunto de datos únicamente incluye el día de la
  semana, por lo que no es posible capturar efectos de estacionalidad, festivos o eventos
  extraordinarios.
- Integración con sistemas aeroportuarios o aerolíneas en tiempo real.

### 2.4 Cómo se resolverá la pregunta de negocio

La solución se abordará desde dos perspectivas complementarias: análisis descriptivo y análisis
predictivo.

**Análisis descriptivo:** se desarrollarán visualizaciones orientadas a identificar patrones
históricos de riesgo, incluyendo tasas de retraso por aerolínea, día de la semana, franja horaria y
ruta. Este análisis permitirá comprender los principales factores asociados a los retrasos y
proporcionar contexto para la toma de decisiones operativas.

**Análisis predictivo:** siguiendo enfoques reportados en la literatura para la predicción de
retrasos aéreos [2], se compararán varios algoritmos de clasificación supervisada. Se utilizará la
Regresión Logística como modelo base y posteriormente se evaluarán modelos de mayor capacidad,
incluyendo Decision Tree, Random Forest y Gradient Boosting/XGBoost. La comparación se realizará
mediante métricas como Accuracy, Precision, Recall, F1-Score y AUC-ROC, con el objetivo de
identificar el modelo que proporcione la mejor capacidad predictiva para estimar el riesgo de
retraso.

---

## 3. Descripción de conjuntos de datos a emplear

### 3.1 Fuente, tamaño y formato

El proyecto utilizará el conjunto de datos **Airlines Dataset**, disponible a través de OpenML y
distribuido mediante DataHub. El objetivo original del dataset es la predicción de retrasos en
vuelos a partir de información conocida antes del despegue [3].

- **Fuente:** OpenML / DataHub Airlines Dataset
- **Archivo:** `data/airlines.csv`
- **Formato:** CSV
- **Tamaño local:** 19.164.425 bytes (aprox. 18 MB)
- **Número de registros:** 539.383 vuelos
- **Número de variables:** 8

**Descripción de variables**

| Variable | Tipo analítico | Descripción |
|---|---|---|
| `Airline` | Categórica nominal | Código identificador de la aerolínea |
| `Flight` | Categórica nominal | Número o identificador del vuelo |
| `AirportFrom` | Categórica nominal | Aeropuerto de origen |
| `AirportTo` | Categórica nominal | Aeropuerto de destino |
| `DayOfWeek` | Categórica ordinal | Día de la semana codificado de 1 a 7 |
| `Time` | Numérica | Hora programada de salida expresada en minutos desde medianoche |
| `Length` | Numérica | Duración programada del vuelo en minutos |
| `Delay` | Binaria | Variable objetivo; 1 indica retraso y 0 indica ausencia de retraso |

**Variable objetivo**

La variable objetivo (`Delay`) presenta una distribución relativamente equilibrada. Del total de
registros, **240.264 vuelos (44,54%)** presentan retraso, mientras que **299.119 vuelos (55,46%)**
corresponden a vuelos sin retraso. Esta distribución permite abordar el problema como una tarea de
clasificación binaria sin requerir inicialmente estrategias agresivas de balanceo de clases.

**Consideraciones y limitaciones de los datos**

El dataset contiene únicamente variables disponibles antes de la salida del vuelo, razón por la
cual resulta adecuado para construir modelos predictivos orientados a la anticipación de retrasos.
Sin embargo, no incorpora información meteorológica, características específicas de la aeronave,
causas operativas de retraso ni información de tráfico aéreo en tiempo real. Asimismo, únicamente
registra el día de la semana y no la fecha calendario completa, lo que limita el análisis de
fenómenos estacionales o eventos extraordinarios.

### 3.2 Estructura de carpetas y versionamiento

Con el fin de garantizar la trazabilidad y reproducibilidad del proyecto, los datos serán
gestionados mediante **Git y DVC (Data Version Control)**.

```
project
├── data
│   ├── airlines.csv
│   └── airlines.csv.dvc
├── exploration
│   └── name-airlines.ipynb
├── scripts
├── models
└── README.md
```

Descripción de los principales elementos:

- **`data/airlines.csv.dvc`**: archivo de metadatos utilizado por DVC para rastrear la versión del
  dataset y verificar su integridad.
- **`data/airlines.csv`**: copia local del conjunto de datos utilizada durante el desarrollo y
  excluida del repositorio Git debido a su tamaño.
- **`exploration/name-airlines.ipynb`**: notebook reproducible que contiene el análisis
  exploratorio de datos, visualizaciones y hallazgos iniciales realizado por cada miembro del
  equipo. La exploración fue realizada de forma individual por cada integrante del equipo con el
  propósito de familiarizarse con el conjunto de datos, comprender sus características y generar
  una visión compartida del problema a resolver.

---

## 4. Exploración de los datos

### 4.1 Objetivo de la exploración

Comprender la calidad, estructura y comportamiento del dataset `airlines.csv` para determinar su
viabilidad como base de un modelo predictivo de retraso de vuelos, usando para esto la variable
`Delay` como variable objetivo.

Puntualmente se buscó:

1. Verificar la completitud y tipos de datos.
2. Medir el balance de la variable objetivo.
3. Identificar relaciones aparentes entre las variables predictoras y la variable objetivo.
4. Detectar problemas de calidad en la recolección de los datos, tales como duplicados y outliers
   que deban resolverse antes del modelado.

### 4.2 Alcance de los datos analizados

- **Fuente:** dataset "Airlines" de OpenML (id 1169), versionado en el repositorio con DVC
  (`data/airlines.csv.dvc`).
- **Tamaño:** 539.383 registros, 8 columnas.
- **Cobertura temporal:** el dataset no incluye fecha explícita, solo `DayOfWeek` (día de la
  semana, 1–7); no es posible ubicar los vuelos en un rango de fechas calendario.
- **Cobertura geográfica:** 293 aeropuertos distintos como origen y como destino, con fuerte
  concentración en grandes hubs de Estados Unidos (ATL, ORD, DFW, DEN, LAX).
- **Aerolíneas:** 18 aerolíneas distintas, con Southwest (WN) como la de mayor volumen (~94k
  vuelos, 17% del total).

### 4.3 Estructura y formatos

El formato es un único CSV plano, sin anidamiento ni columnas derivadas, por lo que el formato de
los datos es estructurado y tabular.

### 4.4 Plan de limpieza y estandarización

Realizando la exploración de los datos se evidencia que la correlación de las variables numéricas
en general es débil:

| | Time | Length | Delay |
|---|---|---|---|
| **Time** | 1,000000 | -0,020612 | 0,150454 |
| **Length** | -0,020612 | 1,000000 | 0,040489 |
| **Delay** | 0,150454 | 0,040489 | 1,000000 |

Por lo tanto, se trabajará con todas las variables numéricas disponibles.

A partir de los hallazgos de la exploración, se propone:

1. **Duplicados exactos (216.618 filas, ~40% del dataset):** no se eliminan automáticamente. Dado
   que no existe columna de fecha, estas filas podrían representar vuelos recurrentes (misma
   ruta/horario en semanas distintas) y no un error de carga.
2. **Valores fuera de rango en `Length`:** hay 25.650 vuelos por encima de 283,5 minutos que
   parecen plausibles y deben conservarse, y 4 vuelos con duración = 0 minutos, inválido
   físicamente. Se eliminan estos registros (impacto despreciable, <0,001% de los datos).
3. Los tipos **`Airline`, `AirportFrom`, `AirportTo` y `DayOfWeek`** deben codificarse como
   categóricos antes del modelado usando codificación *one-hot*.
4. **Variables con nulos:** no se encontraron valores nulos, por lo que no será necesario aplicar
   técnicas de imputación.
5. **Variables más relacionadas:** `Time` muestra la mayor correlación lineal con `Delay`, aunque
   es débil (r = 0,150). Las tasas evidencian asociaciones más marcadas con la franja horaria, la
   aerolínea, el día y los aeropuertos de origen y destino.
6. **Posibles transformaciones:** se pueden crear franjas horarias o una representación cíclica de
   `Time`, codificar las variables categóricas y tratar `Flight` como identificador categórico de
   alta cardinalidad, por lo que puede ser descartado o codificado si se decide utilizar.

### 4.5 Balance y particiones

- La variable objetivo (`Delay`) está razonablemente balanceada — 55,5% no retrasado / 44,5%
  retrasado — por lo que no se requieren técnicas de balanceo de clases
  (oversampling/undersampling) para el modelado.
- Las particiones de entrenamiento/validación/test aún no están definidas, y dado que no hay
  fechas, no se puede hacer un split temporal estricto. Se debe hacer un split estratificado por
  `Delay`, para preservar el balance de clases en cada partición.

### 4.6 Licencia

El dataset "airlines" (OpenML id 1169) está distribuido bajo licencia **ODC-PDDL** (Open Data
Commons Public Domain Dedication and License v1.0), según lo verificado en
[datahub.io/core/openml-datasets/data/airlines](https://datahub.io/core/openml-datasets/data/airlines).
Esta licencia permite el uso, copia, modificación y distribución de los datos sin restricciones,
incluyendo fines comerciales, sin requerir atribución obligatoria.

Por lo tanto, no hay restricciones que limiten su uso en este proyecto, por lo que no se requieren
pasos adicionales de cumplimiento.

---

## 5. Maqueta del prototipo

La maqueta presenta una propuesta preliminar del tablero descriptivo y predictivo que se
desarrollará durante el proyecto. El objetivo es integrar visualizaciones exploratorias,
indicadores clave y un módulo de predicción que permita estimar el riesgo de retraso de un vuelo a
partir de la información disponible en su itinerario programado, brindando apoyo a la toma de
decisiones operativas.

**Descripción del prototipo visual:**

1. **Filtros interactivos** (aerolínea, ruta, día de la semana y franja horaria) para explorar el
   comportamiento histórico de los vuelos.
2. **Indicadores clave (KPIs)** asociados al problema de negocio, como tasa de retraso, volumen de
   vuelos, duración promedio y desempeño del modelo.
3. **Visualizaciones descriptivas** orientadas a identificar patrones y factores relacionados con
   la ocurrencia de retrasos.
4. **Módulo de predicción** que permite ingresar las características de un vuelo y obtener una
   estimación de la probabilidad de retraso y su nivel de riesgo, conectando el tablero con el
   modelo de Machine Learning mediante una API.

> *Figura 1. Mockup del Dashboard* — la imagen está en el reporte entregado en PDF. Pendiente
> agregarla a `docs/1st_delivery/images/` para dejarla versionada junto con el resto de soportes.

---

## 6. Repositorios creados

### 6.1 Repositorio GitHub

**URL:** https://github.com/santiagoMeloMedina/microproyecto-grupo4-pds-maia

### 6.2 Bucket / almacenamiento remoto (S3)

**Bucket:** `s3://microproyecto-grupo4-pds-maia`
**Región:** `us-east-1`

Credenciales de AWS Academy Learner Lab compartidas (*872896465993*) en el equipo.

### 6.3 Configuración DVC

Comando de inicialización:

```bash
dvc init
```

Comando para versionar el dataset:

```bash
dvc add data/airlines.csv
```

Contenido de `data/airlines.csv.dvc`:

```yaml
outs:
- md5: 9912b30b4059e7bfdc58eb5b5a1ca043
  size: 19164425
  hash: md5
  path: airlines.csv
```

Comando para configurar el remote:

```bash
dvc remote add -d aws-remote s3://microproyecto-grupo4-pds-maia
```

Contenido de `.dvc/config`:

```ini
[core]
    remote = aws-remote
['remote "aws-remote"']
    url = s3://microproyecto-grupo4-pds-maia
```

Las capturas de soporte de esta sección (repositorio, bucket y `dvc push`) están en
[`repository_configuration.md`](repository_configuration.md) y en `images/`.

---

## 7. Reporte de trabajo en equipo

| Actividad | Responsable de ejecución |
|---|---|
| Contexto del problema | Pilar |
| Pregunta de negocio y alcance | Katherin, Pilar |
| Conjunto de datos | Katherin, Pilar |
| Descripción, exploración de datos | Edisson |
| Commits EDA | Santiago, Pilar, Edisson |
| Mockup — tablero descriptivo/predictivo | Katherin |
| Repositorio GitHub | Santiago |
| Configuración DVC con remoto AWS | Santiago |
| Reporte y revisión | Pilar, Katherin, Santiago, Edisson |

---

## 8. Referencias

1. Carvalho, L., Sternberg, A., Gonçalves, L. M., Cruz, A. B., Soares, J. A., Brandão, D.,
   Carvalho, D., & Ogasawara, E. (2020). *On the relevance of data science for flight delay
   research: a systematic review*. Transport Reviews, 41(4), 472–489.
   https://www.tandfonline.com/doi/abs/10.1080/01441647.2020.1861123
2. Tang, Y. (2021). *Airline Flight Delay Prediction Using Machine Learning Models*. Proceedings of
   the 2021 5th International Conference on E-Business and Internet (ICEBI 2021). ACM.
   https://dl.acm.org/doi/abs/10.1145/3497701.3497725
3. DataHub. *Airlines Dataset (OpenML #1169)* [Dataset].
   https://datahub.io/core/openml-datasets/data/airlines — Fuente original: Bifet, A., &
   Ikonomovska, E. (2009). Airlines Dataset. OpenML Dataset 1169. https://www.openml.org/d/1169

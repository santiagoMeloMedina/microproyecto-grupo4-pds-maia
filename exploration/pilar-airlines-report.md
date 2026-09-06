# Reporte de análisis exploratorio de retrasos aéreos

## 1. Problema y contexto

### Contexto general

Los retrasos aéreos afectan la utilización de aeronaves, la asignación de personal, las conexiones entre vuelos y la experiencia de los pasajeros. Anticipar el riesgo de retraso permite al equipo de operaciones priorizar vuelos, ajustar recursos y preparar acciones de mitigación antes de la salida.

### Desafíos y dimensiones del problema

- **Anticipación:** la estimación debe realizarse con información disponible antes del despegue.
- **Impacto operativo:** una alerta puede apoyar la asignación preventiva de personal, puertas, conexiones y atención a pasajeros.
- **Incertidumbre:** el resultado debe expresarse como probabilidad y no únicamente como una clasificación binaria.
- **Generalización:** el modelo deberá responder ante distintas aerolíneas, rutas, horarios y días.
- **Costo de error:** no detectar un retraso y generar una falsa alarma tienen consecuencias operativas diferentes.

## 2. Pregunta de negocio y alcance del proyecto

### Pregunta de negocio

> Dado el itinerario programado de un vuelo (aerolínea, ruta, día, hora y duración), ¿cuál es la probabilidad de que se retrase, para que el equipo de operaciones pueda anticipar acciones de mitigación?

### Objetivo del proyecto

Desarrollar y validar una solución analítica que estime la probabilidad de retraso de un vuelo a partir de su itinerario programado y presente el resultado de forma útil para el equipo de operaciones.

### Alcance técnico y operativo

1. **Datos:** utilizar el conjunto histórico de vuelos y únicamente variables conocidas antes del despegue.
2. **Exploración:** evaluar calidad, distribuciones, valores atípicos y asociaciones con `Delay`.
3. **Preparación:** tratar registros inválidos, codificar categorías y crear características de hora y ruta.
4. **Modelo:** comparar un modelo probabilístico base con alternativas de mayor capacidad.
5. **Validación:** medir discriminación y calibración, además de evitar fuga de información entre particiones.
6. **Prototipo:** permitir el ingreso de un itinerario y mostrar probabilidad, nivel de riesgo y una alerta operativa.
7. **Viabilidad:** construir una prueba de concepto; no se incluye integración en tiempo real con sistemas aeroportuarios ni despliegue productivo.

### Cómo se resolverá la pregunta

Se prepararán las variables del itinerario, se dividirán los datos antes de ajustar transformaciones y se entrenará un modelo de clasificación probabilística. La salida será una probabilidad calibrada de retraso y un nivel de riesgo definido mediante un umbral operativo.

## 3. Descripción de los conjuntos de datos a emplear

### Fuente, tamaño y formato

- **Fuente:** [OpenML / DataHub Airlines Dataset](https://datahub.io/core/openml-datasets/data/airlines)
- **Archivo:** `data/airlines.csv`
- **Formato:** CSV
- **Tamaño local:** 19,164,425 bytes (aproximadamente 18 MB)
- **Registros:** 539,383 vuelos
- **Variables:** 8

| Variable | Tipo analítico | Descripción |
|---|---|---|
| `Airline` | Categórica nominal | Código de la aerolínea |
| `Flight` | Categórica nominal | Número o código del vuelo |
| `AirportFrom` | Categórica nominal | Aeropuerto de origen |
| `AirportTo` | Categórica nominal | Aeropuerto de destino |
| `DayOfWeek` | Categórica ordinal | Día de la semana codificado del 1 al 7 |
| `Time` | Numérica | Hora programada expresada en minutos desde medianoche |
| `Length` | Numérica | Duración programada del vuelo en minutos |
| `Delay` | Binaria | Variable objetivo: 1 indica retraso y 0 ausencia de retraso |

La variable objetivo está relativamente equilibrada: 240,264 vuelos (44.54%) presentan retraso y 299,119 (55.46%) no presentan retraso.

### Estructura de carpetas y versionamiento

- `data/airlines.csv.dvc`: metadatos utilizados por DVC para recuperar y verificar el archivo de datos.
- `data/airlines.csv`: archivo local de trabajo, excluido de Git por su tamaño.
- `exploration/pilar-airlines.ipynb`: notebook reproducible del análisis exploratorio.
- `exploration/pilar-airlines-report.md`: reporte que resume el problema, alcance y resultados.

El conjunto no contiene archivos de anotaciones separados. La variable objetivo `Delay` ya está incluida en el CSV.

## 4. Exploración de los datos

### Objetivo de la exploración

Evaluar la calidad y el comportamiento de los datos, identificar variables asociadas con `Delay` y determinar qué información programada podría utilizarse posteriormente para construir un modelo de probabilidad de retraso.

### Alcance de los datos analizados

El EDA utiliza los 539,383 registros y las ocho variables del archivo original. En esta fase no se eliminan filas ni se transforman variables de forma permanente; las decisiones de limpieza quedan documentadas para la siguiente etapa.

### Estructura y formatos

Se analizaron `Time` y `Length` como variables cuantitativas; `Airline`, `AirportFrom`, `AirportTo` y `Flight` como variables categóricas nominales; `DayOfWeek` como categoría ordinal; y `Delay` como variable binaria objetivo.

### Calidad de datos

- No se encontraron valores nulos.
- Se identificaron 216,618 filas repetidas (40.16%). No se eliminan durante el EDA porque no existe una fecha completa ni un identificador único que permita confirmar que correspondan al mismo vuelo.
- Se encontraron cuatro registros con `Length = 0`, los cuales representan duraciones inválidas y deberán tratarse durante la limpieza.
- Los demás controles de rango para hora, día, aeropuertos, número de vuelo y variable objetivo no mostraron valores inválidos.

### Distribuciones y valores atípicos

- La mediana de `Time` es 795 minutos después de medianoche, equivalente a las 13:15.
- La mediana de `Length` es 115 minutos y su distribución tiene asimetría positiva por la presencia de vuelos largos.
- El método de Tukey identificó 25,650 vuelos con duración superior a 283.5 minutos. Estos valores son estadísticamente atípicos, pero corresponden a rutas plausibles y no deben eliminarse automáticamente.
- `WN` concentra el mayor volumen, con 94,097 vuelos (17.45%), seguida por `DL`, con 60,940 (11.30%).
- `ATL` es el aeropuerto más frecuente como origen y destino.

### Relación con los retrasos

- `Time` presenta una correlación positiva débil con `Delay` ($r=0.150$). La hora no explica por sí sola los retrasos, pero sí aporta una señal relevante.
- `Length` presenta una correlación lineal muy baja con `Delay` ($r=0.040$).
- La tasa de retraso aumenta a medida que avanza el día: 27.93% entre 00:00 y 06:00, 36.36% entre 06:00 y 12:00, 50.09% entre 12:00 y 18:00 y 51.44% entre 18:00 y 24:00.
- El día 3 tiene la mayor tasa de retraso (47.08%) y el día 6 la menor (40.06%). La fuente debe consultarse antes de asignar nombres concretos a estos códigos.
- Entre las aerolíneas con al menos 1,000 vuelos, `WN` presenta la mayor tasa de retraso (69.78%), seguida por `CO` (56.62%). Por cantidad absoluta de retrasos lideran `WN`, `DL`, `OO`, `AA` y `MQ`.
- Entre los aeropuertos con al menos 1,000 vuelos, `MDW` presenta la mayor tasa como origen (73.52%) y `OAK` la mayor como destino (63.71%).

Estos resultados representan asociaciones descriptivas y no relaciones causales. Además, los efectos de aerolínea, aeropuerto y ruta pueden estar relacionados entre sí.

### Respuesta a las preguntas exploratorias

1. **¿Qué aerolíneas presentan más retrasos?** `WN` lidera tanto por tasa como por cantidad. El orden de las demás aerolíneas depende de la métrica utilizada.
2. **¿Qué días tienen más retrasos?** El día 3 presenta la mayor tasa y cantidad de retrasos; el día 6 presenta la menor tasa.
3. **¿La hora afecta los retrasos?** Existe una asociación clara: la tasa aumenta desde 27.93% en la madrugada hasta 51.44% en la noche.
4. **¿La duración influye?** Su relación lineal con el retraso es muy baja, por lo que su aporte deberá comprobarse durante el modelado.

### Plan de limpieza y estandarización

La siguiente fase deberá:

1. Tratar los cuatro registros con duración igual a cero y revisar el efecto de las filas repetidas sin eliminarlas automáticamente.
2. Utilizar únicamente información disponible antes del despegue: `Airline`, `AirportFrom`, `AirportTo`, `DayOfWeek`, `Time` y `Length`.
3. Crear características derivadas, como la ruta `AirportFrom-AirportTo`, franjas horarias y representaciones cíclicas de la hora y el día.
4. Evaluar por separado `Flight`, debido a su alta cardinalidad y al riesgo de que funcione como identificador en lugar de aportar un patrón generalizable.
5. Separar entrenamiento y prueba antes de ajustar transformaciones, evitando que registros idénticos queden en ambos conjuntos.
6. Construir un modelo base probabilístico y compararlo con modelos de mayor capacidad.
7. Evaluar discriminación y calidad de las probabilidades mediante ROC-AUC, PR-AUC, log loss, Brier score y curvas de calibración.
8. Definir un umbral de alerta de acuerdo con el costo operativo de no detectar un retraso frente al costo de generar una falsa alarma.

### Balance y particiones

- `Delay` presenta una distribución de 44.54% con retraso y 55.46% sin retraso, por lo que inicialmente no se requiere remuestreo.
- Los datos aún no se han dividido durante el EDA.
- Para el modelado se propone una partición estratificada en entrenamiento, validación y prueba.
- Los registros idénticos deberán mantenerse dentro de una misma partición para evitar una estimación artificialmente optimista.
- Debido a que no existe una fecha completa, no es posible realizar una validación temporal real con este conjunto.

### Licencia

La página de DataHub identifica la procedencia del conjunto, pero la licencia no está documentada en los archivos locales del repositorio. Debe confirmarse en la fuente original antes de distribuir los datos o utilizar la solución fuera del contexto académico.

### Conclusión

Las variables con mayor potencial inicial son la aerolínea, la hora, el día de la semana y los aeropuertos de origen y destino. La duración puede conservarse para evaluar su aporte incremental. Los resultados permiten avanzar hacia la preparación y el modelado, pero todavía no demuestran causalidad ni garantizan capacidad predictiva fuera de la muestra.

El análisis reproducible y sus visualizaciones se encuentran en [`pilar-airlines.ipynb`](pilar-airlines.ipynb).

## 5. Maqueta del prototipo

La prueba de concepto se plantea como una interfaz de una sola vista:

1. Formulario con aerolínea, aeropuerto de origen, aeropuerto de destino, día, hora y duración programada.
2. Botón **Estimar riesgo** para solicitar la predicción.
3. Resultado principal con la probabilidad estimada de retraso.
4. Nivel de riesgo bajo, medio o alto según umbrales definidos con el equipo de operaciones.
5. Resumen del itinerario evaluado y factores asociados al resultado.
6. Mensaje de mitigación sugerida cuando el riesgo supere el umbral operativo.

## 6. Mockup

```text
+--------------------------------------------------------------+
| Estimación de riesgo de retraso                              |
+--------------------------------------------------------------+
| Aerolínea        [ WN v ]   Día              [ 3 v ]         |
| Origen           [ MDW v]   Destino          [ OAK v ]       |
| Hora programada  [ 18:30]   Duración (min)   [ 240   ]       |
|                                                              |
|                                      [ Estimar riesgo ]       |
+--------------------------------------------------------------+
| Probabilidad de retraso                                      |
|                                                              |
|                         68%                                  |
|                     RIESGO ALTO                              |
|                                                              |
| Ruta: MDW - OAK | Franja: noche | Aerolínea: WN             |
| Acción: revisar recursos y conexiones antes de la salida.    |
+--------------------------------------------------------------+
```

El porcentaje del mockup es únicamente ilustrativo; no corresponde a una predicción real porque el modelo todavía no ha sido entrenado.
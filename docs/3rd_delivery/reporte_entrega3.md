# Riesgo de retraso por franja de itinerario — Entrega Final

**Grupo 4 · Proyecto de Desarrollo de Soluciones · MAIA, Universidad de los Andes**

Repositorio: `https://github.com/santiagoMeloMedina/microproyecto-grupo4-pds-maia`

---

## 1. Resumen del problema

**Contexto.** Un retraso no afecta solo al vuelo que lo sufre: compromete la aeronave y la
tripulación para los siguientes trayectos, de modo que una demora temprana se propaga en cascada por
la red. Esa propagación se observa en los datos —la tasa de retraso crece de forma sostenida a lo
largo del día— y convierte el problema en una cuestión de **diseño de itinerario**, no solo de
reacción operativa. Así, para los equipos de planeación no basta con conocer la tasa global de
retraso: necesitan identificar anticipadamente qué combinaciones recurrentes de aerolínea, ruta, día
y horario presentan mayor exposición, con el fin de priorizar recursos operativos limitados.

**Pregunta de negocio.**

> **¿Qué combinaciones de aerolínea, ruta, día y franja horaria concentran el mayor riesgo de
> retraso, de modo que el equipo de planeación pueda reforzar recursos y ajustar márgenes de
> conexión en los itinerarios más expuestos?**

**Usuario y decisión.** La solución está dirigida principalmente al equipo de planeación de red. Su
propósito es apoyar decisiones previas a la operación, como asignar personal de apoyo, revisar
márgenes de conexión y priorizar itinerarios que requieren mayor seguimiento. El sistema no
reemplaza la decisión del usuario: organiza las franjas según su riesgo estimado y aporta contexto
histórico para interpretarlas.

**Solución desarrollada.** Se implementó un prototipo funcional compuesto por un modelo supervisado
XGBoost empaquetado, una API de inferencia desarrollada con FastAPI y un tablero web en React. El
usuario puede consultar las franjas de itinerario con mayor riesgo, aplicar filtros operativos y
estimar el riesgo de una combinación específica. El tablero consume las predicciones y los
parámetros del modelo mediante la API; además, integra visualizaciones descriptivas para
contextualizar los patrones históricos de retraso. La solución puede desplegarse mediante
contenedores Docker coordinados con Docker Compose.

**Conjunto de datos.** Se utilizó el conjunto público *Airlines* de OpenML (OpenML id 1169, licencia
ODC-PDDL), versionado con DVC, que contiene 539.383 registros de vuelos domésticos de 18 aerolíneas
entre 293 aeropuertos, y 8 variables. Después de retirar cuatro registros con duración inválida (0
minutos), el conjunto de análisis quedó conformado por 539.379 vuelos. La variable objetivo `Delay`
indica si ocurrió un retraso. El periodo se dividió temporalmente en entrenamiento, validación y
prueba para evaluar el desempeño sobre observaciones posteriores a las utilizadas durante el ajuste.

Con respecto a la entrega anterior, no se incorporaron nuevas fuentes de datos para entrenamiento.
Los principales cambios estuvieron orientados a la preparación de artefactos destinados al
despliegue de la solución. Adicionalmente, se identificó la necesidad de versionar mediante DVC tanto
el modelo ganador como el conjunto de datos derivado utilizado por el tablero, con el fin de cumplir
los requisitos de trazabilidad y reproducibilidad del proyecto.

**Registros repetidos.** Se identificaron 216.618 filas exactamente repetidas que se conservaron. De
las 185.451 combinaciones de itinerario que aparecen más de una vez, 95.373, equivalentes al 51,4%,
presentan resultados diferentes en `Delay`. Esto indica que una misma programación puede
corresponder a distintas ocurrencias de vuelos con resultados diferentes, por lo que los registros
repetidos no pueden tratarse automáticamente como errores de captura. Eliminarlos alteraría la
frecuencia observada de operación y la distribución de la variable objetivo.

**Estructura temporal.** Aunque el conjunto no contiene una fecha explícita, el orden de las filas y
los cambios consecutivos en `DayOfWeek` permitieron reconstruir 31 días. La tasa de retraso aumenta
de 41,0% en el bloque inicial a 53,1% en el bloque final. Para respetar ese desplazamiento temporal,
los datos se dividieron en entrenamiento, validación y prueba mediante bloques consecutivos, sin
realizar una partición aleatoria.

**Alcance y limitaciones.** El modelo utiliza únicamente información disponible durante la
programación: aerolínea, aeropuerto de origen, aeropuerto de destino, día de la semana, hora de
salida y duración prevista. Por ello, estima el riesgo de una franja recurrente de itinerario, no el
estado en tiempo real de un vuelo específico ni la duración del posible retraso. Quedan fuera
variables como clima, tráfico aéreo, estado de la aeronave, tripulación y condiciones operativas del
día. En consecuencia, el resultado debe utilizarse para ordenar y priorizar itinerarios, no como
garantía de que un vuelo específico se retrasará.

### Cambios respecto a la Entrega 2

En la Entrega 2 se desarrollaron y compararon los modelos y se presentó un tablero monolítico. Para
la entrega final, el modelo XGBoost seleccionado se convirtió en un paquete instalable y versionado;
sus inferencias se publicaron mediante una API; el tablero se migró a React y se conectó a
predicciones reales; y se incorporaron artefactos de Docker para desplegar la API y la interfaz como
servicios independientes. También se añadieron pruebas automatizadas, documentación de endpoints y
manuales de instalación y uso.

| Tema | Entrega 2 | Entrega Final |
|---|---|---|
| **Modelo** | Artefacto `.joblib` suelto, no versionado | **Paquete instalable** `model_riesgo_retraso` (wheel) con el pipeline entrenado dentro |
| **Servicio** | El tablero cargaba el modelo en su propio proceso | **API FastAPI** con cinco endpoints documentados |
| **Tablero** | Prototipo en Dash, monolítico | **Tablero React** que consume la API |
| **Despliegue** | Ejecución local | **Docker Compose** local y **Terraform/ECS sobre EC2** en AWS |
| **Familias evaluadas** | Tres (logística, Random Forest, XGBoost) | Se probó además **LightGBM** como comparación experimental; no se incorporó al producto final |
| **Reproducibilidad** | Notebook | `tox run -e train` reentrena y `tox run -e test_package` valida |

---

## 2. Modelos desarrollados y su evaluación

### 2.1 Decisiones de preparación

**Partición.** Sobre los 539.379 vuelos se aplicó una partición temporal en tres bloques disjuntos:
entrenamiento con los días 0–19 (347.091 vuelos, 41,0% de retraso), validación con los días 20–24
(84.824 vuelos, 48,1%) y prueba con los días 25–30 (107.464 vuelos, 53,1%). La validación se empleó
para seleccionar hiperparámetros y familia, y el bloque de prueba se mantuvo intacto hasta la
evaluación final. El modelo ganador se reajustó después sobre los días 0–24 antes de exportarse.

**Ingeniería de características.** El diseño estuvo sujeto a una restricción operativa: toda variable
debía poder calcularse con los seis campos que el tablero solicita al usuario, ya que cualquier
variable dependiente del día calendario concreto sería imposible de construir al momento de predecir.
Bajo esa regla se construyeron `Hora`, `TimeSin` y `TimeCos`, que tratan la hora como magnitud
cíclica; `Franja`, que discretiza la propagación de retrasos a lo largo del día; `Ruta`, el par
origen–destino, que discrimina entre 19,0% y 68,0% de retraso en las rutas frecuentes; y
`DensidadOrigen` y `DensidadDestino`, un proxy de congestión aprendido como tabla de consulta
únicamente sobre el bloque de entrenamiento.

**Variable `Flight`.** En respuesta a la retroalimentación de la Entrega 1, `Flight` se sometió a un
experimento controlado en lugar de descartarse por inspección. La sugerencia era que una codificación
por objetivo podría recuperar el efecto de rotación de aeronave. El resultado fue negativo y
consistente: la correlación del riesgo por número de vuelo entre entrenamiento y validación es de
apenas 0,393, y el riesgo medio codificado pasa de 0,410 a 0,481, de modo que la variable arrastra la
tasa base del período de ajuste hacia uno donde la tasa real es mayor. Incorporarla deteriora el AUC
en las tres familias: −0,0035 en regresión logística, −0,0061 en Random Forest y −0,0060 en XGBoost.
El daño disminuye de forma monótona al aumentar el suavizado, que es la firma de un predictor que
aporta ruido y sesgo en lugar de señal. `Flight` quedó excluida.

### 2.2 Alternativas de modelado y búsqueda

Se seleccionaron tres familias que cubren un espectro deliberadamente amplio: una base lineal
interpretable, un representante de *bagging* y uno de *boosting*. Esa diversidad es la que permite
distinguir si la complejidad adicional se traduce en desempeño o si el límite proviene de los datos.

La búsqueda de hiperparámetros se realizó por muestreo aleatorio y no por malla exhaustiva: con seis
o siete hiperparámetros una malla obligaría a miles de combinaciones, mientras que 30 muestras cubren
mejor el espacio con el mismo presupuesto. Se ejecutaron **30 corridas por familia, 90 en total**,
con semilla fija y registro íntegro en MLflow.

**Métricas.** El criterio de selección es **ROC-AUC**, porque mide ordenamiento y es invariante a la
tasa base: con la tasa desplazándose de 41,0% a 53,1% entre bloques, cualquier métrica atada a un
umbral cambiaría por razones ajenas al modelo. Se acompaña de PR-AUC, Brier y log-loss —el tablero
muestra una probabilidad y ese número debe significar lo que dice—, precisión, recall y F1 al umbral
fijado en validación, y el tamaño del artefacto, que no es un detalle menor cuando la deriva obliga a
reentrenar con frecuencia.

**Líneas base.** Tres referencias con el mismo tratamiento que los modelos: clase mayoritaria
(ROC-AUC 0,5000), memoria de itinerario (0,6043) y tasa por aerolínea × franja (**0,6763**). La
tercera es la referencia exigente, pues equivale a la regla que un analista escribiría a mano en una
tarde.

### 2.3 Resultados

![Dispersión del AUC y costo de ajuste](../2nd_delivery/images/modelo_02_dispersion_auc.png)

*Figura 1. Izquierda: dispersión del ROC-AUC de validación en los 30 experimentos de cada familia.
Derecha: costo de ajuste frente a desempeño, con el tiempo en escala logarítmica.*

Las cajas resumen el comportamiento de cada familia. La regresión logística presenta una dispersión
mínima —sus 30 corridas se mueven en un rango de 0,014 de AUC— señal de que ya alcanzó su límite.
Random Forest exhibe la caja más amplia, con corridas que descienden hasta 0,6633: es la familia más
sensible a la configuración. XGBoost combina la mediana más alta, 0,6996, con una dispersión
estrecha. El panel derecho resuelve el empate entre los dos modelos de árboles: ambos alcanzan techos
equivalentes, pero XGBoost obtiene el mismo AUC en segundos donde Random Forest necesita minutos.

**Sobre el bloque de prueba** (días 25–30, 107.464 vuelos), evaluado una sola vez:

| Familia | ROC-AUC | PR-AUC | Brier | Tamaño | Ajuste |
|---|---|---|---|---|---|
| Random Forest | **0,6987** | 0,7312 | **0,2195** | 75,9 MB | 125 s |
| XGBoost | 0,6974 | 0,7309 | 0,2292 | **10,3 MB** | **5,6 s** |
| Regresión logística | 0,6857 | 0,7158 | 0,2236 | 0,15 MB | 7,7 s |
| LightGBM | 0,6972 | — | — | — | 11 s |
| *Mejor línea base* | *0,6763* | — | *0,2352* | — | — |

La evaluación experimental de LightGBM fue desarrollada por Edisson David
Prieto. En el registro consolidado disponible para esta comparación se
reportaron ROC-AUC y tiempo de ajuste; los guiones indican métricas no
reportadas, no valores iguales a cero. LightGBM se usó solo como contraste: no
fue seleccionado, empaquetado ni incorporado a la API o al despliegue final.

Una reproducción del entrenamiento del paquete en macOS obtuvo ROC-AUC 0,6972
para XGBoost, una diferencia de 0,0002 frente al artefacto desplegado. Esta
variación de último decimal no modifica la selección del modelo ni la compuerta
de desempeño; la reproducibilidad esperada es funcional y métrica dentro de esa
tolerancia, no identidad binaria entre plataformas.

**Selección.** Random Forest y XGBoost quedaron separados por 0,0013 de AUC, diferencia dentro del
ruido para un bloque de 107 mil filas, mientras que el artefacto de Random Forest pesa 7,4 veces más
y tarda 22 veces más en ajustarse. Se aplicó una regla declarada de antemano: gana el de mayor AUC,
salvo que otro quede dentro de 0,005 y pese menos de la mitad. **El modelo elegido fue XGBoost**, por
costo de despliegue y no por desempeño, en un sistema que la deriva obliga a reentrenar.

Se evaluó además una recalibración isotónica y se descartó: corrige el sesgo pero cuesta 0,0163 de
AUC, y ese costo no viene de la calibración sino de que el esquema obliga a entrenar con 20 días en
vez de 25.

**Punto de operación.** El umbral se fijó con criterio de negocio y no maximizando F1, que marcaría
el 83% del itinerario con un *lift* de apenas 1,09. Bajo un **presupuesto de refuerzo del 20%**, el
umbral 0,553 señala el 20,9% de las franjas con **79,9% de precisión** y *lift* 1,50: 80 aciertos por
cada 100 franjas reforzadas, frente a 53 repartiendo los recursos al azar.

### 2.4 Soporte en MLflow

Las 90 corridas se registraron contra un servidor de seguimiento desplegado sobre una **instancia EC2
de AWS**, con respaldo en SQLite y artefactos servidos por el propio servidor. Cada corrida almacena
la familia, los hiperparámetros muestreados, las métricas de validación, el tiempo de ajuste y el
tamaño del artefacto, lo que permite comparar desempeño contra costo directamente en la interfaz. El
ganador quedó publicado en el Model Registry como `riesgo-retraso-vuelos`, versión 1. Las evidencias
están en el anexo.

### 2.5 Empaquetamiento del modelo

El modelo se distribuye como un paquete instalable, `model_riesgo_retraso`, construido en
`model-pkg/` siguiendo la metodología del taller 5. Toda la configuración vive en `config.yml` y se
valida con pydantic al arrancar; `tox run -e train` reentrena de forma reproducible y
`python -m build` genera un wheel de 4,4 MB **con el pipeline entrenado dentro**.

Esto resuelve tres problemas de una vez. El artefacto deja de ser un archivo suelto no versionado
—antes, un clon limpio o una construcción de imagen fallaban—; la API deja de necesitar que el
paquete de experimentación esté en el `PYTHONPATH`; y las versiones de scikit-learn y xgboost quedan
fijadas junto al modelo, que es lo que evita que se sirva con una versión distinta de la que entrenó.

El entrenamiento del paquete en CPU reproduce las cifras publicadas, obtenidas con GPU T4 en Colab:
ROC-AUC 0,6974 y Brier 0,2292 idénticos, con diferencias en la cuarta cifra atribuibles a la
construcción de histogramas de XGBoost. Siete pruebas unitarias cubren el contrato de entrada, la
coherencia de las bandas y el manejo de categorías no vistas; una de ellas es una **compuerta de
desempeño** que falla si el AUC cae por debajo de la línea base, de modo que una regresión rompe la
construcción en lugar de pasar inadvertida.

---

## 3. Tablero y API desarrollados

### 3.1 Arquitectura

```
model-pkg/  ──build──▶  wheel  ──pip install──▶  api/  ──HTTP/JSON──▶  ui/
(entrenamiento)      (modelo)       (FastAPI)                      (React + nginx)
                                         │
                            dashboard/data/vuelos.parquet
                                  (histórico)
```

Cada pieza tiene una responsabilidad y un contrato explícito. El paquete produce el modelo; la API lo
sirve y añade el contexto histórico; el tablero consume la API y no conoce el modelo. Los dos últimos
corren como contenedores independientes.

### 3.2 La API

FastAPI sobre uvicorn, con la estructura del taller 6: configuración en `config.py`, esquemas
Pydantic separados por recurso y enrutador en `api.py`. Expone cinco endpoints bajo `/api/v1`:

| Endpoint | Qué entrega |
|---|---|
| `GET /health` | Estado, versión de la API, **versión del modelo**, familia y umbrales vigentes |
| `GET /catalog` | Aerolíneas, aeropuertos, rutas frecuentes y días, derivados del histórico |
| `POST /predict` | Probabilidad, banda y comparación con las tasas históricas de referencia |
| `GET /schedule-slots` | Franjas ordenadas por riesgo estimado, con cuatro filtros combinables |
| `GET /schedule-slots/summary` | Indicadores de la selección activa |

La documentación interactiva se genera sola en `/docs`. Nueve pruebas cubren los endpoints, la
validación de entradas y la configuración de CORS, y corren con `tox run -e test_app` contra el mismo
wheel que se despliega.

### 3.3 El tablero

Aplicación React con Vite, servida por nginx. Tres secciones:

**Visualización de datos.** Tres tableros descriptivos —panorama general, patrones tácticos y
priorización por exposición e impacto— que resumen lo ocurrido en el período. Son vistas
descriptivas: no estiman riesgo futuro.

**Franjas a reforzar.** Es la respuesta directa a la pregunta de negocio. Lista las franjas de
itinerario ordenadas por el riesgo que estima el modelo, con cuatro filtros combinables (aerolínea,
ruta, día y franja) e indicadores que responden siempre a la selección activa. El orden lo da el
modelo y no la tasa observada porque muchas franjas tienen menos de una docena de vuelos en el
período: una franja con cuatro vuelos y cuatro retrasos muestra 100% observado, pero eso es ruido. La
columna de volumen permite juzgar cuánto respaldo tiene cada fila.

**Evaluación de un itinerario.** Formulario con los seis campos y respuesta en tres partes:
probabilidad y banda, ubicación frente al punto de operación con la acción asociada, y comparación
contra las tasas históricas de la aerolínea, la ruta, la franja y la media global. Esa comparación es
lo que permite juzgar la cifra: un 55% significa cosas distintas en una aerolínea cuyo histórico es
70% y en una cuyo histórico es 30%.

Los cortes de banda no están escritos en la interfaz: se leen de la respuesta de la API, de modo que
un cambio de umbral se refleje sin tocar el tablero.

### 3.4 Despliegue

`docker compose up --build` levanta ambos servicios. La imagen de la API instala el modelo desde el
wheel, corre como usuario sin privilegios y declara un *healthcheck* con margen de arranque, porque
al primer arranque puntúa las 92.250 franjas del itinerario. La del tablero se construye en dos
etapas y se sirve con nginx configurado para enrutamiento del lado del cliente.

El puerto del tablero es configurable con `UI_PORT`, del que se derivan también los orígenes
permitidos por CORS. Mantenerlos sincronizados no es un detalle: durante la construcción se detectó
que pydantic normaliza las URL agregando una barra final, mientras el navegador envía el encabezado
`Origin` sin ella. Como la comparación es por igualdad exacta, el tablero quedaba sin datos aunque la
API respondiera correctamente por `curl`. Hay dos pruebas de regresión que cubren ese caso.

El PR #13 añadió el despliegue reproducible en AWS. Terraform crea repositorios
ECR para API y tablero, un clúster ECS respaldado por una instancia EC2, dos
servicios independientes, una IP elástica, reglas de red y grupos de logs en
CloudWatch. El estado se conserva en un bucket S3 versionado y
`infra/scripts/build_and_push.sh` automatiza la creación de infraestructura, la
construcción y publicación de imágenes y el redespliegue de ambos servicios.

La solución utiliza `LabRole` y `LabInstanceProfile` para ser compatible con AWS
Academy. Es un despliegue académico de una sola instancia: no ofrece balanceo,
TLS, autenticación, alta disponibilidad ni continuidad garantizada durante un
redespliegue. Los puertos 80 y 8002 son públicos por defecto y deben
restringirse fuera del laboratorio.

---

## 4. Principales resultados y conclusiones

**1. Los cuatro modelos superan las líneas base, por márgenes modestos.** La ganancia es de +0,0212
de AUC sobre una tabla de frecuencias por aerolínea y franja. Es real y consistente, pero el techo lo
impone la información disponible y no el algoritmo.

**2. Cuatro familias evaluadas convergen al mismo techo.** Random Forest 0,6987, XGBoost 0,6974,
LightGBM 0,6972 y regresión logística 0,6857, todas sobre el mismo bloque de prueba. LightGBM se
evaluó como experimento comparativo y no forma parte de la solución desplegada. Que esta cuarta
familia, implementada por separado, caiga dentro de 0,0015 de las anteriores es evidencia de que el
límite está en los datos. El dataset perdió la marca temporal que vinculaba cada vuelo con el
anterior de la misma aeronave, y con ella la variable más predictiva del problema.

**3. Cuando el desempeño empata, la decisión es de ingeniería.** XGBoost y Random Forest se separan
por 0,0013 de AUC frente a un artefacto 7,4 veces más pesado y un ajuste 22 veces más lento.

**4. La deriva temporal domina el problema.** Obliga a partición temporal, hace que la clase
mayoritaria del entrenamiento no sea la de prueba, descalibra las probabilidades —el modelo predice
42,8% de riesgo medio cuando la tasa real fue 53,1%— y convierte el reentrenamiento periódico en
parte del diseño y no en una mejora opcional.

**5. La métrica de comparación y el punto de operación son decisiones separadas.** El AUC elige el
modelo porque es invariante a la tasa base; el umbral se fija después, con criterio de negocio.
Confundirlas conduce a un sistema que marca el 83% del itinerario y no prioriza nada.

**6. El valor entregado es de priorización, no de pronóstico.** Con el presupuesto de refuerzo del
20%, de cada 100 franjas señaladas 80 registran retraso frente a 53 al azar. Ese *lift* de 1,50 es el
resultado que justifica la herramienta, y no el AUC.

**7. Empaquetar cambió la naturaleza del entregable.** Pasar de un `.joblib` en una carpeta a un
wheel instalable con pruebas y versión hizo que el modelo fuera desplegable desde un clon limpio. Los
tres defectos que se corrigieron en esta entrega —artefactos no versionados, predicciones simuladas
en el tablero y CORS rechazando su propio origen— solo se vuelven visibles cuando el sistema se
integra de extremo a extremo.

### Limitaciones y trabajo futuro

El modelo no incorpora clima, estado de la aeronave ni tráfico en tiempo real, y su horizonte es la
franja semanal y no el vuelo individual. La calibración quedó pendiente: la recalibración isotónica
cuesta demasiado AUC bajo el esquema actual, y la salida es validación cruzada sobre los días 0–24,
que no sacrifica datos. Como línea de exploración queda evaluar los Modelos Fundacionales Tabulares,
que trasladan la filosofía de los LLM al dato tabular.

---

# Anexo · Evidencias

## A.1 Experimentos en MLflow sobre AWS EC2

![Instancia EC2](../2nd_delivery/images/mlflow_01_instancia_ec2.png)

*Figura A1. Consola de AWS EC2 con la instancia en ejecución y el usuario visible.*

![Servidor MLflow](../2nd_delivery/images/mlflow_02_servidor_ssh.png)

*Figura A2. Servidor de seguimiento en funcionamiento sobre la instancia.*

![Experimento en MLflow](../2nd_delivery/images/mlflow_03_experimento.jpeg)

*Figura A3. Las 90 corridas registradas, con la IP del servidor visible.*

![Comparación de corridas](../2nd_delivery/images/mlflow_04_comparacion.jpeg)

*Figura A4. Comparación de corridas por familia y métrica.*

![Modelo registrado](../2nd_delivery/images/mlflow_06_modelo_registrado.jpeg)

*Figura A5. El ganador publicado en el Model Registry como `riesgo-retraso-vuelos`, versión 1.*

## A.2 Tablero y API desplegados

![Franjas a reforzar](images/e3_01_franjas.png)

*Figura A6. Ranking de franjas de itinerario ordenado por riesgo estimado, con los filtros y los
indicadores de la selección activa.*

![Evaluación de un itinerario](images/e3_02_prediccion.png)

*Figura A7. Módulo de evaluación: probabilidad, banda, punto de operación y comparación contra el
histórico.*

![Repositorios de imágenes en ECR](images/e3_install_ecr_repositories.jpeg)

*Figura A8. Repositorios ECR creados para las imágenes de la API y del tablero.*

![Instancia EC2](images/e3_install_ec2_instance.jpeg)

*Figura A9. Instancia EC2 que aporta capacidad al clúster ECS.*

![Servicios ECS](images/e3_install_ecs_services.jpeg)

*Figura A10. Servicios independientes de API y tablero administrados por ECS.*

![Tablero desplegado](images/e3_install_dashboard_franjas.jpeg)

*Figura A11. Vista de franjas a reforzar servida desde el despliegue en AWS.*

![Predicción desplegada](images/e3_install_dashboard_prediction.jpeg)

*Figura A12. Predicción individual consumiendo la API desplegada.*

[Ver demostración en video del despliegue](media/e3_deployment_demo.mp4)

*Evidencia audiovisual de la navegación por el sistema desplegado.*

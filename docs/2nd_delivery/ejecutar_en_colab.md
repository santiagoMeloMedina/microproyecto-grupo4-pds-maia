# Ejecutar el notebook de modelado en Google Colab

El notebook detecta solo dónde se está ejecutando. En Colab clona el repositorio, instala las
dependencias y reconstruye el dataset; en local no hace nada de eso. El resto del código es idéntico
en ambos entornos.

## Qué aporta la GPU, y qué no

Conviene tenerlo claro antes de decidir:

| Modelo | ¿Usa GPU? |
|---|---|
| Regresión logística | No. CPU únicamente. |
| Random Forest (scikit-learn) | No. CPU únicamente. |
| XGBoost | **Sí**, con `device="cuda"`. |

**La GPU acelera el entrenamiento de XGBoost; no mejora su desempeño.** Sobre estos datos el AUC
sale idéntico en CPU y en GPU —se verificó— porque el algoritmo es el mismo y solo cambia dónde se
calculan los histogramas.

Dos tercios de la búsqueda (regresión logística y Random Forest) corren en CPU, así que el número de
núcleos disponibles importa tanto como la tarjeta. La detección es automática: `airlines_ml.modeling`
consulta `nvidia-smi` y usa `cuda` solo si hay una GPU visible.

## Pasos

### 1. Llevar el código a Colab

Hay dos caminos, y la celda de arranque detecta cuál aplica:

**Si la rama ya está publicada en GitHub** — desde Colab: **Archivo → Abrir cuaderno → GitHub**,
pegar la URL del repositorio y elegir `modeling/katherin-modelos-entrega2.ipynb` en la rama
correspondiente. El notebook clona el repositorio solo.

**Si la rama todavía no se ha publicado** — subir el código a mano, sin necesidad de commitear:

1. Generar el paquete con los archivos que el notebook necesita (unos 14 KB, solo código):
   ```bash
   python scripts/empaquetar_colab.py
   ```
2. En Colab: **Archivo → Subir cuaderno** y elegir `modeling/katherin-modelos-entrega2.ipynb`.
3. En el panel de archivos de Colab (icono de carpeta a la izquierda), subir `proyecto.zip` a
   `/content/`.

La celda de arranque busca `/content/proyecto.zip`; si lo encuentra lo descomprime, y si no, clona
desde GitHub.

### 2. Activar la GPU

**Entorno de ejecución → Cambiar tipo de entorno de ejecución → Acelerador por hardware: GPU (T4)**.

La T4 es suficiente: el cuello de botella aquí es el tamaño del dataset, no la capacidad de cómputo.

### 3. Configurar la dirección de MLflow

La primera celda tiene un campo de formulario:

```python
MLFLOW_TRACKING_URI = ""  #@param {type:"string"}
```

Escribir ahí `http://<ip-publica-ec2>:5000`. Si se deja vacío, MLflow escribe en SQLite dentro de la
máquina de Colab y los experimentos se pierden al cerrar la sesión.

> **Importante para este caso:** la IP desde la que sale Colab es dinámica y no se puede anticipar,
> así que el *security group* de la instancia debe permitir el puerto 5000 desde `0.0.0.0/0`. MLflow
> no tiene autenticación, de modo que mientras esa regla esté activa cualquiera que conozca la IP
> puede leer y borrar experimentos. **Detener la instancia apenas se terminen de tomar las
> evidencias.**

### 4. Ejecutar

**Entorno de ejecución → Ejecutar todo.** La primera celda debe imprimir:

```
Entorno: Google Colab
Raiz del proyecto: /content/microproyecto-grupo4-pds-maia
MLflow tracking URI: http://<ip>:5000
Servidor remoto   : True
Dispositivo XGBoost: cuda
```

Si `Dispositivo XGBoost` dice `cpu`, el acelerador no quedó activado: revisar el paso 2.

### 5. Recuperar los artefactos

Al terminar la sesión, Colab borra su disco. El notebook genera tres archivos que el tablero
necesita, y hay que bajarlos antes de cerrar:

```python
from google.colab import files
files.download(f"{RAIZ}/models/modelo_ganador.joblib")
files.download(f"{RAIZ}/models/metadata.json")
files.download(f"{RAIZ}/dashboard/data/vuelos.parquet")
```

Se copian en el repositorio local a `models/` y `dashboard/data/` respectivamente. Las figuras del
reporte se generan igual en `docs/2nd_delivery/images/` y también hay que bajarlas:

```python
!zip -qr /content/figuras.zip {RAIZ}/docs/2nd_delivery/images
files.download("/content/figuras.zip")
```

Alternativa más cómoda si se va a repetir: montar Google Drive al inicio y escribir ahí.

## Cuándo conviene cada entorno

| | Local | Colab con T4 |
|---|---|---|
| Regresión logística y Random Forest | Depende de los núcleos de CPU | 2 vCPU, suele ser más lento |
| XGBoost | Minutos | Segundos |
| Artefactos | Quedan en el repositorio | Hay que descargarlos antes de cerrar |
| Acceso a MLflow en EC2 | Puerto abierto solo a tu IP | Requiere abrirlo a `0.0.0.0/0` |

Con un equipo local de 8 o más núcleos, la diferencia total es pequeña porque dos de los tres
modelos no aprovechan la GPU. Colab gana claramente si el equipo local tiene pocos núcleos o está
ocupado con otra cosa.

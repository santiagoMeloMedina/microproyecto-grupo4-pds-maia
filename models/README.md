# Models

Esta carpeta contiene el entrenamiento de modelos predictivos sobre el dataset de airlines.

## LGBMClassifier

[train_lgbm.py](train_lgbm.py) entrena un `LGBMClassifier` (LightGBM) para predecir la columna `Delay` y registra parámetros, métricas y el modelo en MLflow.

### Dependencias

```bash
pip install -r models/requirements.txt
```

### Correr el entrenamiento

Desde la raíz del proyecto:

```bash
python models/train_lgbm.py
```

Por defecto lee `data/airlines.csv`. Se puede ajustar con argumentos, por ejemplo:

```bash
python models/train_lgbm.py --n-estimators 200 --learning-rate 0.05
```

### Correr varios escenarios de una vez

Para probar varias combinaciones de hiperparámetros sin invocar el script una por una, defínelas en un archivo YAML (ver [scenarios.lgbm.training.yaml](scenarios.lgbm.training.yaml), versionado como plantilla del equipo) y pásalo con `--scenarios-file`:

```bash
python models/train_lgbm.py --scenarios-file models/scenarios.lgbm.training.yaml
```

Cada escenario del archivo se corre una sola vez y queda como una corrida (run) separada en MLflow, nombrada con el campo `name` del escenario. Cualquier campo que no se indique en un escenario toma el valor por defecto (o el pasado por línea de comandos).

Si necesitas escenarios propios que no quieres compartir, cópialo a otro nombre (ej. `models/scenarios.local.yaml`) — no está versionado (ver `.gitignore`).

### Ver las corridas en MLflow

MLflow guarda las corridas localmente en `mlruns/` (en el directorio desde donde se ejecuta el script). Para explorarlas:

```bash
mlflow ui
```

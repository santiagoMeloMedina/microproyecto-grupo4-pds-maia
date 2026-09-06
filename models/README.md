# Models

Esta carpeta contiene el entrenamiento de modelos predictivos sobre el dataset de airlines.

## LGBMClassifier

[train_lgbm.py](train_lgbm.py) entrena un `LGBMClassifier` (LightGBM) para predecir la columna `Delay` y registra parámetros, métricas y el modelo en MLflow.

### Features y datos

La preparación de datos se encuentra en [features.py](features.py). La limpieza (espacios iniciales, filas con `Length<=0`, reconstrucción del día calendario) y la partición train/test (prueba = día ≥ 25) reutilizan [`airlines_ml.data`](../airlines_ml/data.py), el mismo módulo que usa el notebook `katherin-modelos-entrega2`. Así ambos flujos evalúan sobre exactamente el mismo período; solo cambian las features que arma cada uno encima de esos datos.

**`AirlineDowPrevDelay`:** es un **proxy aproximado**, no la señal real de "delay propagado por la misma aeronave".

**`AirlineTimeBucket`:** interacción explícita `Airline` + hora del día (buckets de 2h).

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

#### Hiperparámetros por defecto

- `n_estimators=300`, `learning_rate=0.05`, `num_leaves=63`, `max_depth=8`, `min_child_samples=50`, `reg_alpha=0.5`, `reg_lambda=0.5`: esta combinación regularizada mejora accuracy, f1 y roc_auc de forma consistente frente a los hiperparámetros simples originales (`n_estimators=100`, `learning_rate=0.1`, `num_leaves=31`, sin regularización). El escenario `sin_regularizacion` en [scenarios.lgbm.training.yaml](scenarios.lgbm.training.yaml) reproduce esos valores originales para comparar.
- `is_unbalance=true`: en todos los escenarios probados mejoró recall, f1 y roc_auc de forma consistente frente a no balancear (a costa de algo de precision). El escenario `sin_balanceo` lo desactiva explícitamente (`is_unbalance: false`, o `--no-is-unbalance` desde CLI) para confirmar que efectivamente empeora sin él.

Con `python models/train_lgbm.py` sin argumentos ya se obtiene el resultado equivalente al escenario `baseline` del YAML.

### Ver las corridas en MLflow

El experimento por defecto es `airlines-retrasos`, el mismo que usa el notebook de Katherin. El tracking se resuelve con [`airlines_ml.tracking`](../airlines_ml/tracking.py) (ver [docs/2nd_delivery/mlflow_ec2.md](../docs/2nd_delivery/mlflow_ec2.md)): si hay un `.env` en la raíz con `MLFLOW_TRACKING_URI` apuntando al servidor EC2 del equipo, las corridas quedan ahí junto con las de los demás modelos; sin `.env`, caen en el mismo SQLite local (`mlflow.db` en la raíz) que usa el notebook, así que de todas formas se ven juntas con `mlflow ui`.

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

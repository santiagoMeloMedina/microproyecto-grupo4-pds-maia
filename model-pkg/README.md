# `model_riesgo_retraso` — modelo empaquetado

Paquete instalable con el modelo de riesgo de retraso por franja de itinerario: el
ganador de los 90 experimentos de la Entrega 2. El wheel incluye el pipeline ya
entrenado, de modo que instalarlo basta para predecir, sin necesidad del
repositorio, del CSV ni de tener `airlines_ml` en el `PYTHONPATH`.

## Por qué existe, si ya está `airlines_ml`

Son dos paquetes con propósitos distintos y conviene no mezclarlos.

`airlines_ml` es el paquete de **experimentación**: contiene las tres familias de
modelos, sus espacios de búsqueda, las tres líneas base y la configuración de
MLflow. Sirve para responder *qué modelo elegir* y es lo que consume el notebook
de modelado.

`model_riesgo_retraso` es el paquete de **producción**: contiene una sola
configuración, la que ganó, sin ramas ni alternativas. Sirve para responder *cuál
es el riesgo de este itinerario* y es lo que consume la API. Al no depender del
repositorio se puede instalar dentro de un contenedor con un solo `pip install`.

## Estructura

```
model-pkg/
├── model_riesgo_retraso/
│   ├── config.yml              parámetros del modelo y del punto de operación
│   ├── config/core.py          carga y validación del YAML con pydantic
│   ├── processing/
│   │   ├── features.py         variables derivadas y transformadores
│   │   ├── data_manager.py     carga, partición temporal y persistencia
│   │   └── validation.py       esquemas de entrada (DataInputSchema)
│   ├── pipeline.py             definición del pipeline de producción
│   ├── train_pipeline.py       entrenamiento reproducible
│   ├── predict.py              interfaz de predicción
│   └── trained_models/         el pipeline entrenado (se genera, no se versiona)
├── requirements/
├── tests/
├── setup.py
└── tox.ini
```

## Uso

### Entrenar

Requiere `data/airlines.csv` en la raíz del repositorio (`dvc pull`) o la variable
de entorno `AIRLINES_CSV` apuntando al archivo.

```bash
cd model-pkg
tox run -e train
```

Ajusta el pipeline sobre los días 0–24 —la misma ventana del reajuste final de la
Entrega 2—, lo evalúa una sola vez sobre el bloque de prueba 25–30 y lo guarda en
`trained_models/` junto con un `metadata.json` que registra las métricas
obtenidas.

Para entrenar con GPU en Colab, exporte `XGBOOST_DEVICE=cuda`. La GPU acelera el
ajuste pero no mejora el resultado: el AUC es idéntico en CPU y en GPU.

### Probar

```bash
cd model-pkg
tox run -e test_package
```

Entrena y corre las pruebas unitarias. Además de verificar el contrato de entrada
y la coherencia de las bandas, una prueba comprueba que el AUC sobre el bloque de
prueba supere la línea base del proyecto (0,6763), de modo que una regresión de
desempeño rompe la construcción en lugar de pasar inadvertida.

### Construir el wheel

```bash
cd model-pkg
python -m build
```

Genera `dist/model_riesgo_retraso-0.0.1-py3-none-any.whl` (4,4 MB) con el pipeline
entrenado dentro.

### Instalar y predecir

```bash
pip install model_riesgo_retraso-0.0.1-py3-none-any.whl
```

```python
from model_riesgo_retraso.predict import make_prediction

resultado = make_prediction(input_data=[{
    "Airline": "WN", "AirportFrom": "LAS", "AirportTo": "PHX",
    "DayOfWeek": 3, "Time": 480, "Length": 65,
}])

resultado["predictions"]  # [0.5555]
resultado["bands"]        # ['medio']
resultado["errors"]       # None
```

`Time` va en minutos desde medianoche y `DayOfWeek` de 1 a 7. Una entrada fuera de
rango no llega al modelo: `predictions` vuelve en `None` y el detalle queda en
`errors`, para que la API pueda responder 400 en lugar de un 500 opaco. Una
categoría no vista en entrenamiento —una aerolínea o un aeropuerto nuevo— no
rompe: queda como `NaN`, que XGBoost maneja de forma nativa.

## Reproducibilidad

El entrenamiento del paquete reproduce las métricas publicadas en la Entrega 2,
que se obtuvieron en Google Colab sobre una GPU T4:

| Métrica | Entrega 2 (GPU) | Paquete (CPU) |
|---|---|---|
| ROC-AUC | 0,6974 | 0,6974 |
| PR-AUC | 0,7309 | 0,7308 |
| Brier | 0,2292 | 0,2292 |
| Precisión @ 0,553 | 0,7993 | 0,7980 |
| Recall @ 0,553 | 0,3139 | 0,3135 |

Las diferencias en la cuarta cifra provienen de la construcción de histogramas de
XGBoost, que no es idéntica entre CPU y GPU. El ordenamiento —que es lo que mide
el AUC y lo que usa el tablero— es el mismo.

## Versiones fijas

`requirements/requirements.txt` fija versiones exactas y no rangos. El pipeline se
serializa con pickle, y pickle no garantiza compatibilidad entre versiones de
scikit-learn ni de xgboost: entrenar con una versión y servir con otra es la causa
más común de que un modelo empaquetado falle en producción sin dar un error claro.

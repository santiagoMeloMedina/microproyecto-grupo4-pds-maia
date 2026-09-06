# Exploration

Esta carpeta es donde cada integrante del equipo hace su propia exploración de los datos, normalmente en un notebook (ej. `<nombre>-<tema>.ipynb`).

El análisis consolidado de calidad, distribuciones y asociaciones con los retrasos está disponible
en [pilar-airlines-report.md](pilar-airlines-report.md).

## Datos

Los datos se importan desde `data/` en la raíz del proyecto. Por ejemplo, desde un notebook dentro de `exploration/`:

```python
import pandas as pd

airlines = pd.read_csv("../data/airlines.csv")
```

## Dependencias

Si tu exploración necesita una librería que no está instalada, agrégala a [requirements.txt](requirements.txt).

Estas dependencias se instalan automáticamente al correr `make install` desde la raíz del proyecto (el script de instalación instala `exploration/requirements.txt` dentro del `.venv/`).

## Kernel

Para correr los notebooks, selecciona como kernel el intérprete de `.venv/` (creado por `make install`). Ver la sección de instalación en el [README](../README.md) de la raíz para más detalle.

# Entorno en Windows

`scripts/install.sh` y `scripts/update_data.sh` no corren en Windows: `python3` no existe como
comando y el entorno virtual se crea en `.venv\Scripts\`, no en `.venv/bin/`. Instalar `make` no
lo resuelve, porque el fallo está dentro del script.

Aquí están los equivalentes en PowerShell. Los scripts originales no se modificaron: en macOS y
Linux todo sigue igual.

| macOS / Linux | Windows |
|---|---|
| `make install` | `powershell -ExecutionPolicy Bypass -File scripts\windows\install.ps1` |
| `make update-data` | `powershell -ExecutionPolicy Bypass -File scripts\windows\update_data.ps1` |
| `source .venv/bin/activate` | `.\.venv\Scripts\Activate.ps1` |

Con GNU Make instalado, esta carpeta incluye un `Makefile` con los mismos targets:

```powershell
make -f scripts/windows/Makefile install
make -f scripts/windows/Makefile update-data
```

Todo se ejecuta desde la raíz del repositorio.

**Kernel de notebooks:** seleccionar `.venv\Scripts\python.exe` como intérprete.

**Alternativa:** dentro de WSL con una distro Linux, el `Makefile` de la raíz funciona sin cambios.

---

# Obtener los datos

`data/` está en `.gitignore`; solo se versiona el puntero `data/airlines.csv.dvc`.

## `dvc pull` del remote del proyecto

El remote es `s3://microproyecto-grupo4-pds-maia`, en una cuenta de AWS Academy Learner Lab. Dos
limitaciones: las credenciales son temporales e incluyen un `aws_session_token`, y Learner Lab no
permite crear usuarios IAM, así que no hay acceso entre cuentas.

```powershell
aws configure --profile dvc-user
aws configure set aws_session_token "<token de la sesion>" --profile dvc-user
dvc remote modify --local aws-remote profile dvc-user
dvc pull
```

El token debe renovarse cada vez que se reinicie el laboratorio.

## Remote propio

La bandera `--local` escribe en `.dvc/config.local`, que está en `.dvc/.gitignore` y no afecta al
equipo.

```powershell
aws s3 mb s3://<nombre-del-bucket> --region us-east-1 --profile dvc-user
dvc remote add mi-remote s3://<nombre-del-bucket> --local
dvc remote modify mi-remote profile dvc-user --local
dvc push --remote mi-remote
```

Recuperar después: `dvc pull --remote mi-remote`.

## `rebuild_dataset.py`

Utilidad de verificación. `airlines.csv` es la sección `@data` del ARFF de OpenML (id 1169) con la
fila de encabezado antepuesta. El script lo reconstruye y comprueba que el MD5 coincida con el del
puntero DVC. Sirve para validar el origen de los datos y para hacer pruebas sin credenciales.

```powershell
Invoke-WebRequest -Uri "https://openml.org/data/v1/download/66526/airlines.arff" `
  -OutFile "$env:TEMP\airlines.arff" -UseBasicParsing
python scripts\windows\rebuild_dataset.py "$env:TEMP\airlines.arff" data\airlines.csv
dvc commit data\airlines.csv.dvc --force
```

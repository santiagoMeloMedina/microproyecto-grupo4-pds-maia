# Manual de instalación

Instalación y despliegue del tablero de riesgo de retraso y de la API que lo
alimenta. La vía recomendada es Docker Compose: levanta todo con un comando y no
exige instalar Python ni Node en la máquina.

---

## 1. Requisitos

| Componente | Versión | Para qué |
|---|---|---|
| Docker Engine | 24 o superior | Despliegue con contenedores (vía recomendada) |
| Docker Compose | v2 o superior | Orquestación de los dos servicios |
| Git | cualquiera | Clonar el repositorio |

Solo si se va a instalar sin Docker, o reentrenar el modelo:

| Componente | Versión | Para qué |
|---|---|---|
| Python | 3.10 – 3.12 | API y paquete del modelo |
| Node.js | 20 o superior | Compilar el tablero |
| DVC con soporte S3 | cualquiera | Descargar `data/airlines.csv`, solo para reentrenar |

---

## 2. Clonar el repositorio

```bash
git clone https://github.com/santiagoMeloMedina/microproyecto-grupo4-pds-maia.git
cd microproyecto-grupo4-pds-maia
```

No hace falta ejecutar `dvc pull`. El modelo entrenado viaja dentro del wheel en
`api/model-package/` y el histórico de vuelos está versionado en
`dashboard/data/vuelos.parquet`. El CSV original, de 19 MB, solo se necesita para
reentrenar desde cero.

---

## 3. Despliegue con Docker Compose (recomendado)

```bash
docker compose up --build
```

La primera construcción tarda varios minutos: instala XGBoost y compila el
tablero. Al terminar:

| Servicio | Dirección |
|---|---|
| Tablero | http://localhost:8080 |
| API (documentación interactiva) | http://localhost:8002/docs |
| API (estado) | http://localhost:8002/api/v1/health |

Para detenerlo:

```bash
docker compose down
```

### Si el puerto 8080 está ocupado

Es frecuente en Windows. El puerto del tablero se cambia con `UI_PORT`, que
ajusta también los orígenes que la API acepta por CORS:

```bash
UI_PORT=8088 docker compose up --build
```

En PowerShell:

```powershell
$env:UI_PORT = "8088"; docker compose up --build
```

> **Importante:** no basta con cambiar el puerto publicado a mano en el
> `docker-compose.yml`. El navegador envía el encabezado `Origin` con el puerto
> desde el que se sirve el tablero, y la API compara ese valor por igualdad
> exacta. Si ambos no coinciden, la interfaz carga pero queda sin datos. Usar
> `UI_PORT` mantiene las dos cosas sincronizadas.

---

## 4. Despliegue en una instancia EC2

1. Lanzar una instancia con Ubuntu 24.04. Se recomienda **t3.small** o superior
   con 20 GB de disco; la API carga el modelo y el histórico en memoria.

2. Abrir en el grupo de seguridad los puertos **8002** (API) y **8080** (tablero),
   con origen *Anywhere IPv4*.

3. Conectarse e instalar Docker:

   ```bash
   ssh -i llave.pem ubuntu@IP_PUBLICA

   sudo apt update
   sudo apt install -y docker.io docker-compose-v2 git
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```

4. Clonar y levantar, indicando la IP pública para que el tablero sepa dónde
   está la API:

   ```bash
   git clone https://github.com/santiagoMeloMedina/microproyecto-grupo4-pds-maia.git
   cd microproyecto-grupo4-pds-maia

   PUBLIC_HOST=http://IP_PUBLICA:8002 docker compose up --build -d
   ```

   `PUBLIC_HOST` es obligatorio en un despliegue remoto. Vite congela esa URL
   dentro del bundle durante la construcción, así que un tablero compilado
   apuntando a `localhost` seguirá buscando la API en la máquina del visitante y
   no en el servidor.

5. Verificar:

   ```bash
   curl http://IP_PUBLICA:8002/api/v1/health
   ```

   El tablero queda en `http://IP_PUBLICA:8080`.

---

## 5. Instalación local sin Docker

Útil para desarrollar. Requiere dos terminales.

### API

```bash
cd api
pip install tox
tox run -e run
```

`tox` crea su propio entorno virtual, instala el paquete del modelo desde el
wheel y levanta uvicorn en el puerto 8002.

### Tablero

```bash
cd ui
cp .env.example .env.local
npm ci
npm run dev
```

Queda en http://localhost:5173, que ya está entre los orígenes que la API acepta
por defecto.

---

## 6. Reentrenar el modelo

Solo si se quiere regenerar el artefacto. Requiere el CSV original.

```bash
dvc pull                    # descarga data/airlines.csv (19 MB)

cd model-pkg
tox run -e test_package     # entrena y corre las pruebas
python -m build             # genera dist/*.whl

cp dist/model_riesgo_retraso-0.0.1-py3-none-any.whl ../api/model-package/
```

El entrenamiento toma alrededor de un minuto en CPU. Para usar GPU en Colab,
exportar `XGBOOST_DEVICE=cuda`; acelera el ajuste pero no cambia el resultado.

Si cambia el histórico, regenerar también el parquet del tablero:

```bash
python scripts/generar_datos_tablero.py
```

---

## 7. Verificar la instalación

```bash
cd api    && tox run -e test_app        # 12 pruebas de la API
cd model-pkg && tox run -e test_package # 7 pruebas del modelo
```

Las pruebas del paquete incluyen una compuerta de desempeño: fallan si el
ROC-AUC del modelo cae por debajo de la línea base del proyecto (0,6763).

---

## 8. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| El tablero carga pero todo aparece vacío | El origen del tablero no coincide con el que acepta la API | Levantar con `UI_PORT`, o revisar `BACKEND_CORS_ORIGINS` |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | Otro servicio usa el 8080 | `UI_PORT=8088 docker compose up` |
| El tablero busca la API en `localhost` desde otra máquina | Se construyó sin `PUBLIC_HOST` | Reconstruir con `PUBLIC_HOST=http://IP:8002 docker compose build ui` |
| `libgomp.so.1: cannot open shared object file` | Falta la librería de OpenMP que usa XGBoost | Ya resuelto en el `Dockerfile`; en instalación manual, `sudo apt install libgomp1` |
| `No se encontro .../data/airlines.csv` | Solo ocurre al reentrenar | `dvc pull`, o definir `AIRLINES_CSV` |
| Recargar `/franjas` da 404 | Falta el `try_files` de nginx | Ya resuelto en `ui/nginx.conf`; ocurre si se sirve `dist/` con otro servidor |
| La primera consulta tarda varios segundos | La API puntúa las 92.250 franjas al arrancar | Es esperado y ocurre una sola vez por proceso |

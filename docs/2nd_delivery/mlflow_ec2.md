# Servidor de MLflow en EC2

Guía para levantar el servidor de seguimiento donde se consolidan los experimentos del equipo.

> **Encender la instancia no es suficiente.** Arrancar la máquina solo levanta el sistema
> operativo; el servidor de MLflow hay que instalarlo (§2–§4) y dejarlo corriendo. Si ya se instaló
> en una sesión anterior con el servicio de systemd de §4, arranca solo al encender y basta con
> verificarlo. Si no, hay que hacer §2 a §4 una vez.
>
> **La IP pública cambia** cada vez que la instancia se detiene y se vuelve a encender, salvo que
> tenga una IP elástica asignada. Después de encenderla hay que tomar la IP nueva de la consola de
> EC2 y actualizar el `.env`.

## 0. Ruta rápida si la instancia ya está encendida

```bash
# 1. Conectarse (desde CMD, PowerShell o Git Bash)
ssh -i ruta\a\tu-llave.pem ubuntu@<ip-publica>

# 2. ¿Ya está corriendo el servidor?
sudo systemctl status mlflow          # si existe el servicio de §4
curl http://localhost:5000/health     # debe responder OK

# 3. Si no está corriendo
sudo systemctl start mlflow
```

Si `systemctl status mlflow` responde `Unit mlflow.service could not be found`, el servidor nunca se
instaló en esa máquina: seguir desde §2.

Como alternativa a SSH, la consola de AWS ofrece **EC2 Instance Connect** (botón *Connect* en la
instancia), que abre una terminal en el navegador sin necesidad de la llave `.pem`.

## 1. Instancia

| | |
|---|---|
| AMI | Ubuntu Server 24.04 LTS |
| Tipo | `t2.medium` — 2 vCPU y 4 GB de RAM |
| Almacenamiento | 20 GB |
| Grupo de seguridad | SSH (22) desde tu IP · TCP 5000 |

**Sobre el tipo de instancia.** El entrenamiento **no corre aquí**: la máquina solo hospeda el
servidor de seguimiento, que recibe parámetros y métricas y guarda un artefacto de unos 10 MB al
final. Lo que pesa no es el cómputo sino la memoria, porque MLflow levanta varios *workers* de
gunicorn y la interfaz web es una aplicación de varios megabytes.

Por eso `t2.medium` (4 GB) va más holgado que `t3.small` (2 GB), aunque ambos tengan 2 vCPU: lo
que los diferencia es la RAM, no el procesador.

> **Sobre el puerto 5000.** Si el entrenamiento corre desde Google Colab, la IP de origen es
> dinámica y hay que abrirlo a `0.0.0.0/0`. MLflow no trae autenticación, así que mientras esa
> regla esté activa cualquiera que conozca la IP puede leer y borrar experimentos: conviene
> **detener la instancia apenas se terminen de tomar las evidencias**. Si el entrenamiento corre
> en local, basta con abrirlo a la IP propia.

## 2. Instalación

Una sola vez por instancia. Si se elimina y se crea otra hay que repetirlo: el disco se va con la
instancia.

```bash
sudo apt update && sudo apt install -y python3-venv
python3 -m venv ~/env-mlflow
source ~/env-mlflow/bin/activate
pip install "mlflow==3.15.2" boto3
mlflow --version
```

## 3. Backend

MLflow 3 dejó en mantenimiento el backend de archivos (`./mlruns`) y exige uno de base de datos.
SQLite basta para el volumen de este proyecto:

```bash
mkdir -p ~/mlflow/artifacts
```

## 4. Servicio

```bash
sudo tee /etc/systemd/system/mlflow.service > /dev/null <<'EOF'
[Unit]
Description=MLflow Tracking Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/mlflow
ExecStart=/home/ubuntu/env-mlflow/bin/mlflow server \
  --backend-store-uri sqlite:////home/ubuntu/mlflow/mlflow.db \
  --artifacts-destination /home/ubuntu/mlflow/artifacts \
  --serve-artifacts \
  --allowed-hosts '*' \
  --cors-allowed-origins '*' \
  --workers 2 \
  --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now mlflow
sudo systemctl status mlflow
```

La UI queda en `http://<ip-publica>:5000`.

> **Por qué cuatro barras en `sqlite:////`.** En SQLAlchemy tres barras indican ruta
> **relativa** y cuatro, absoluta. Con `sqlite:///home/ubuntu/mlflow/mlflow.db` y
> `WorkingDirectory=/home/ubuntu/mlflow`, la base termina en
> `/home/ubuntu/mlflow/home/ubuntu/mlflow/mlflow.db`. Funciona, pero la ruta queda anidada y
> confunde al inspeccionarla o respaldarla.

> **Por qué `--cors-allowed-origins`.** Por defecto MLflow solo acepta peticiones cuyo origen
> sea `localhost`. Al abrir la interfaz por la IP pública, el navegador envía
> `Origin: http://<ip>:5000` y el servidor bloquea todo lo que modifique datos —borrar un
> experimento, renombrar una corrida— con un error de *cross-origin request blocked*.

> **Por qué `--workers 2`.** El valor por defecto es 4, y en una máquina de 2 vCPU los procesos
> compiten entre sí por CPU y memoria. Para un servidor que usa un equipo pequeño bastan dos, y
> la interfaz responde bastante mejor.

> **Por qué `--allowed-hosts`.** MLflow 3 valida el header `Host` de cada petición para prevenir
> ataques de *DNS rebinding*, y por defecto solo acepta `localhost` y direcciones privadas
> (`10.*`, `192.168.*`, `172.16-31.*`). Al entrar por la **IP pública** el servidor responde
> `Invalid Host header - possible DNS rebinding attack detected`, tanto desde el navegador como
> desde el cliente de Python.
>
> Se usa `'*'` en vez de la IP concreta porque la IP pública cambia en cada encendido de la
> instancia; fijarla obligaría a editar el servicio cada vez. Es aceptable aquí porque el servidor
> se apaga al terminar la entrega. Para algo permanente, lo correcto sería listar el dominio o la
> IP elástica: `--allowed-hosts 'mlflow.midominio.com,54.1.2.3:5000'`.

> **Por qué `--artifacts-destination` y no `--default-artifact-root`.** Son dos modos distintos y la
> diferencia importa cuando el entrenamiento corre fuera de la instancia:
>
> - `--default-artifact-root /ruta` le devuelve al cliente **esa ruta del sistema de archivos**, y el
>   cliente intenta escribir ahí. Si el entrenamiento corre en un equipo Windows, esa ruta de Linux
>   no existe y la subida del modelo falla.
> - `--artifacts-destination` con `--serve-artifacts` hace que el cliente suba los artefactos **por
>   HTTP a través del servidor**, que es quien los guarda. Es el modo que funciona con clientes
>   remotos, y el único viable en este proyecto.

## 5. Apuntar el notebook al servidor

El notebook no requiere cambios: lee `MLFLOW_TRACKING_URI`. Hay tres formas de definirla, en orden
de precedencia.

**Opción recomendada — archivo `.env` en la raíz del repositorio.** Está en `.gitignore`, así que la
IP de cada quien no viaja al repositorio compartido, y no obliga a abrir una terminal nueva.

```bash
cp .env.example .env
```

Y editar la línea:

```
MLFLOW_TRACKING_URI=http://<ip-publica>:5000
```

**Variable de entorno**, si se prefiere no crear el archivo:

```powershell
$env:MLFLOW_TRACKING_URI = "http://<ip-publica>:5000"   # PowerShell, sesión actual
setx MLFLOW_TRACKING_URI "http://<ip-publica>:5000"     # Windows, requiere terminal nueva
```

```bash
export MLFLOW_TRACKING_URI="http://<ip-publica>:5000"   # macOS / Linux / Git Bash
```

**Sin definir nada**, MLflow escribe en SQLite local (`mlflow.db`) y el notebook corre igual.

Verificación desde el equipo local:

```bash
curl http://<ip-publica>:5000/health
```

Si responde, al ejecutar el notebook la primera celda debe imprimir esa misma URI y
`Servidor remoto: True`.
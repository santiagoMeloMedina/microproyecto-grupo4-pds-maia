# Infraestructura AWS

API y tablero en un clúster ECS respaldado por una instancia EC2 `t3.micro`,
con repositorios ECR, IP elástica y logs en CloudWatch.

## Prerrequisitos

- Terraform 1.5 o superior.
- AWS CLI 2 autenticada (`aws sts get-caller-identity`).
- Docker Engine 24 o superior en ejecución.
- Una VPC y una subred pública con salida a Internet.
- Permisos para EC2, ECS, ECR, S3, CloudWatch y lectura de parámetros SSM.

En AWS Academy se reutilizan `LabRole` y `LabInstanceProfile`, porque el
laboratorio no permite crear roles IAM propios. En otra cuenta AWS deben existir
un rol y un perfil de instancia equivalentes; sus nombres se configuran mediante
`lab_role_name` y `lab_instance_profile_name`.

## Deploy

```bash
cd infra
cp .env.example .env
# editar .env: VPC_ID y SUBNET_ID (subnet publica, con salida a internet)

./scripts/build_and_push.sh
```

Eso corre `terraform apply` y luego construye, publica y despliega las dos imagenes.

```bash
terraform output ui_url
terraform output api_url
```

Redespliegue tras un cambio de código:

```bash
./scripts/build_and_push.sh
```

La definición actual de las tareas ECS referencia `latest`. Aunque el script
acepta otro tag para construir y publicar, ese tag no se propaga a Terraform;
por eso el procedimiento reproducible debe ejecutarse sin argumento.

## Verificación y logs

```bash
UI_URL="$(terraform output -raw ui_url)"
API_URL="$(terraform output -raw api_url)"

curl "$API_URL/api/v1/health"
open "$UI_URL"  # macOS
```

Los logs se almacenan en `/ecs/$PROJECT_NAME/api` y
`/ecs/$PROJECT_NAME/ui`. Por ejemplo:

```bash
aws logs tail "/ecs/${PROJECT_NAME:-airlines-delay}/api" --follow
```

## infra/.env

| Variable | Requerida |
|---|---|
| `VPC_ID` | si |
| `SUBNET_ID` | si |
| `TF_STATE_BUCKET` | no, se genera y se guarda solo en `.env` si falta |
| `TF_STATE_PREFIX` | no, default `PROJECT_NAME` |
| `AWS_REGION` | no, default `us-east-1` |
| `PROJECT_NAME` | no, default `airlines-delay` |
| `IMAGE_TAG` | no, default `latest` |

El despliegue del PR #13 está validado de extremo a extremo con el puerto 80 para
la interfaz y el 8002 para la API. Aunque Terraform expone variables de puerto,
cambiarlas exige ajustar también nginx, uvicorn, CORS y la URL de construcción
del frontend. En particular, la configuración CORS actual omite el puerto de la
interfaz porque presupone HTTP en el puerto 80.

## Costos y destrucción

La arquitectura usa una sola instancia y no incluye balanceador, TLS,
autenticación ni alta disponibilidad. `deployment_minimum_healthy_percent = 0`
permite que exista una interrupción breve durante un redespliegue.

Para evitar costos al finalizar:

```bash
set -a
source .env
set +a
export TF_VAR_aws_region="${AWS_REGION:-us-east-1}"
export TF_VAR_project_name="${PROJECT_NAME:-airlines-delay}"

# Necesario en un clon nuevo o si se elimino .terraform/.
terraform init -input=false -reconfigure \
  -backend-config="bucket=$TF_STATE_BUCKET" \
  -backend-config="key=${TF_STATE_PREFIX:-${PROJECT_NAME:-airlines-delay}}/terraform.tfstate" \
  -backend-config="region=${AWS_REGION:-us-east-1}"

terraform destroy -var="vpc_id=$VPC_ID" -var="subnet_id=$SUBNET_ID"
```

El bucket S3 de estado se crea fuera del estado de Terraform. Si ya no se
utilizará, debe vaciarse y eliminarse por separado después del `destroy`.

## Notas

- El estado de Terraform se guarda en `s3://$TF_STATE_BUCKET/$TF_STATE_PREFIX/terraform.tfstate`.
  Terraform no permite variables dentro del bloque `backend`, asi que el bucket/prefijo se
  pasan por `-backend-config` en `terraform init`, leidos de `.env` por el script. El script
  crea el bucket (con versionado) si no existe.
- Usa `LabRole` / `LabInstanceProfile` (AWS Academy Learner Lab) en vez de crear roles IAM
  propios, porque `iam:CreateRole` esta bloqueado en ese entorno. Si los nombres son otros
  en tu lab, ajustalos con `lab_role_name` / `lab_instance_profile_name`.
- `VITE_API_URL` queda congelado en el bundle del tablero en build time, por eso el script
  aplica Terraform primero (necesita la IP elastica) y construye la imagen despues.
- `t3.micro` = 1 GiB RAM para los dos contenedores + agente ECS. Ajustar `api_task_memory`
  en `variables.tf` si la API cae por OOM.
- Puertos 80 y 8002 abiertos a `0.0.0.0/0` por defecto
  (`public_ingress_cidr`). Restringir este CIDR fuera del laboratorio.

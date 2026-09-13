# Infra

API + tablero en un cluster ECS (EC2), una sola `t3.micro`, con IP elastica.

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

Redeploy tras un cambio de codigo:

```bash
./scripts/build_and_push.sh        # tag latest
./scripts/build_and_push.sh v2     # tag especifico
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
- Puertos 80 y 8002 abiertos a `0.0.0.0/0` por defecto (`public_ingress_cidr`).

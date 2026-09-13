#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$INFRA_DIR/.." && pwd)"

ENV_FILE="$INFRA_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

export TF_VAR_vpc_id="${VPC_ID:?VPC_ID no esta definido en infra/.env}"
export TF_VAR_subnet_id="${SUBNET_ID:?SUBNET_ID no esta definido en infra/.env}"
[[ -n "${PROJECT_NAME:-}" ]] && export TF_VAR_project_name="$PROJECT_NAME"
[[ -n "${AWS_REGION:-}" ]] && export TF_VAR_aws_region="$AWS_REGION"

TAG="${1:-${IMAGE_TAG:-latest}}"
STATE_PREFIX="${TF_STATE_PREFIX:-${PROJECT_NAME:-airlines-delay}}"
STATE_REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"

if [[ -z "${TF_STATE_BUCKET:-}" ]]; then
  PROJECT_SLUG="$(echo "${PROJECT_NAME:-airlines-delay}" | tr '[:upper:]' '[:lower:]')"
  STATE_BUCKET="${PROJECT_SLUG}-tfstate-${ACCOUNT_ID: -6}-$(printf '%04x%04x' "$RANDOM" "$RANDOM")"
  echo "==> TF_STATE_BUCKET no definido, generando bucket nuevo: $STATE_BUCKET"
  if grep -q '^TF_STATE_BUCKET=' "$ENV_FILE" 2>/dev/null; then
    sed -i.bak "s/^TF_STATE_BUCKET=.*/TF_STATE_BUCKET=$STATE_BUCKET/" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "TF_STATE_BUCKET=$STATE_BUCKET" >> "$ENV_FILE"
  fi
  echo "==> Guardado en infra/.env para reutilizarlo en la proxima corrida"
else
  STATE_BUCKET="$TF_STATE_BUCKET"
fi

if ! aws s3api head-bucket --bucket "$STATE_BUCKET" --region "$STATE_REGION" 2>/dev/null; then
  echo "==> Creando bucket de estado $STATE_BUCKET"
  if [[ "$STATE_REGION" == "us-east-1" ]]; then
    aws s3api create-bucket --bucket "$STATE_BUCKET" --region "$STATE_REGION"
  else
    aws s3api create-bucket --bucket "$STATE_BUCKET" --region "$STATE_REGION" \
      --create-bucket-configuration "LocationConstraint=$STATE_REGION"
  fi
  aws s3api put-bucket-versioning --bucket "$STATE_BUCKET" --versioning-configuration Status=Enabled
fi

terraform -chdir="$INFRA_DIR" init -input=false -migrate-state -force-copy \
  -backend-config="bucket=$STATE_BUCKET" \
  -backend-config="key=$STATE_PREFIX/terraform.tfstate" \
  -backend-config="region=$STATE_REGION"
terraform -chdir="$INFRA_DIR" apply -auto-approve

tf_output() {
  terraform -chdir="$INFRA_DIR" output -raw "$1"
}

REGION="$(tf_output aws_region)"
ELASTIC_IP="$(tf_output elastic_ip)"
API_REPO="$(tf_output ecr_api_repository_url)"
UI_REPO="$(tf_output ecr_ui_repository_url)"
CLUSTER="$(tf_output ecs_cluster_name)"
API_SERVICE="$(tf_output ecs_api_service_name)"
UI_SERVICE="$(tf_output ecs_ui_service_name)"

aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "==> Construyendo API ($API_REPO:$TAG)"
docker build --platform linux/amd64 -f "$REPO_ROOT/api/Dockerfile" -t "$API_REPO:$TAG" "$REPO_ROOT"
docker push "$API_REPO:$TAG"

echo "==> Construyendo tablero ($UI_REPO:$TAG), VITE_API_URL=http://$ELASTIC_IP:8002"
docker build \
  --platform linux/amd64 \
  --build-arg "VITE_API_URL=http://$ELASTIC_IP:8002" \
  -t "$UI_REPO:$TAG" \
  "$REPO_ROOT/ui"
docker push "$UI_REPO:$TAG"

echo "==> Forzando redespliegue de los servicios ECS"
aws ecs update-service --cluster "$CLUSTER" --service "$API_SERVICE" --force-new-deployment --region "$REGION" >/dev/null
aws ecs update-service --cluster "$CLUSTER" --service "$UI_SERVICE" --force-new-deployment --region "$REGION" >/dev/null

echo
echo "Listo."
echo "  Tablero: http://$ELASTIC_IP"
echo "  API:     http://$ELASTIC_IP:8002/docs"

#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
APP_DIR="${ROOT_DIR}/infra-k8s/manifests/app"
PLATFORM_DIR="${ROOT_DIR}/infra-k8s/manifests/platform"
NAMESPACE="${NAMESPACE:-oficina}"
: "${IMAGE:?IMAGE is required}"
JWT_SECRET="${JWT_SECRET:-}"
WEBHOOK_API_KEY="${WEBHOOK_API_KEY:-}"
DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://oficina:oficina@postgres:5432/oficina_os}"
RABBITMQ_URL="${RABBITMQ_URL:-amqp://guest:guest@rabbitmq:5672/}"
MONGODB_URL="${MONGODB_URL:-mongodb://mongodb:27017}"
INTERNAL_SERVICE_KEY="${INTERNAL_SERVICE_KEY:-dev-internal-key}"
SKIP_PLATFORM="${SKIP_PLATFORM:-true}"
DEPLOY_PLATFORM="${DEPLOY_PLATFORM:-false}"

[[ -n "${JWT_SECRET}" && -n "${WEBHOOK_API_KEY}" ]] || { echo "JWT_SECRET e WEBHOOK_API_KEY obrigatórios" >&2; exit 1; }

kubectl apply -f "${APP_DIR}/namespace.yaml"
if [[ "${DEPLOY_PLATFORM}" == "true" ]]; then
  kubectl apply -f "${PLATFORM_DIR}/"
fi
if [[ "${SKIP_PLATFORM}" != "true" ]]; then
  kubectl apply -f "${APP_DIR}/postgres.yaml"
  kubectl wait --for=condition=ready pod -l app=postgres -n "${NAMESPACE}" --timeout=180s
fi
kubectl apply -f "${APP_DIR}/configmap.yaml"
kubectl create secret generic oficina-os-secrets -n "${NAMESPACE}" \
  --from-literal=DATABASE_URL="${DATABASE_URL}" \
  --from-literal=JWT_SECRET="${JWT_SECRET}" \
  --from-literal=WEBHOOK_API_KEY="${WEBHOOK_API_KEY}" \
  --from-literal=RABBITMQ_URL="${RABBITMQ_URL}" \
  --from-literal=MONGODB_URL="${MONGODB_URL}" \
  --from-literal=INTERNAL_SERVICE_KEY="${INTERNAL_SERVICE_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl delete job oficina-os-service-migration -n "${NAMESPACE}" --ignore-not-found
sed "s|oficina-os-service:latest|${IMAGE}|g" "${APP_DIR}/migration-job.yaml" | kubectl apply -f -
kubectl wait --for=condition=complete job/oficina-os-service-migration -n "${NAMESPACE}" --timeout=180s
sed "s|oficina-os-service:latest|${IMAGE}|g" "${APP_DIR}/deployment.yaml" | kubectl apply -f -
kubectl apply -f "${APP_DIR}/service.yaml" -f "${APP_DIR}/hpa.yaml"
if [[ -f "${APP_DIR}/ingress.yaml" ]]; then
  kubectl apply -f "${APP_DIR}/ingress.yaml"
fi
kubectl rollout status deployment/oficina-os-service -n "${NAMESPACE}" --timeout=180s
echo "Deploy oficina-os-service concluído."

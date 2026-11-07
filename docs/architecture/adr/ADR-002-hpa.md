# ADR-002 — Horizontal Pod Autoscaler (HPA)

- **Status:** Aceito
- **Data:** 2026-09-13

## Contexto

Múltiplas unidades e picos de OS exigem elasticidade da API.

## Decisão

HPA no Deployment `oficina-api`:

- minReplicas: 2
- maxReplicas: 10
- CPU averageUtilization: 70%
- Memory averageUtilization: 80%

Manifesto: `k8s/hpa.yaml` (também espelhado em `oficina-infra-k8s/manifests/hpa.yaml`).

## Consequências

- Requer metrics-server / métricas de recurso no EKS.
- Migrations **não** rodam em cada pod (Job dedicado) para evitar corrida ao escalar.

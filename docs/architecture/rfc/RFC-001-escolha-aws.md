# RFC-001 — Escolha da nuvem: AWS

- **Status:** Aceito
- **Data:** 2026-09-13
- **Autores:** Time Oficina POS

## Contexto

Necessidade de API Gateway, Function Serverless, banco gerenciado, Kubernetes e IaC com entrega acadêmica/corporativa.

## Opções

1. AWS (API Gateway + Lambda + RDS + EKS)
2. GCP (API Gateway/Cloud Endpoints + Cloud Functions + Cloud SQL + GKE)
3. Azure (APIM + Functions + Azure DB + AKS)

## Decisão

Adotar **AWS**.

## Motivos

- Cobertura 1:1 com o enunciado (API Gateway, Lambda, RDS, EKS).
- Ecossistema Terraform maduro (`hashicorp/aws`).
- Documentação e exemplos abundantes para HPA + ALB Controller + Datadog.

## Consequências

- Custo de NAT Gateway / EKS em demos reais — mitigar com ambientes efêmeros.
- Credenciais e OIDC GitHub→AWS necessários nos pipelines.

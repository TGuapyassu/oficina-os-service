# ADR-001 — Comunicação síncrona REST via API Gateway

- **Status:** Aceito
- **Data:** 2026-09-13

## Contexto

Precisamos de um ponto único de entrada para auth serverless e APIs no Kubernetes.

## Decisão

Usar **REST síncrono** atrás do **AWS API Gateway HTTP API**, com rotas:

- `POST /auth/cpf` → Lambda
- `ANY /api/{proxy+}` → ALB/Ingress do EKS (quando configurado)

## Consequências

- Simplicidade operacional e alinhamento ao Swagger/Postman existentes.
- Sem event bus neste ciclo (webhooks permanecem HTTP).

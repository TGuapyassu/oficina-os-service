# ADR-003 — Observabilidade com Datadog + JWT validado na API

- **Status:** Aceito
- **Data:** 2026-09-13

## Contexto

Exigência de latência, CPU/memória K8s, health/uptime, alertas de falha em OS e logs JSON correlacionados.

## Decisão

1. **Datadog** Agent via Helm (`oficina-infra-k8s/modules/datadog`) + `ddtrace` na API.
2. Middleware `X-Request-ID` + logs JSON por request.
3. Métricas de domínio (`os.created`, `os.status_failure`, `integration.error`).
4. Validação do JWT HS256 **na aplicação** (authorizer OIDC nativo do API Gateway não cobre HS256 sem Cognito).

## Dashboards (a configurar no Datadog)

- Volume diário de OS (`os.created`)
- Tempo médio por status (APM spans / logs de transição)
- Erros de integração (`integration.error`)
- Latência p95 das rotas `/os`, `/auth`
- CPU/mem dos pods + HPA desired replicas

## Alertas sugeridos

- Taxa de `os.status_failure` > limiar em 5 min
- `/health` failing em >1 pod
- Erro 5xx API Gateway > 1%

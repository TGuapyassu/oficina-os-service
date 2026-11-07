# Observabilidade — Datadog

## O que é monitorado

| Sinal | Fonte |
|-------|--------|
| Latência das APIs | Datadog APM (`ddtrace`) |
| CPU / memória pods | Datadog Agent + Kubernetes |
| Health / uptime | Probe `/health` + monitor Datadog |
| Falhas de status OS | log/metric `os.status_failure` |
| Erros de integração | `integration.error` |
| Correlação | header `X-Request-ID` + trace id |

## Dashboards sugeridos

1. **Operação diária** — volume `os.created` por dia
2. **Lead time por status** — duração Diagnóstico → Execução → Finalização (spans/logs)
3. **Integrações** — taxa de erro webhook
4. **Cluster** — CPU/mem vs réplicas HPA

## Alertas

- `os.status_failure` acima do limiar
- Pods not ready / healthcheck fail
- p95 latência `/os` > 2s

Configuração do Agent: módulo Terraform `oficina-infra-k8s/modules/datadog` (requer `datadog_api_key`).

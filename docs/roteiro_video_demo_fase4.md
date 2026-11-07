# Roteiro — vídeo Fase 4 (≤ 15 min)

Publique no **YouTube** ou **Vimeo** (não listado) e cole o link no [`README.md`](../README.md) do oficina-os-service.

**Vídeo demonstrativo:** _(cole a URL aqui após gravar)_

## Preparação

1. `docker compose -f docker-compose.stack.yml up --build` (neste repositório)
2. Postman: importar [`oficina-fase4-microservices.postman_collection.json`](postman/oficina-fase4-microservices.postman_collection.json)
3. Abrir RabbitMQ: http://localhost:15672 (guest/guest)
4. GitHub Actions do repo `oficina-os-service` (run verde após `bash scripts/publish-github-repos.sh`)

## Timeline

| Tempo | Conteúdo |
|-------|----------|
| 0:00–1:30 | Objetivo Fase 4 + links GitHub (contracts, os, billing, execution) |
| 1:30–3:00 | Subir stack Compose |
| 3:00–7:00 | Postman **Saga — fluxo feliz** (login → OS → orçamento → pagamento → status) |
| 7:00–9:00 | RabbitMQ: filas `*-service.saga` e routing keys |
| 9:00–11:00 | Falha: `docker compose stop billing-service`, nova OS ou evento; mostrar compensação / `budget.creation_failed` |
| 11:00–13:00 | GitHub Actions: job test + artefato **coverage-report** + build/deploy OS |
| 13:00–14:30 | `correlation_id` nos eventos; header `X-Request-ID` no OS; Mongo `GET /internal/os/{id}/historico` |
| 14:30–15:00 | Checklist README + encerramento |

## Roteiro falha Saga

1. Com stack no ar, criar OS e pausar billing **antes** de `execution.diagnosis_completed` propagar, ou reiniciar billing com `OS_SERVICE_URL` inválido.
2. Mostrar mensagem `budget.creation_failed` na fila e OS retornando a `RECEBIDA` (estoque reposto).

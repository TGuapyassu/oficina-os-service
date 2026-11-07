# oficina-os-service

**GitHub:** https://github.com/TGuapyassu/oficina-os-service

## Cobertura de testes

```bash
pip install -e ../oficina-contracts  # ou git+https://...@v0.1.0
pip install -e ".[dev]"
pytest --cov-report=term-missing --cov-report=html
```

Evidências: [`docs/evidencias/`](docs/evidencias/) · Artefato CI: **coverage-report** no workflow Actions.

## Vídeo demonstrativo

Ver [`README-microservices.md`](../README-microservices.md#vídeo-demonstrativo-15-min) na raiz do monorepo.

Microsserviço de **Ordem de Serviço**, catálogo (clientes, veículos, peças, serviços) e projeção de status.

## Bancos

| Tipo | Uso |
|------|-----|
| PostgreSQL | Agregados, outbox, idempotência (`processed_events`) |
| MongoDB | Timeline imutável `os_events` |

## Saga (coreografia)

Publica `os.created` / `os.items_reserved` via **outbox** após `POST /os`. Consome eventos `budget.*`, `payment.*`, `execution.*` e aplica compensações.

| Evento recebido | Ação |
|-----------------|------|
| `budget.created` | OS → `AGUARDANDO_APROVACAO` |
| `budget.rejected` | OS → `ORCAMENTO_RECUSADO` |
| `payment.confirmed` | Aprova orçamento → `EM_EXECUCAO` |
| `execution.status_changed` | Atualiza status conforme payload |
| `execution.completed` | OS → `FINALIZADA` |
| `budget.creation_failed` | **Compensação:** devolve estoque + OS → `RECEBIDA` |

### Por que coreografia?

Serviços autônomos, sem orquestrador SPOF, alinhado a webhooks Mercado Pago e RabbitMQ. Rastreio via `correlation_id` + Mongo timeline.

## API interna

`GET /internal/os/{id}/items` (header `X-Internal-Service-Key`) — usado pelo Billing.

## Variáveis

`DATABASE_URL`, `RABBITMQ_URL`, `MONGODB_URL`, `INTERNAL_SERVICE_KEY`, `JWT_SECRET`

## Local

```bash
pip install -e ../oficina-contracts
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --port 8001
```

Stack completa: [`../docker-compose.microservices.yml`](../docker-compose.microservices.yml)

## CI/CD

PR → testes (cov ≥80% domain+application), Ruff, SonarCloud (opcional), build Docker, deploy K8s.

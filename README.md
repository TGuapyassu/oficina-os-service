# oficina-os-service

API principal da oficina: cadastro de **clientes**, **veículos**, **catálogo** (peças e serviços) e ciclo de vida da **ordem de serviço**. Publica eventos de domínio via **outbox** no RabbitMQ, consome respostas da Saga e mantém projeções (incluindo timeline em MongoDB quando configurado).

## O que este serviço faz

- Autenticação **JWT** (admin e cliente) e CRUD do domínio operacional.
- Abertura de OS com reserva de peças e publicação de `os.created` / `os.items_reserved`.
- Consumidor de eventos Saga (`budget.*`, `payment.*`, `execution.*`) para atualizar status da OS e compensações (ex.: repor estoque em falha de orçamento).
- Integrações externas legadas em `/integrations` (webhook com `X-Webhook-Key`) para aprovação de orçamento e atualização de status.
- Endpoints internos para os demais microsserviços (`INTERNAL_SERVICE_KEY`).

Persistência principal: **PostgreSQL**. Opcional: **MongoDB** (eventos/timeline), **RabbitMQ** (Saga).

## Ecossistema

| Componente | Repositório | Porta (stack local) |
|------------|-------------|---------------------|
| OS (este) | `oficina-os-service` | 8000 |
| Billing | `oficina-billing-service` | 8003 |
| Execution | `oficina-execution-service` | 8002 |
| Contratos | [`oficina-contracts/`](oficina-contracts/) (local, v0.1.0) | — |

Arquitetura detalhada: [`docs/architecture/`](docs/architecture/) · visão dos serviços: [`docs/architecture/components.md`](docs/architecture/components.md).

## Pré-requisitos

- Python **3.11+** e Docker / Docker Compose (para stack completa).
- Pacote vendored [`oficina-contracts/`](oficina-contracts/) neste repositório (Docker e `pip install -e ./oficina-contracts` antes do serviço).

## Como rodar

### Stack completa (recomendado)

Na máquina de desenvolvimento, as três pastas devem ser **irmãs** (ex.: `pos/oficina-os-service`, `pos/oficina-billing-service`, `pos/oficina-execution-service).

```bash
cd oficina-os-service
docker compose -f docker-compose.stack.yml up --build
```

| Recurso | URL |
|---------|-----|
| Swagger (OS) | http://localhost:8000/docs |
| Swagger (Billing) | http://localhost:8003/docs |
| Swagger (Execution) | http://localhost:8002/docs |
| RabbitMQ Management | http://localhost:15672 (guest/guest) |

**Fluxo operacional típico** (também coberto no Postman Saga):

1. `POST /auth/login` → token admin.
2. Cadastrar cliente, veículo, peças/serviços e `POST /os`.
3. Após eventos, consultar orçamento em `GET http://localhost:8003/orcamentos/os/{id}`.
4. `POST .../decisao` e, em dev, `POST .../pagamento/simular-aprovado`.
5. `GET /os/{id}` — status atualizado pela coreografia.

### Só o OS (API + Postgres)

Útil para desenvolver o domínio sem billing/execution. A Saga **não** funciona por completo sem RabbitMQ.

```bash
cp .env.example .env   # ajuste JWT_SECRET e demais
docker compose up --build
```

API em http://localhost:8000/docs.

### Desenvolvimento local (Python)

```bash
pip install -e ./oficina-contracts
pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg2://oficina:oficina@localhost:5432/oficina_os
export RABBITMQ_URL=amqp://guest:guest@localhost:5672/   # opcional
export MONGODB_URL=mongodb://localhost:27017              # opcional
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Principais variáveis (ver também [`.env.example`](.env.example)):

| Variável | Uso |
|----------|-----|
| `DATABASE_URL` | PostgreSQL (ou SQLite em testes) |
| `JWT_SECRET` | Assinatura dos tokens |
| `WEBHOOK_API_KEY` | Header `X-Webhook-Key` em `/integrations` |
| `RABBITMQ_URL` | Outbox + consumidor Saga |
| `MONGODB_URL` | Timeline / projeções |
| `INTERNAL_SERVICE_KEY` | Chamadas entre serviços |

## API e Postman

- OpenAPI: **http://localhost:8000/docs**
- Fluxo integrado: [`docs/postman/oficina-saga-microservices.postman_collection.json`](docs/postman/oficina-saga-microservices.postman_collection.json)

## Testes

```bash
pip install -e ".[dev]"
pytest
```

Cobertura mínima **80%** em `app/domain` e `app/application`. Evidências: [`docs/evidencias/cobertura-local.txt`](docs/evidencias/cobertura-local.txt) e [`cobertura-resumo.svg`](docs/evidencias/cobertura-resumo.svg). Relatório HTML: `docs/evidencias/htmlcov/` após o `pytest`.

## Infraestrutura

| Pasta | Conteúdo |
|-------|----------|
| `infra-db/` | Terraform (RDS `oficina_os`) |
| `infra-k8s/manifests/app/` | Deploy da API |
| `infra-k8s/manifests/platform/` | RabbitMQ e Redis (namespace compartilhado) |
| `scripts/k8s-deploy.sh` | Aplicação dos manifests |

Exemplo de deploy:

```bash
export IMAGE=ghcr.io/OWNER/oficina-os-service:TAG
export DEPLOY_PLATFORM=true   # primeira vez: RabbitMQ/Redis
export JWT_SECRET=... WEBHOOK_API_KEY=...
bash scripts/k8s-deploy.sh
```

## Documentação adicional

- Eventos Saga (este serviço): [`docs/architecture/saga-events.md`](docs/architecture/saga-events.md)
- ADR coreografia: [`docs/architecture/adr/ADR-004-saga-choreography-rabbitmq.md`](docs/architecture/adr/ADR-004-saga-choreography-rabbitmq.md)
- DDD / Event Storming: [`docs/ddd_documentacao_event_storming.md`](docs/ddd_documentacao_event_storming.md)

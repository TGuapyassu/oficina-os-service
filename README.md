# oficina-os-service — Entrega Fase 4

Microsserviço principal: **clientes, veículos, catálogo, ordens de serviço**, outbox Saga, MongoDB timeline.

**GitHub:** https://github.com/TGuapyassu/oficina-os-service

## Repositórios do workspace

| Serviço | Repo |
|---------|------|
| OS (este) | https://github.com/TGuapyassu/oficina-os-service |
| Billing | https://github.com/TGuapyassu/oficina-billing-service |
| Execution | https://github.com/TGuapyassu/oficina-execution-service |
| Contratos (pip) | https://github.com/TGuapyassu/oficina-contracts @ `v0.1.0` |

## Estrutura do repositório

- `app/` — FastAPI + DDD
- `infra-db/` — Terraform RDS (`oficina_os`)
- `infra-k8s/manifests/app` — deploy da API
- `infra-k8s/manifests/platform` — RabbitMQ + Redis (plataforma Saga)
- `docker-compose.stack.yml` — stack local dos 3 microsserviços
- `docs/` — arquitetura, Postman, roteiro de vídeo

## Stack local

Na raiz do workspace (`pos/`) devem existir apenas as 3 pastas de microsserviços.

```bash
cd oficina-os-service
docker compose -f docker-compose.stack.yml up --build
```

- OS API: http://localhost:8000/docs  
- Billing: http://localhost:8003/docs  
- Execution: http://localhost:8002/docs  
- RabbitMQ: http://localhost:15672  

## Fluxo Saga (manual)

1. `POST /auth/login` → token admin  
2. Cadastros + `POST /os`  
3. `GET http://localhost:8003/orcamentos/os/{id}`  
4. `POST .../decisao` → `POST .../pagamento/simular-aprovado`  
5. `GET /os/{id}` — status avança via eventos  

Postman: [`docs/postman/oficina-fase4-microservices.postman_collection.json`](docs/postman/oficina-fase4-microservices.postman_collection.json)

## Cobertura de testes

```bash
pip install "oficina-contracts @ git+https://github.com/TGuapyassu/oficina-contracts.git@v0.1.0"
pip install -e ".[dev]"
pytest --cov-report=term-missing --cov-report=html
```

Artefato CI: **coverage-report**. Evidências: [`docs/evidencias/`](docs/evidencias/) (relatório `cobertura-local.txt` + resumo visual).

## Deploy Kubernetes

```bash
export IMAGE=ghcr.io/OWNER/oficina-os-service:TAG
export DEPLOY_PLATFORM=true  # primeira vez: RabbitMQ/Redis
export JWT_SECRET=... WEBHOOK_API_KEY=...
bash scripts/k8s-deploy.sh
```

## Saga e compensações

- [docs/architecture/saga-events.md](docs/architecture/saga-events.md)
- [docs/architecture/adr/ADR-004-saga-choreography-rabbitmq.md](docs/architecture/adr/ADR-004-saga-choreography-rabbitmq.md)

## Publicar no GitHub

```bash
chmod +x scripts/publish-all-repos.sh
GITHUB_OWNER=TGuapyassu bash scripts/publish-all-repos.sh
```

## Vídeo demonstrativo (≤ 15 min)

URL: _(cole após gravar)_  
Roteiro: [`docs/roteiro_video_demo_fase4.md`](docs/roteiro_video_demo_fase4.md)

## Checklist Fase 4

- [ ] 3 repos no GitHub
- [ ] `infra-db` + `infra-k8s` por serviço
- [ ] CI verde + artefato cobertura
- [ ] Postman Saga
- [ ] Vídeo linkado acima

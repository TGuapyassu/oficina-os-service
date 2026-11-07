# Componentes — microsserviços

| Componente | Repo | Função |
|------------|------|--------|
| OS Service | `oficina-os-service` | Catálogo, OS, outbox, Mongo timeline, platform K8s (RabbitMQ/Redis) |
| Billing | `oficina-billing-service` | Orçamento, Mercado Pago |
| Execution | `oficina-execution-service` | Fila Redis, work orders |
| Contratos | `oficina-os-service/oficina-contracts/` | Envelope Saga |
| RDS | `infra-db/` em cada repo | PostgreSQL por serviço |
| EKS/ manifests | `infra-k8s/` em cada repo | Deploy por serviço |

Clientes entram pela **API do OS Service** (auth admin + CRUD). Billing e Execution expõem APIs próprias para orçamento/pagamento e fila.

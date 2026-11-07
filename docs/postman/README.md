# Collection Postman — Oficina API

## Importar

1. Abra o Postman.
2. **Import** → [`oficina-api.postman_collection.json`](oficina-api.postman_collection.json).
3. Variáveis:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `baseUrl` | `http://localhost:8000` | API no EKS/local |
| `apiGatewayUrl` | `http://localhost:8000` | Em cloud: endpoint do API Gateway |
| `token` | (vazio) | JWT admin (Login) |
| `clienteToken` | (vazio) | JWT CPF (Login CPF) |
| `webhookKey` | `dev-webhook-key` | Integrações |
| `osId` | `1` | ID da OS |

## Fluxos

1. **Admin:** Auth → Login → OS / Clientes / etc.
2. **Cliente:** Auth CPF → Me / GET OS (Bearer `clienteToken`).
3. **Integrações:** header `X-Webhook-Key`.

## Swagger

- Local: http://localhost:8000/docs
- Arquitetura: [`../architecture/`](../architecture/)

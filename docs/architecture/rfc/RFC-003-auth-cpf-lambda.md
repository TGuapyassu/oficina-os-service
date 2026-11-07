# RFC-003 — Autenticação serverless por CPF

- **Status:** Aceito
- **Data:** 2026-09-13

## Contexto

Direção exige proteger rotas sensíveis com autenticação via CPF, usando Function Serverless.

## Decisão

Lambda `POST /auth/cpf` (via API Gateway): valida CPF → consulta `clientes` no RDS → JWT HS256 (`sub=cpf`, `cliente_id`, `typ=cliente`).

Admin permanece com `POST /auth/login` (e-mail/senha) na API.

## Motivos

- Atende requisito de serverless + CPF.
- Reaproveita `cpf_cnpj` único já modelado.
- Mesmo `JWT_SECRET` compartilhado com `oficina-api` simplifica validação.

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| CPF sozinho é fator fraco | MVP acadêmico; evolução: OTP/SMS ou Cognito |
| JWT authorizer OIDC no APIGW | Validação HS256 na API (ADR-003) |

## Contrato

```json
POST /auth/cpf
{ "cpf": "39053344705" }

→ 200 { "access_token": "...", "token_type": "bearer", "cliente_id": 1 }
```

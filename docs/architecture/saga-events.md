# Eventos Saga — OS Service

## Publica

| Routing key | Momento |
|-------------|---------|
| `os.created` | Após `POST /os` (outbox) |
| `os.items_reserved` | Mesma transação |

## Consome

| Routing key | Efeito |
|-------------|--------|
| `budget.created` | `AGUARDANDO_APROVACAO` |
| `budget.rejected` | `ORCAMENTO_RECUSADO` |
| `payment.confirmed` | Aprova → `EM_EXECUCAO` |
| `execution.status_changed` | Patch status |
| `execution.completed` | `FINALIZADA` |
| `budget.creation_failed` | **Compensação:** repõe peças, `RECEBIDA` |

Implementação: `app/application/saga/os_handlers.py`, outbox em `app/infrastructure/messaging/outbox.py`.

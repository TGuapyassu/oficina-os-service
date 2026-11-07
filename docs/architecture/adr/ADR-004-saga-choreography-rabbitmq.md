# ADR-004 — Saga coreografada com RabbitMQ

## Contexto

Abertura de OS, orçamento, pagamento e execução passaram a ser microsserviços com bancos isolados.

## Decisão

**Coreografia** via exchange topic `oficina.events` (RabbitMQ), envelope `DomainEvent` (`oficina-contracts`), outbox no OS Service e consumidores idempotentes.

## Consequências

- Sem orquestrador central; compensações explícitas (`budget.creation_failed`, liberação de estoque).
- Rastreio distribuído com `correlation_id` e timeline MongoDB.
- APIs REST por serviço; consistência eventual via eventos.

## Alternativa rejeitada

Saga orquestrada — adicionaria SPOF e acoplamento ao deploy do orquestrador.

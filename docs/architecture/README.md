# Arquitetura — OS Service

## Bounded context

Clientes, veículos, catálogo, ordem de serviço (agregado raiz), outbox e projeção de status.

```mermaid
flowchart LR
  API[REST_API]
  PG[(PostgreSQL)]
  Mongo[(MongoDB_timeline)]
  RMQ[RabbitMQ]
  API --> PG
  API --> Mongo
  API --> RMQ
  RMQ --> API
```

## Ecossistema

Visão dos três serviços e dependências: [components.md](components.md).

## Referência Saga

Detalhes de eventos: [saga-events.md](saga-events.md). ADR: [ADR-004](adr/ADR-004-saga-choreography-rabbitmq.md).

# RFC-002 — Banco de dados gerenciado: RDS PostgreSQL

- **Status:** Aceito
- **Data:** 2026-09-13

## Contexto

Migrar de Postgres no cluster (StatefulSet) para serviço gerenciado, com backups e Multi-AZ em produção.

## Decisão

**Amazon RDS for PostgreSQL 16**, provisionado por `oficina-infra-db`.

## Motivos

- Compatibilidade total com Alembic/SQLAlchemy existentes.
- ACID para estoque e OS.
- Secrets Manager para credenciais; SG restrito a Lambda + nodes EKS.

## Alternativas

- Aurora PostgreSQL (custo maior; overkill para MVP).
- Cloud SQL / Azure Database (implicaria outra nuvem).

Detalhes do modelo: [../er-modelo.md](../er-modelo.md).

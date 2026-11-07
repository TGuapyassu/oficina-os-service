from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.outbox import OutboxMessage
from app.infrastructure.messaging.rabbit import publish_event
from oficina_contracts.events import DomainEvent

log = logging.getLogger(__name__)


class OutboxWriter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def stage(self, event: DomainEvent) -> None:
        self._session.add(
            OutboxMessage(
                routing_key=event.routing_key,
                payload=event.model_dump_json(),
            )
        )


def flush_outbox(session: Session, amqp_url: str | None, batch: int = 50) -> int:
    if not amqp_url:
        return 0
    rows = (
        session.execute(
            select(OutboxMessage)
            .where(OutboxMessage.published_at.is_(None))
            .order_by(OutboxMessage.id)
            .limit(batch)
        )
        .scalars()
        .all()
    )
    sent = 0
    for row in rows:
        body = json.loads(row.payload)
        if publish_event(amqp_url, row.routing_key, body):
            row.published_at = datetime.now(UTC)
            sent += 1
    if sent:
        session.commit()
    return sent

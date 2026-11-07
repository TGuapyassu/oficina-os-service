from __future__ import annotations

import json
import logging
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.dtos.ordem_dto import OrdemUpdateStatusIn
from app.application.use_cases.ordem_servico import (
    AtualizarStatusOrdem,
    AprovarOrdemServico,
    CompensarReservaPecas,
)
from app.domain.enums import OrdemServicoStatus
from app.infrastructure.database.models.processed_event import ProcessedEvent
from app.infrastructure.mongo.timeline import OsEventTimeline
from app.presentation.composition import build_saga_use_cases
from oficina_contracts.routing import RoutingKey

log = logging.getLogger(__name__)

CONSUMER_NAME = "os-service"


def _mark_processed(session: Session, event_id: str) -> bool:
    exists = session.execute(
        select(ProcessedEvent).where(
            ProcessedEvent.consumer_name == CONSUMER_NAME,
            ProcessedEvent.event_id == event_id,
        )
    ).scalar_one_or_none()
    if exists:
        return False
    session.add(ProcessedEvent(consumer_name=CONSUMER_NAME, event_id=event_id))
    return True


def handle_incoming_event(
    session: Session,
    timeline: OsEventTimeline,
    body: bytes,
) -> None:
    data = json.loads(body)
    event_id = data.get("event_id", "")
    routing_key = data.get("routing_key", "")
    os_id = data.get("os_id")
    if not event_id or not _mark_processed(session, event_id):
        return
    timeline.append(os_id or 0, routing_key, data)
    use_cases = build_saga_use_cases(session)
    patch: AtualizarStatusOrdem = use_cases["patch"]
    aprovar: AprovarOrdemServico = use_cases["aprovar"]
    compensar: CompensarReservaPecas = use_cases["compensar"]
    handlers: dict[str, Callable[[], None]] = {
        RoutingKey.BUDGET_CREATED.value: lambda: _budget_created(patch, os_id),
        RoutingKey.BUDGET_REJECTED.value: lambda: _budget_rejected(patch, os_id),
        RoutingKey.PAYMENT_CONFIRMED.value: lambda: _payment_confirmed(aprovar, os_id, data),
        RoutingKey.PAYMENT_FAILED.value: lambda: None,
        RoutingKey.EXECUTION_STATUS_CHANGED.value: lambda: _exec_status(patch, os_id, data),
        RoutingKey.EXECUTION_COMPLETED.value: lambda: _exec_completed(patch, os_id),
        RoutingKey.BUDGET_CREATION_FAILED.value: lambda: _compensate(compensar, patch, os_id),
    }
    fn = handlers.get(routing_key)
    if fn and os_id:
        fn()
    session.commit()


def _budget_created(patch: AtualizarStatusOrdem, os_id: int | None) -> None:
    if os_id is None:
        return
    patch.execute(os_id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))


def _budget_rejected(patch: AtualizarStatusOrdem, os_id: int | None) -> None:
    if os_id is None:
        return
    patch.execute(
        os_id,
        OrdemUpdateStatusIn(status=OrdemServicoStatus.ORCAMENTO_RECUSADO),
    )


def _payment_confirmed(aprovar: AprovarOrdemServico, os_id: int | None, data: dict) -> None:
    if os_id is None:
        return
    ref = data.get("payload", {}).get("payment_id")
    aprovar.execute(os_id, referencia_externa=ref)


def _exec_status(patch: AtualizarStatusOrdem, os_id: int | None, data: dict) -> None:
    if os_id is None:
        return
    st = data.get("payload", {}).get("status")
    if st:
        patch.execute(os_id, OrdemUpdateStatusIn(status=OrdemServicoStatus(st)))


def _exec_completed(patch: AtualizarStatusOrdem, os_id: int | None) -> None:
    if os_id is None:
        return
    patch.execute(os_id, OrdemUpdateStatusIn(status=OrdemServicoStatus.FINALIZADA))


def _compensate(compensar: CompensarReservaPecas, patch: AtualizarStatusOrdem, os_id: int | None) -> None:
    if os_id is None:
        return
    compensar.execute(os_id)
    patch.execute(os_id, OrdemUpdateStatusIn(status=OrdemServicoStatus.RECEBIDA))

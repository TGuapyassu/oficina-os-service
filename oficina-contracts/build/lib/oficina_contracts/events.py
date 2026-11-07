from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from oficina_contracts.routing import RoutingKey


class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    routing_key: str
    os_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        key: RoutingKey | str,
        *,
        os_id: int | None = None,
        correlation_id: str | None = None,
        **payload: Any,
    ) -> "DomainEvent":
        return cls(
            routing_key=key.value if isinstance(key, RoutingKey) else key,
            os_id=os_id,
            correlation_id=correlation_id or str(uuid4()),
            payload=payload,
        )

"""Contratos compartilhados entre microsserviços da oficina."""

from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import EXCHANGE_EVENTS, RoutingKey

__all__ = ["DomainEvent", "EXCHANGE_EVENTS", "RoutingKey"]

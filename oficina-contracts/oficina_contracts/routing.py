from enum import Enum

EXCHANGE_EVENTS = "oficina.events"


class RoutingKey(str, Enum):
    OS_CREATED = "os.created"
    OS_ITEMS_RESERVED = "os.items_reserved"
    BUDGET_CREATED = "budget.created"
    BUDGET_CREATION_FAILED = "budget.creation_failed"
    BUDGET_APPROVED = "budget.approved"
    BUDGET_REJECTED = "budget.rejected"
    PAYMENT_PENDING = "payment.pending"
    PAYMENT_CONFIRMED = "payment.confirmed"
    PAYMENT_FAILED = "payment.failed"
    EXECUTION_QUEUED = "execution.queued"
    EXECUTION_STATUS_CHANGED = "execution.status_changed"
    EXECUTION_DIAGNOSIS_COMPLETED = "execution.diagnosis_completed"
    EXECUTION_STARTED = "execution.started"
    EXECUTION_COMPLETED = "execution.completed"

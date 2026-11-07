from fastapi import APIRouter, Depends

from app.infrastructure.config import get_settings
from app.infrastructure.database import get_engine
from app.infrastructure.mongo.timeline import OsEventTimeline
from app.infrastructure.observability import snapshot
from app.presentation.dependencies import require_admin

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str | bool]:
    s = get_settings()
    db_ok = False
    try:
        with get_engine().connect() as c:
            from sqlalchemy import text

            c.execute(text("SELECT 1"))
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False
    mongo_ok = OsEventTimeline(s.mongodb_url or None).ping()
    return {
        "status": "ok" if db_ok and mongo_ok else "degraded",
        "database": db_ok,
        "mongodb": mongo_ok,
        "rabbitmq_configured": bool(s.rabbitmq_url),
    }


@router.get("/metrics/snapshot", dependencies=[Depends(require_admin)])
def metrics_snapshot() -> dict:
    """Snapshot local de contadores (complementa dashboards Datadog)."""
    return snapshot()

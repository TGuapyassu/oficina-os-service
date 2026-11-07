from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("oficina.metrics")

# Contadores em memória (agregados pelo Datadog via logs/APM; útil também em demo local)
_os_created_today = 0
_os_status_failures = 0
_integration_errors = 0


def incr_os_created() -> None:
    global _os_created_today
    _os_created_today += 1
    logger.info('{"metric":"os.created","value":1}')


def incr_os_status_failure(*, ordem_id: int, detail: str) -> None:
    global _os_status_failures
    _os_status_failures += 1
    logger.error(
        '{"metric":"os.status_failure","ordem_id":%s,"detail":%s}',
        ordem_id,
        detail.__repr__(),
    )


def incr_integration_error(*, path: str, detail: Optional[str] = None) -> None:
    global _integration_errors
    _integration_errors += 1
    logger.error(
        '{"metric":"integration.error","path":%s,"detail":%s}',
        path.__repr__(),
        (detail or "").__repr__(),
    )


def snapshot() -> dict:
    return {
        "os_created": _os_created_today,
        "os_status_failures": _os_status_failures,
        "integration_errors": _integration_errors,
    }

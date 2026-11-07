from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import get_settings, reset_settings_cache
from app.domain.exceptions import DomainError
from app.infrastructure.database import get_engine, reset_engine_and_session
from app.infrastructure.database.models import Base
from app.infrastructure.observability import RequestContextMiddleware
from app.presentation.httpxx import errmap
from app.infrastructure.messaging.consumer_worker import start_background_workers
from app.presentation.routes import all_routers

log = logging.getLogger(__name__)
_worker_stop: threading.Event | None = None


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    _configure_logging()
    s = get_settings()
    if s.dd_trace_enabled:
        try:
            from ddtrace import patch_all

            patch_all()
            log.info('{"msg":"datadog_trace_enabled","service":"%s"}', s.dd_service)
        except Exception:  # noqa: BLE001
            log.warning('{"msg":"datadog_trace_unavailable"}')
    if not s.is_production:
        get_engine()
        try:
            Base.metadata.create_all(bind=get_engine(), checkfirst=True)
        except Exception:  # noqa: BLE001
            log.debug("create_all: ignorado (ex.: tabelas já existem com migração)")
    global _worker_stop
    _worker_stop = threading.Event()
    start_background_workers(_worker_stop)
    yield
    if _worker_stop:
        _worker_stop.set()
    reset_engine_and_session()
    reset_settings_cache()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Oficina OS Service",
        description="Microsserviço de ordens de serviço, catálogo e projeção de status (Saga coreografia).",
        version="2.0.0",
        lifespan=lifespan,
    )
    s = get_settings()
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.get_cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for r in all_routers:
        app.include_router(r)

    @app.exception_handler(DomainError)
    async def _dom(_: Request, e: Exception) -> JSONResponse:
        assert isinstance(e, DomainError)
        c, m = errmap(e)
        return JSONResponse(status_code=c, content={"detail": m})

    @app.exception_handler(RequestValidationError)
    async def _val(_: Request, e: Exception) -> JSONResponse:
        assert isinstance(e, RequestValidationError)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": e.errors(), "message": "Erro de validação"},
        )

    return app


app = create_app()

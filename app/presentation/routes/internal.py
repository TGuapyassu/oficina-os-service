from fastapi import APIRouter, Depends

from app.application.use_cases.ordem_servico import ObterOsItemsInterno
from app.infrastructure.mongo.timeline import OsEventTimeline
from app.infrastructure.config import get_settings
from app.presentation.composition import get_obter_os_items_interno, require_internal_service_key
from app.presentation.transaction import handle_domain_errors
from oficina_contracts.internal_dto import OsItemsInternal

router = APIRouter(prefix="/internal", tags=["interno"])


def _timeline() -> OsEventTimeline:
    return OsEventTimeline(get_settings().mongodb_url or None)


@router.get(
    "/os/{id}/items",
    response_model=OsItemsInternal,
    dependencies=[Depends(require_internal_service_key)],
)
def obter_itens_os(
    id: int,
    use_case: ObterOsItemsInterno = Depends(get_obter_os_items_interno),
) -> OsItemsInternal:
    return handle_domain_errors(lambda: use_case.execute(id))


@router.get(
    "/os/{id}/historico",
    dependencies=[Depends(require_internal_service_key)],
)
def historico_os(id: int) -> list[dict]:
    return _timeline().list_by_os(id)

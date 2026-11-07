from fastapi import APIRouter, Depends

from app.presentation.dependencies import require_cliente
from app.presentation.deps_schemas import TokenData

router = APIRouter(prefix="/me", tags=["cliente autenticado"])


@router.get("")
def me(token: TokenData = Depends(require_cliente)) -> dict:
    """Perfil do cliente autenticado via JWT da Lambda (CPF)."""
    return {
        "cpf": token.sub,
        "cliente_id": token.cliente_id,
        "typ": token.typ,
    }

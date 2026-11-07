from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.infrastructure.security import verify_token
from app.presentation.deps_schemas import TokenData

bearer = HTTPBearer(auto_error=False)
DbSess = Annotated[Session, Depends(get_session)]


def get_token_payload(
    cred: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer)],
) -> TokenData:
    if not cred or not cred.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente.",
        )
    p = verify_token(cred.credentials)
    if p is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado."
        )
    return TokenData(
        sub=p.sub,
        user_id=p.user_id,
        is_admin=p.is_admin,
        cliente_id=p.cliente_id,
        typ=p.typ,
    )


def require_admin(
    t: Annotated[TokenData, Depends(get_token_payload)],
) -> TokenData:
    if not t.is_admin and t.typ != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requer privilégio de administrador.",
        )
    if not t.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requer privilégio de administrador.",
        )
    return t


def require_cliente(
    t: Annotated[TokenData, Depends(get_token_payload)],
) -> TokenData:
    """JWT emitido pela Lambda de autenticação por CPF."""
    if t.typ != "cliente" or t.cliente_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requer autenticação de cliente (CPF).",
        )
    return t


def require_cliente_or_admin(
    t: Annotated[TokenData, Depends(get_token_payload)],
) -> TokenData:
    if t.is_admin or (t.typ == "cliente" and t.cliente_id is not None):
        return t
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Requer autenticação de cliente ou administrador.",
    )

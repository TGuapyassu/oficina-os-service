from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.infrastructure.config import get_settings


class TokenPayload(BaseModel):
    sub: str
    exp: int
    user_id: Optional[int] = None
    is_admin: bool = False
    cliente_id: Optional[int] = None
    typ: str = "admin"  # admin | cliente


def create_token(user_id: int, email: str, is_admin: bool) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=s.access_token_expire_minutes)
    to_encode: dict[str, Any] = {
        "sub": email,
        "user_id": user_id,
        "is_admin": is_admin,
        "typ": "admin",
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(to_encode, s.jwt_secret, algorithm=s.jwt_algorithm)


def verify_token(token: str) -> Optional[TokenPayload]:
    s = get_settings()
    try:
        p = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
        typ = str(p.get("typ") or ("cliente" if p.get("cliente_id") is not None else "admin"))
        user_id = p.get("user_id")
        cliente_id = p.get("cliente_id")
        return TokenPayload(
            sub=str(p["sub"]),
            user_id=int(user_id) if user_id is not None else None,
            is_admin=bool(p.get("is_admin", False)),
            cliente_id=int(cliente_id) if cliente_id is not None else None,
            typ=typ,
            exp=int(p["exp"]),
        )
    except (JWTError, KeyError, TypeError, ValueError):
        return None

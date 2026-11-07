from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class TokenData:
    sub: str
    user_id: Optional[int]
    is_admin: bool
    cliente_id: Optional[int] = None
    typ: str = "admin"

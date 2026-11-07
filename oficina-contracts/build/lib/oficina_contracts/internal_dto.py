from decimal import Decimal

from pydantic import BaseModel, Field


class OsItemsInternal(BaseModel):
    os_id: int
    cliente_id: int
    veiculo_id: int
    valor_total: Decimal
    servicos: list = Field(default_factory=list)
    pecas: list = Field(default_factory=list)

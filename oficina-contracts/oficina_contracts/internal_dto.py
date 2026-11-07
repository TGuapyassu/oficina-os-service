from decimal import Decimal

from pydantic import BaseModel, Field


class ItemServicoLinha(BaseModel):
    servico_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal


class ItemPecaLinha(BaseModel):
    peca_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal


class OsItemsInternal(BaseModel):
    os_id: int
    cliente_id: int
    veiculo_id: int
    valor_total: Decimal
    servicos: list[ItemServicoLinha] = Field(default_factory=list)
    pecas: list[ItemPecaLinha] = Field(default_factory=list)

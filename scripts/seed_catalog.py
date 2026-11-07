"""
Cadastro mínimo para demo (cliente, veículo, serviço, peça).
Uso: mesmo DATABASE_URL/JWT do serviço; requer pip install -e ".[dev]".
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

os.environ.setdefault("JWT_SECRET", "seed-local")

BASE = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
EMAIL = os.environ.get("ADMIN_EMAIL", "admin@oficina.dev")
SENHA = os.environ.get("ADMIN_SENHA", "admin123")


def _post(path: str, body: dict, token: str | None = None) -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main() -> None:
    login = _post("/auth/login", {"email": EMAIL, "senha": SENHA})
    token = login["access_token"]
    cliente = _post(
        "/clientes",
        {"nome": "Maria Demo", "contato": "maria@exemplo.com", "cpf_cnpj": "52998224725"},
        token,
    )
    veiculo = _post(
        "/veiculos",
        {
            "cliente_id": cliente["id"],
            "placa": "ABC1234",
            "marca": "Fiat",
            "modelo": "Uno",
            "ano": 2015,
        },
        token,
    )
    servico = _post("/servicos", {"nome": "Troca de óleo", "preco": "100.00"}, token)
    peca = _post(
        "/pecas",
        {"nome": "Filtro de óleo", "preco": "25.00", "quantidade_estoque": 10},
        token,
    )
    print(
        json.dumps(
            {
                "cliente_id": cliente["id"],
                "veiculo_id": veiculo["id"],
                "servico_id": servico["id"],
                "peca_id": peca["id"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        sys.exit(1)

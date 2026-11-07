# oficina-contracts (cópia local)

Pacote vendored em **oficina-os-service** para build Docker e desenvolvimento sem depender do GitHub.

O `pip install -e .` nos microsserviços já resolve este pacote via `file:./oficina-contracts` no `pyproject.toml`.

Instalação isolada (opcional):

```bash
pip install -e ./oficina-contracts
```

Billing e execution referenciam `file:../oficina-os-service/oficina-contracts`. O Docker usa o mesmo código via `docker-compose.stack.yml`.

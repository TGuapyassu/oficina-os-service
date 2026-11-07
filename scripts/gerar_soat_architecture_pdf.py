#!/usr/bin/env python3
"""
Gera PDF de entrega SOAT (repositório, desenho da arquitetura e vídeo).
Saída: docs/soat-architecture.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError as e:
    print("Instale fpdf2: pip install fpdf2", file=sys.stderr)
    raise SystemExit(1) from e

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "soat-architecture.pdf"

REPO_URL = "https://github.com/TGuapyassu/pos_arquitetura"
VIDEO_URL = "https://youtu.be/vIpxsSsmQwo"
APP_URL = "https://pos-arquitetura.tguapyassu.com/"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]
FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONT_MONO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def find_fonts() -> tuple[str, str, str]:
    reg, bold, mono = "", "", ""
    for p in FONT_CANDIDATES:
        if Path(p).is_file():
            reg = p
            break
    for p in FONT_BOLD:
        if Path(p).is_file():
            bold = p
            break
    for p in FONT_MONO:
        if Path(p).is_file():
            mono = p
            break
    if reg and not bold:
        bold = reg
    if reg and not mono:
        mono = reg
    return reg, bold, mono


def main() -> None:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    f_reg, f_bold, f_mono = find_fonts()
    if f_reg:
        pdf.add_font("Body", "", f_reg)
        pdf.add_font("Body", "B", f_bold or f_reg)
        family = "Body"
        if f_mono:
            pdf.add_font("Mono", "", f_mono)
            mono = "Mono"
        else:
            mono = family
    else:
        family = "Helvetica"
        mono = "Courier"
        print(
            "Aviso: fonte TrueType não encontrada; acentos podem falhar.",
            file=sys.stderr,
        )

    pdf.add_page()

    def heading(text: str) -> None:
        pdf.set_font(family, "B", 12)
        pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def body(size: int = 10) -> None:
        pdf.set_font(family, "", size)

    def link_line(label: str, url: str) -> None:
        body()
        pdf.set_font(family, "B", 10)
        pdf.write(6, f"{label}: ")
        pdf.set_font(family, "", 10)
        pdf.set_text_color(0, 0, 180)
        pdf.write(6, url, link=url)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)

    pdf.set_font(family, "B", 16)
    pdf.cell(
        0,
        10,
        "SOAT — Arquitetura da solução (Oficina API)",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    heading("Participante")
    body()
    pdf.multi_cell(
        0,
        6,
        "Tiago de Andrade Guapyassu Machado",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    heading("Links da entrega")
    link_line("Repositório GitHub", REPO_URL)
    link_line("Vídeo demonstrativo (até 15 min)", VIDEO_URL)
    link_line("Aplicação em produção", APP_URL)

    heading("Desenho da arquitetura")
    body(9)
    pdf.multi_cell(
        0,
        5,
        "Monólito FastAPI em camadas (DDD / hexagonal) implantado em Kubernetes, "
        "com PostgreSQL interno, migrations via Job, HPA e provisionamento local "
        "via Terraform (kind).",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    diagram = """\
Local / CI
  docker-compose          GitHub Actions (pytest → GHCR → deploy)
         |                              |
Terraform (kind) ──────────────► Cluster Kubernetes
  kind + metrics-server               namespace oficina
                                         ├── StatefulSet postgres + PVC
                                         ├── Job alembic migration
                                         ├── Deployment oficina-api
                                         ├── Service :80
                                         └── HPA (CPU 70% / mem 80%, 2–10)"""

    pdf.set_font(mono, "", 8)
    for line in diagram.splitlines():
        pdf.cell(0, 4.2, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    heading("Recursos escolhidos")
    body(9)
    recursos = [
        ("API", "Python 3.11+, FastAPI, Pydantic v2, JWT"),
        ("Persistência", "PostgreSQL 16, SQLAlchemy 2, Alembic"),
        ("Arquitetura app", "DDD + Clean/Hexagonal (ports & adapters)"),
        ("Container", "Docker multi-stage + docker-compose (dev)"),
        ("Cluster local", "kind (kindest/node:v1.29.2), cluster oficina"),
        ("IaC", "Terraform ≥1.5 (kind-cluster + k8s-platform)"),
        ("Kubernetes", "Namespace, StatefulSet, PVC, Job, Deployment, Service"),
        ("Escalabilidade", "HPA min 2 / max 10 — CPU 70%, memória 80%"),
        ("Métricas", "metrics-server (Helm via Terraform)"),
        ("CI/CD", "GitHub Actions → pytest → GHCR → k8s-deploy.sh"),
        ("Registry", "ghcr.io/<owner>/oficina-api:<sha>"),
    ]
    col1, col2 = 42, 140
    pdf.set_font(family, "B", 9)
    pdf.cell(col1, 6, "Camada", border=1)
    pdf.cell(col2, 6, "Tecnologia / recurso", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(family, "", 8)
    for camada, tech in recursos:
        pdf.cell(col1, 5.5, camada, border=1)
        pdf.cell(col2, 5.5, tech, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    heading("Justificativa dos recursos")
    body(9)
    justificativa = (
        "A aplicação é um monólito em camadas com regras de negócio no domínio e "
        "persistência relacional: o PostgreSQL garante ACID, FKs e schema versionado "
        "com Alembic. Docker e kind permitem reproduzir o ambiente localmente; o "
        "Terraform formaliza o cluster, o Postgres interno e o metrics-server. No "
        "Kubernetes, o Deployment da API, o Job de migrations e o HPA cobrem deploy "
        "idempotente e elasticidade sob carga. O GitHub Actions fecha o ciclo com "
        "testes, publicação da imagem no GHCR e deploy automatizado."
    )
    pdf.multi_cell(0, 5, justificativa, new_x="LMARGIN", new_y="NEXT")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(OUT)
    print(f"PDF gerado: {OUT}")


if __name__ == "__main__":
    main()

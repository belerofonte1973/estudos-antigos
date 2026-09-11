#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migra src/content/docs/ (Starlight) para src/content/biblioteca/ e
src/pages/ (páginas soltas).

Transformações, todas determinísticas e reportadas:
  1. move os dossiês para biblioteca/<area>/<slug>.mdx
  2. frontmatter: sidebar.order -> ordem; injeta area:
  3. import do Starlight -> import dos componentes próprios
  4. :::note[X] ... ::: -> <Aside type="note" title="X"> ... </Aside>
  5. remove o <h1> duplicado (o layout já renderiza o título)
  6. extrai páginas institucionais para src/pages/
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DOCS = RAIZ / "src" / "content" / "docs"
BIB = RAIZ / "src" / "content" / "biblioteca"
PAGES = RAIZ / "src" / "pages"

# origem -> (destino, area, ordem) dentro da biblioteca
MAPA = {
    "biblia/introducao.mdx": ("biblia/introducao.mdx", "biblia", 0),
    "biblia/genesis.mdx": ("biblia/genesis.mdx", "biblia", 1),
    "biblia/exodo.mdx": ("biblia/exodo.mdx", "biblia", 2),
    "biblia/levitico.mdx": ("biblia/levitico.mdx", "biblia", 3),
    "biblia/numeros.mdx": ("biblia/numeros.mdx", "biblia", 4),
    "biblia/deuteronomio.mdx": ("biblia/deuteronomio.mdx", "biblia", 5),
    "biblia/sumeria.mdx": ("biblia/sumeria.mdx", "biblia", 6),
    "classica/introducao.mdx": ("classica/introducao.mdx", "classica", 0),
    "idade-media/introducao.mdx": ("idade-media/introducao.mdx", "idade-media", 0),
    "pre-historia/prehistoria-humana.mdx": (
        "pre-historia/pre-historia-humana.mdx",
        "pre-historia",
        0,
    ),
}

# arquivos que viram página solta (não dossiê)
PAGINAS = {
    "ferramentas/como-pesquisar.mdx": "como-pesquisar.mdx",
}

# descartes: resíduo do template Starlight e a antiga home
DESCARTES = {
    "index.mdx",
    "guides/example.md",
    "reference/example.md",
    "sobre.mdx",
    "sobre/contato.mdx",
    "sobre/contribua.mdx",
}

IMPORT_ANTIGO = re.compile(
    r"^import\s*\{[^}]*\}\s*from\s*'@astrojs/starlight/components';\s*$",
    re.MULTILINE,
)
IMPORT_NOVO = (
    "import Card from '../../components/Card.astro';\n"
    "import CardGrid from '../../components/CardGrid.astro';\n"
    "import Aside from '../../components/Aside.astro';\n"
    "import LinkButton from '../../components/LinkButton.astro';"
)

# :::note[**Título**]  (com ou sem negrito, com ou sem rótulo)
DIRETIVA_ABRE = re.compile(r"^:::([a-z]+)(?:\[(.*?)\])?\s*$")
DIRETIVA_FECHA = re.compile(r"^:::\s*$")

RELATORIO: list[str] = []


def normaliza_titulo(bruto: str | None, tipo: str) -> str:
    if not bruto:
        return {"note": "Nota", "tip": "Dica", "caution": "Atenção", "danger": "Importante"}.get(
            tipo, "Nota"
        )
    # o rótulo vinha com markdown; o componente já estiliza em negrito
    return bruto.replace("**", "").replace("*", "").strip()


def converte_corpo(texto: str, nome: str) -> str:
    """Converte diretivas :::x[] para <Aside> e remove o H1 duplicado."""
    linhas = texto.split("\n")
    saida: list[str] = []
    abertos = 0
    h1_removido = 0

    for linha in linhas:
        m = DIRETIVA_ABRE.match(linha)
        if m:
            tipo, rotulo = m.group(1), m.group(2)
            titulo = normaliza_titulo(rotulo, tipo)
            saida.append(f'<Aside type="{tipo}" title="{titulo}">')
            abertos += 1
            continue

        if DIRETIVA_FECHA.match(linha) and abertos > 0:
            saida.append("</Aside>")
            abertos -= 1
            continue

        # primeiro H1 fora de bloco: o layout já emite o <h1> do frontmatter
        if h1_removido == 0 and re.match(r"^#\s+\S", linha):
            h1_removido += 1
            continue

        saida.append(linha)

    if abertos:
        raise SystemExit(f"ERRO: {nome} tem {abertos} diretiva(s) ::: sem fechamento")

    out = "\n".join(saida)
    # colapsa linhas em branco triplicadas que a remoção do H1 pode criar
    out = re.sub(r"\n{4,}", "\n\n\n", out)
    RELATORIO.append(f"    corpo: {h1_removido} H1 removido, import/troca de diretivas ok")
    return out


def reescreve_frontmatter(fm: str, area: str, ordem: int, nome: str) -> str:
    tem_area = re.search(r"^area:\s", fm, re.MULTILINE)
    tem_ordem = re.search(r"^ordem:\s", fm, re.MULTILINE)

    # remove o bloco aninhado sidebar: + order
    fm = re.sub(r"^sidebar:\s*\n(?:[ \t]+.*\n?)*", "", fm, flags=re.MULTILINE)
    # remove ordem antiga se houver
    fm = re.sub(r"^ordem:\s*.*\n", "", fm, flags=re.MULTILINE)

    adicoes = []
    if not tem_area:
        adicoes.append(f"area: {area}")
    if not tem_ordem:
        adicoes.append(f"ordem: {ordem}")

    if adicoes:
        fm = fm.rstrip("\n") + "\n" + "\n".join(adicoes) + "\n"
        RELATORIO.append(f"    frontmatter: + {' + '.join(adicoes)}")

    return fm


def processa(origem: Path, destino: Path, area: str, ordem: int, imports_rel: str) -> None:
    bruto = origem.read_text(encoding="utf-8")
    bruto = bruto.replace("\r\n", "\n")

    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", bruto, re.DOTALL)
    if not m:
        raise SystemExit(f"ERRO: {origem.name} sem frontmatter válido")

    fm, corpo = m.group(1), m.group(2)
    fm = reescreve_frontmatter(fm, area, ordem, origem.name)
    corpo = converte_corpo(corpo, origem.name)

    if IMPORT_ANTIGO.search(corpo):
        corpo = IMPORT_ANTIGO.sub(imports_rel, corpo, count=1)
    else:
        RELATORIO.append("    AVISO: import do Starlight não encontrado")

    # URLs nuas em <...> quebram o parser MDX
    corpo = re.sub(r"<https?://([^>]+)>", r"[https://\1](https://\1)", corpo)

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f"---\n{fm}---\n{corpo}", encoding="utf-8")


def main() -> int:
    if not DOCS.exists():
        print("Nada a migrar: src/content/docs/ não existe.")
        return 0

    print("== Migração docs/ -> biblioteca/ ==")
    for origem_rel, (destino_rel, area, ordem) in MAPA.items():
        origem = DOCS / origem_rel
        if not origem.exists():
            print(f"  ! ausente: {origem_rel}")
            continue
        print(f"  {origem_rel} -> biblioteca/{destino_rel}")
        RELATORIO.clear()
        processa(
            origem,
            BIB / destino_rel,
            area,
            ordem,
            IMPORT_NOVO.replace("../../components", "../../../components"),
        )
        for linha in RELATORIO:
            print(linha)

    print("\n== Páginas soltas -> src/pages/ ==")
    PAGES.mkdir(parents=True, exist_ok=True)
    for origem_rel, destino_rel in PAGINAS.items():
        origem = DOCS / origem_rel
        if not origem.exists():
            print(f"  ! ausente: {origem_rel}")
            continue
        texto = origem.read_text(encoding="utf-8").replace("\r\n", "\n")
        texto = IMPORT_ANTIGO.sub(
            IMPORT_NOVO.replace("../../components", "../components"), texto, count=1
        )
        texto = re.sub(r"<https?://([^>]+)>", r"[https://\1](https://\1)", texto)
        texto = re.sub(r"^sidebar:\s*\n(?:[ \t]+.*\n?)*", "", texto, flags=re.MULTILINE)
        (PAGES / destino_rel).write_text(texto, encoding="utf-8")
        print(f"  {origem_rel} -> src/pages/{destino_rel}")

    print("\n== Descartes ==")
    for rel in sorted(DESCARTES):
        p = DOCS / rel
        if p.exists():
            print(f"  removido de docs/: {rel}")

    # backup do docs/ original antes de apagar
    backup = RAIZ / "_backup_docs_starlight"
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(DOCS, backup)
    shutil.rmtree(DOCS)
    print(f"\n  backup do antigo docs/ em: {backup.name}/")

    print("\n== Verificação ==")
    arquivos = sorted(BIB.rglob("*.mdx"))
    print(f"  dossiês migrados: {len(arquivos)}")
    problemas = 0
    for f in arquivos:
        t = f.read_text(encoding="utf-8")
        for token, desc in (
            ("starlight", "import do Starlight remanescente"),
            (":::note", "diretiva ::: não convertida"),
            ("sidebar:", "frontmatter sidebar: remanescente"),
        ):
            if token in t:
                print(f"  ! {f.relative_to(BIB)}: {desc}")
                problemas += 1
    if not problemas:
        print("  nenhuma pendência encontrada")

    return 0


if __name__ == "__main__":
    sys.exit(main())

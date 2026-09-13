#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imagens_inserir.py — insere as figuras do manifesto no dossiê (.mdx), cada uma
na seção indicada, e garante o import do componente. Idempotente, com --seco e
--reverter, e backup por arquivo.

Uso:
    python scripts/imagens_inserir.py --slug juizes --seco     # mostra o que faria
    python scripts/imagens_inserir.py --slug juizes            # aplica
    python scripts/imagens_inserir.py --slug juizes --reverter # volta o backup

Regras:
  - a figura entra no FIM da seção indicada (ou no INÍCIO, se posicao="inicio"),
    sempre antes do próximo cabeçalho `##`;
  - a seção é achada pelo NÚMERO do cabeçalho (`## 6.`), que é estável entre as
    duas gerações de dossiê (mudam as palavras, não o número);
  - rodar de novo não duplica: figura cujo src já está no arquivo é ignorada;
  - o import do componente é acrescentado ao bloco de imports existente, sem
    quebrar a linha em branco que o MDX exige depois deles.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONTENT = RAIZ / "src" / "content" / "biblioteca" / "biblia"
META = RAIZ / "_imagens"
IMPORT_FIGURA = "import Figura from '../../../components/Figura.astro';"


def aspas(texto: str) -> str:
    """Texto seguro dentro de atributo JSX com aspas duplas."""
    t = re.sub(r"\s+", " ", (texto or "").replace("\n", " ")).strip()
    return t.replace('"', "“", 1).replace('"', "”") if t.count('"') == 1 else t.replace('"', "”")


def bloco(fig: dict) -> str:
    linhas = [
        "<Figura",
        f'\tsrc="{fig["src"]}"',
        f'\talt="{aspas(fig.get("alt") or fig["titulo"])}"',
        f'\ttitulo="{aspas(fig["titulo"])}"',
        f'\tlegenda="{aspas(fig.get("legenda", ""))}"',
    ]
    if fig.get("passagem"):
        linhas.append(f'\tpassagem="{aspas(fig["passagem"])}"')
    for chave, rotulo in (("artista", "artista"), ("data", "data"),
                          ("tecnica", "tecnica"), ("acervo", "acervo")):
        if fig.get(chave):
            linhas.append(f'\t{rotulo}="{aspas(fig[chave])}"')
    linhas.append(f'\tfonte="{fig["fonte"]}"')
    if fig.get("fonte_rotulo") and fig["fonte_rotulo"] != "Wikimedia Commons":
        linhas.append(f'\tfonteRotulo="{aspas(fig["fonte_rotulo"])}"')
    linhas.append(f'\tlicenca="{aspas(fig["licenca"])}"')
    linhas.append("/>")
    return "\n".join(linhas)


def secoes(texto: str) -> list[tuple[int, int, str]]:
    """[(numero, indice_da_linha, linha)] para cada cabeçalho `## N. ...`."""
    achadas = []
    for i, linha in enumerate(texto.split("\n")):
        m = re.match(r"^##\s+(\d+)\.\s", linha)
        if m:
            achadas.append((int(m.group(1)), i, linha))
    return achadas


def inserir(texto: str, figs: list[dict]) -> tuple[str, list[str]]:
    linhas = texto.split("\n")
    relatos = []

    # import do componente
    if IMPORT_FIGURA not in texto:
        fim_imports = 0
        for i, linha in enumerate(linhas):
            if linha.startswith("import "):
                fim_imports = i + 1
            elif fim_imports and linha.strip() and not linha.startswith("import "):
                break
        if not fim_imports:
            return texto, ["SEM bloco de imports: nada foi inserido (rode o validador)"]
        linhas.insert(fim_imports, IMPORT_FIGURA)
        relatos.append(f"import acrescentado na linha {fim_imports + 1}")

    # figuras, da última seção para a primeira (para não deslocar índices)
    for fig in sorted(figs, key=lambda f: -int(f.get("secao") or 0)):
        if fig["src"] in "\n".join(linhas):
            relatos.append(f"já presente (ignorada): {fig['src']}")
            continue
        cabecalhos = secoes("\n".join(linhas))
        alvo = next((c for c in cabecalhos if c[0] == int(fig.get("secao") or 0)), None)
        if not alvo:
            relatos.append(f"SEÇÃO {fig.get('secao')} não encontrada — figura não inserida: {fig['src']}")
            continue
        _, i_cab, linha_cab = alvo
        if fig.get("posicao") == "inicio":
            destino = i_cab + 1
            while destino < len(linhas) and linhas[destino].strip() == "":
                destino += 1
            bloco_linhas = ["", bloco(fig), ""]
        else:
            seguintes = [c[1] for c in cabecalhos if c[1] > i_cab]
            destino = seguintes[0] if seguintes else len(linhas)
            while destino > i_cab and linhas[destino - 1].strip() == "":
                destino -= 1
            bloco_linhas = ["", bloco(fig), ""]
        linhas[destino:destino] = bloco_linhas
        relatos.append(f"seção {fig['secao']} ({linha_cab[:34].strip()}): + {fig['src']}")

    return "\n".join(linhas), relatos


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--reverter", action="store_true")
    args = ap.parse_args()

    mdx = CONTENT / f"{args.slug}.mdx"
    bak = mdx.with_suffix(".mdx.bak")
    if not mdx.exists():
        sys.exit(f"dossiê não existe: {mdx}")

    if args.reverter:
        if not bak.exists():
            sys.exit(f"sem backup para reverter: {bak}")
        bak.replace(mdx)
        print(f"revertido de {bak.name} para {mdx.name}")
        return

    manifesto = META / f"{args.slug}.json"
    if not manifesto.exists():
        sys.exit(f"manifesto não existe: {manifesto} (rode imagens_baixar.py antes)")
    figs = json.loads(manifesto.read_text(encoding="utf-8"))["figuras"]
    figs = [f for f in figs if f.get("titulo")]

    texto = mdx.read_text(encoding="utf-8")
    novo, relatos = inserir(texto, figs)

    print(f"dossiê: {args.slug} · {len(figs)} figura(s) no manifesto")
    for r in relatos:
        print("  ", r)
    if novo == texto:
        print("\nnada a fazer (arquivo idêntico)")
        return
    if args.seco:
        print("\n(--seco: arquivo não foi alterado)")
        return
    if not bak.exists():
        bak.write_text(texto, encoding="utf-8")
        print(f"\nbackup: {bak.name}")
    mdx.write_text(novo, encoding="utf-8")
    antes, depois = len(texto.split()), len(novo.split())
    print(f"gravado: {mdx}")
    print(f"palavras: {antes} → {depois} (+{depois - antes})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Confere a imagem social do build — o par que impede a imagem sumir calada.

O caminho da imagem é montado em dois lugares que não se conhecem: os layouts
(`BibliotecaLayout` monta `/og/<area>-<slug>.png` a partir do id; `ArtigoLayout`,
`/og/revista-<slug>.png`) e o gerador `scripts/gerar_og.mjs`, que escreve os
arquivos a partir do frontmatter. Renomear um dossiê, mudar o gerador ou
esquecer de rodá-lo não quebra o build — quebra o cartão social, que ninguém vê
em teste local. Este portão fecha esse buraco:

1. todo `<meta property="og:image">` do build aponta para um arquivo que EXISTE
   em `dist/` (e não é o fallback quando a página tem imagem própria);
2. toda imagem de `public/og/` está no formato 1200x630 (lido do IHDR do PNG,
   sem dependência);
3. nenhuma imagem órfã — arquivo gerado para documento que não existe mais.

Uso:
    python scripts/conferir_og.py            # exit 1 em qualquer falha
    python scripts/conferir_og.py --verboso
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIST = RAIZ / "dist"
PUBLIC_OG = RAIZ / "public" / "og"
CONTEUDO = RAIZ / "src" / "content"

OG_RE = re.compile(r'<meta\s+property="og:image"\s+content="([^"]+)"')


def dimensoes_png(caminho: Path) -> tuple[int, int] | None:
    """Lê largura/altura do IHDR (bytes 16..24) sem PIL."""
    with caminho.open("rb") as f:
        cabeca = f.read(24)
    if len(cabeca) < 24 or cabeca[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", cabeca[16:24])


def esperadas() -> set[str]:
    """Nomes de arquivo que o gerador deveria ter produzido."""
    nomes = set()
    for p in CONTEUDO.glob("biblioteca/**/*.mdx"):
        rel = p.relative_to(CONTEUDO / "biblioteca").with_suffix("")
        nomes.add(f"{str(rel).replace(chr(92), '-').replace('/', '-')}.png")
    for p in CONTEUDO.glob("artigos/*.md"):
        nomes.add(f"revista-{p.stem}.png")
    return nomes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verboso", action="store_true")
    args = ap.parse_args()

    if not DIST.exists():
        print("dist/ não existe — rode o build antes.")
        return 1

    falhas: list[str] = []
    avisos: list[str] = []

    # 1. cada página do build: a imagem declarada existe?
    paginas = list(DIST.rglob("*.html"))
    usam_fallback = 0
    for pagina in paginas:
        html = pagina.read_text(encoding="utf-8", errors="replace")
        m = OG_RE.search(html)
        if not m:
            # Páginas utilitárias (`_tema_claro.html`) e o 404 não têm cartão
            # social por construção — não são conteúdo.
            if pagina.name != "404.html" and not pagina.name.startswith("_"):
                avisos.append(f"{pagina.relative_to(DIST)}: sem og:image")
            continue
        url = m.group(1)
        caminho = url.split("://", 1)[-1]
        caminho = caminho.split("/", 1)[1] if "://" in url and "/" in caminho else caminho
        local = DIST / caminho.lstrip("/")
        if url.endswith("/og-default.png"):
            usam_fallback += 1
        if not local.exists():
            falhas.append(f"{pagina.relative_to(DIST)}: og:image aponta para {url} — arquivo não está no build")
        elif args.verboso:
            print(f"  ok  {pagina.relative_to(DIST)} → {url}")

    # 2. dimensões de toda imagem gerada
    geradas = sorted(PUBLIC_OG.glob("*.png")) if PUBLIC_OG.exists() else []
    for img in geradas:
        dim = dimensoes_png(img)
        if dim != (1200, 630):
            falhas.append(f"{img.name}: dimensões {dim} (esperado 1200x630)")

    # 3. órfãs
    esperado = esperadas()
    presentes = {img.name for img in geradas}
    orfas = sorted(presentes - esperado)
    faltando = sorted(esperado - presentes)
    if orfas:
        falhas.append(f"imagens órfãs (documento não existe mais): {orfas}")
    if faltando:
        falhas.append(f"imagens faltando para documentos existentes: {faltando}")

    print("=" * 72)
    if args.verboso:
        pass
    print(
        f"{len(paginas)} páginas · {len(geradas)} imagens em public/og/ "
        f"· {usam_fallback} páginas no fallback og-default.png"
    )
    for a in avisos[:5]:
        print("  ·", a)
    if falhas:
        print("FALHAS:")
        for f in falhas:
            print("  ✗", f)
        return 1
    print(f"OK — toda og:image do build existe; {len(geradas)} imagens em 1200x630; nenhuma órfã.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

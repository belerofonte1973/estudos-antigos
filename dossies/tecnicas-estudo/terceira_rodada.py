#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""terceira_rodada.py — fecha as figuras 3 e 4 do dossiê Técnicas de Estudo.

As figuras 1, 2 e 5 ja tem candidato verificado; estas duas ficaram sem. Poucas
chamadas de API de proposito (o Commons limita por IP e a rajada anterior
estourou 429).

    python dossies/tecnicas-estudo/terceira_rodada.py
"""
from __future__ import annotations

import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import buscar_arquivos, fichas  # noqa: E402

BUSCAS = [
    ("fig3 palacio da memoria", "memory palace method of loci"),
    ("fig3 teatro da memoria", "theatre of memory mnemonics"),
    ("fig4 ciclo do aprendizado", "information processing model memory diagram"),
    ("fig4 consolidacao", "memory consolidation diagram"),
]


def limpa(t: str, n: int = 260) -> str:
    return " ".join((t or "").split())[:n]


def main() -> None:
    titulos: list[str] = []
    for rotulo, termo in BUSCAS:
        print(f"\n== {rotulo}: {termo}")
        for c in buscar_arquivos(termo, limite=10):
            if c not in titulos:
                titulos.append(c)
                print(f"   {c}")

    print("\n\n########## FICHAS ##########")
    for f in fichas(titulos):
        print(f"\n## {f['arquivo']}")
        print(f"   {f['licenca']} [{f['grupo']}]  {f['largura_original']}x{f['altura_original']}"
              f"  {f['kb_original']} KB  {f['mime']}")
        print(f"   artista: {f['artista'][:80]}")
        print(f"   data   : {f['data'][:50]}")
        print(f"   desc   : {limpa(f['descricao_fonte'])}")


if __name__ == "__main__":
    main()

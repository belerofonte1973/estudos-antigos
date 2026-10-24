#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""quarta_rodada.py — ultima busca pela figura 4 (ciclo do aprendizado).

Termos mais cirurgicos: a figura do dossiê descreve atencao -> codificacao ->
consolidacao -> recuperacao, com o sono no centro da consolidacao.

    python dossies/tecnicas-estudo/quarta_rodada.py
"""
from __future__ import annotations

import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import buscar_arquivos, fichas  # noqa: E402

BUSCAS = [
    "encoding consolidation retrieval memory",
    "sleep memory consolidation",
    "forgetting curve Ebbinghaus",
]


def limpa(t: str, n: int = 240) -> str:
    return " ".join((t or "").split())[:n]


def main() -> None:
    titulos: list[str] = []
    for termo in BUSCAS:
        print(f"\n== {termo}")
        for c in buscar_arquivos(termo, limite=12):
            if c not in titulos:
                titulos.append(c)
                print(f"   {c}")

    print("\n\n########## FICHAS ##########")
    for f in fichas(titulos):
        if (f["mime"] or "") not in ("image/jpeg", "image/png"):
            continue
        print(f"\n## {f['arquivo']}")
        print(f"   {f['licenca']} [{f['grupo']}]  {f['largura_original']}x{f['altura_original']}"
              f"  {f['kb_original']} KB  {f['mime']}")
        print(f"   artista: {f['artista'][:80]}")
        print(f"   data   : {f['data'][:50]}")
        print(f"   desc   : {limpa(f['descricao_fonte'])}")


if __name__ == "__main__":
    main()

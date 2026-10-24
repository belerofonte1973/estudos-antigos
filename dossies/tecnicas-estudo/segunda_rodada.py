#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""segunda_rodada.py — desempata as figuras 1, 3 e 4 do dossiê Técnicas de Estudo.

A primeira rodada achou os candidatos; esta lê a `descricao_fonte` (ImageDescription)
de cada um — e e o que diz se a imagem e o "edificio com camaras" do teatro da
memoria, o "palacio da memoria" ou o "ciclo do aprendizado" — e busca termos
melhores para as figuras que ainda nao têm candidato a altura.

    python dossies/tecnicas-estudo/segunda_rodada.py
"""
from __future__ import annotations

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import buscar_arquivos, ficha, fichas  # noqa: E402

AQUI = pathlib.Path(__file__).resolve().parent

# Candidatos curtos da primeira rodada, para ler a descricao.
CANDIDATOS = [
    # fig 1 — teatro da memoria
    "File:Ars Memoriæ.jpg",
    "File:Oculus imaginationis inTractatus 1 Section 2 Portion 3 Robert Fludd’s Ars Memoriae Fludd, 1617.jpg",
    "File:Fotothek df tg 0006516 Theosophie ^ Philosophie ^ Judentum ^ Kabbala ^ Mnemotechnik ^ Theater.jpg",
    "File:Fotothek df tg 0006515 Theosophie ^ Philosophie ^ Judentum ^ Kabbala ^ Mnemotechnik ^ Theater ^ Bühne.jpg",
    "File:Fotothek df tg 0006513 Theosophie ^ Philosophie ^ Judentum ^ Kabbala ^ Mnemotechnik.jpg",
    "File:Fotothek df tg 0006514 Theosophie ^ Philosophie ^ Judentum ^ Kabbala ^ Mnemotechnik ^ Astronomie ^ Zodi.jpg",
    # fig 3 — palacio da memoria
    "File:Fotothek df tg 0006542 Theosophie ^ Philosophie ^ Judentum ^ Kabbala.jpg",
    "File:Fotothek df tg 0006531 Theologie ^ Philosophie.jpg",
    "File:Fotothek df tg 0006537 Theosophie ^ Philosophie ^ Judentum ^ Kabbala.jpg",
    "File:Fotothek df tg 0006541 Theosophie ^ Philosophie ^ Judentum ^ Kabbala.jpg",
    "File:Fotothek df tg 0006533 Theosophie ^ Philosophie ^ Judentum ^ Kabbala.jpg",
    "File:Fotothek df tg 0006538 Theosophie ^ Philosophie ^ Judentum ^ Kabbala.jpg",
    "File:Fotothek df tg 0006540 Theosophie ^ Philosophie ^ Judentum ^ Kabbala.jpg",
    # fig 2
    "File:Brain regions in memory formation updated.jpg",
    "File:Brain regions involved in memory formation.jpg",
]

# Termos melhores para a figura 4 (ciclo do aprendizado / consolidacao).
BUSCAS_FIG4 = [
    "memory consolidation",
    "sleep memory consolidation diagram",
    "engram memory",
    "learning cycle education diagram",
]


def limpa(t: str, n: int = 400) -> str:
    return " ".join((t or "").split())[:n]


def main() -> None:
    print("########## DESCRICOES DOS CANDATOS ##########")
    for f in fichas(CANDIDATOS):
        print(f"\n## {f['arquivo']}")
        print(f"   {f['licenca']} [{f['grupo']}]  {f['largura_original']}x{f['altura_original']}"
              f"  {f['kb_original']} KB")
        print(f"   artista: {f['artista'][:90]}")
        print(f"   data   : {f['data'][:60]}")
        print(f"   acervo : {f['acervo'][:110]}")
        print(f"   desc   : {limpa(f['descricao_fonte'])}")

    print("\n\n########## BUSCAS PARA A FIG. 4 ##########")
    vistos: set[str] = set()
    for termo in BUSCAS_FIG4:
        print(f"\n== {termo}")
        for c in buscar_arquivos(termo, limite=10):
            if c in vistos:
                continue
            vistos.add(c)
            f = ficha(c)
            if not f:
                continue
            print(f"   {c}")
            print(f"      {f['licenca']} [{f['grupo']}]  {f['largura_original']}x{f['altura_original']}"
                  f"  {f['kb_original']} KB  {f['mime']}")
            print(f"      desc: {limpa(f['descricao_fonte'], 220)}")

    (AQUI / "_bruto_candidatos_fig4.json").write_text(
        json.dumps(sorted(vistos), ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

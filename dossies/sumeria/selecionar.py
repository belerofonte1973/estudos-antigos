#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""selecionar.py — resolve os títulos exatos no Commons e imprime a ficha de
origem de cada figura escolhida (para a legenda ser escrita a partir da fonte,
nunca de memória). Não baixa nada.
"""
from __future__ import annotations

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
AQUI = pathlib.Path(__file__).resolve().parent

# escolha por trecho único do título — o título exato vem do JSON da busca,
# que veio da API; nada de título digitado de cabeça.
ESCOLHA = [
    ("Sumer satellite map", 1),
    ("Ziggurat of Ur Site in Nasiriyah 02", 1),
    ("Sumer Akkad.png", 2),
    ("Sumerian King List, 1800 BC, Larsa, Iraq.jpg", 3),
    ("Ancient Uruk, Iraq (ASTER)", 3),
    ("Diorite Victory Stele of Sargon", 3),
    ("Stele of Ur-Nammu (front and back)", 3),
    ("Ziggurat at Eridu (30809118442)", 4),
    ("plan of Nippur (Hilprecht", 4),
    ("Stele of the Vultures in the Louvre Museum", 4),
    ("proto-cuneiform signs, food issue list", 5),
    ("administrative account concerning the distribution of barley and emmer MET", 5),
    ("58 different terms for pig", 5),
    ("School tablet - Sumerian cuneiform - Susa - 2nd mil BC - National Museum of Iran - Inventory number - 1885.jpg", 5),
    ("Warka Vase, Iraq Museum", 6),
    ("Warka Mask, Iraq Museum", 6),
    ("Square Temple of Abu, Shrine II, Early Dynastic period, 2700-2600 BC, gypsum, shell, bitumen", 6),
    ("Bronze foundation figurine of Ur-Nammu from the Temple of Inanna at Uruk", 6),
    ("Man carrying a box, possibly for offerings", 7),
    ("Inlaid Gold Ring from Archaic Period of Sumer", 7),
    ("Gameboard recovered from the royal cemetery of Ur", 7),
    ("Head of a Sumerian woman, from Khafajah", 7),
    ("Cylinder seal MET 159183", 7),
    ("Gudea, City Ruler of Lagash, Sumer - Ny Carlsberg Glyptotek", 8),
    ("Disk of Enheduanna.JPG", 8),
    ("CBS7847 Ninmeshara Penn Museum", 8),
    ("Birth Sargon of Akkad Louvre AO7673", 8),
    ("Sumerian king Eannatum of Lagash from the stele of the vultures", 8),
    ("Tablet XI or the Flood Tablet of the Epic of Gilgamesh", 9),
    ("Epic of Gilgamesh, from Hattusa, Turkey. 13th century BCE. Neues Museum", 9),
    ("Bull Headed Lyre of Ur", 10),
    ("Queen's Lyre Ur Royal Cemetery", 10),
    ("Silver lyre, PG 1237", 10),
    ("Ram in a thicket - British", 10),
    ("Standard of Ur - Peace.jpg", 11),
    ("Standard of Ur - War.jpg", 11),
    ("Relief Ninsun Louvre AO2761", 11),
]


def main() -> None:
    banco: list[dict] = []
    for nome in ("_bruto_candidatos.json", "_bruto_candidatos2.json"):
        p = AQUI / nome
        if p.exists():
            for itens in json.loads(p.read_text(encoding="utf-8")).values():
                banco += itens

    resolvido, faltando = [], []
    for trecho, secao in ESCOLHA:
        cands = [c for c in banco if trecho.lower() in c["arquivo"].lower()]
        if not cands:
            faltando.append(trecho)
            continue
        c = sorted(cands, key=lambda x: (x["grupo"] != "LIVRE", -x["largura"]))[0]
        resolvido.append((secao, c))

    for secao, c in resolvido:
        print(f"S{secao} [{c['grupo'][:4]}] {c['arquivo']}")
        print(f"     licença: {c['licenca']}  |  autor: {c['artista']}  |  data: {c['data']}")
        print(f"     acervo:  {c['acervo']}")
        print(f"     {c['largura']}x{c['altura']}  |  {c['pagina']}")
        print(f"     fonte diz: {c['descricao'][:320]}")
        print()
    print(f"resolvidas: {len(resolvido)}; sem correspondência: {faltando}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pesquisar_prehistoria.py — levantamento de candidatos a figura para o
dossiê Pré-História da Humanidade (site). Usa scripts/commons_api.py."""
from __future__ import annotations

import json
import pathlib
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import commons_api  # noqa: E402
commons_api.MIN_INTERVALO = 1.6
from commons_api import buscar_arquivos, fichas  # noqa: E402

CONSULTAS = [
    ("termo", "human evolution diagram"), ("termo", "hominin family tree"),
    ("termo", "Jebel Irhoud"), ("termo", "Neanderthal reconstruction"),
    ("termo", "Denisovan skull"), ("termo", "Australopithecus"),
    ("termo", "Oldowan tools"), ("termo", "Acheulean hand axe"),
    ("termo", "Mousterian tools"), ("termo", "Venus figurine Paleolithic"),
    ("termo", "Lascaux cave painting"), ("termo", "Chauvet cave"),
    ("termo", "Altamira cave bison"), ("termo", "Cueva de las Manos"),
    ("termo", "prehistoric human migration map"), ("termo", "Out of Africa"),
    ("termo", "Neolithic Revolution"), ("termo", "Jericho tower"),
    ("termo", "Catalhoyuk"), ("termo", "Gobekli Tepe"),
    ("termo", "Stonehenge"), ("termo", "Carnac stones"),
    ("termo", "Newgrange"), ("termo", "megalithic tomb"),
    ("termo", "prehistoric woman"), ("termo", "hunter gatherer"),
    ("termo", "Laetoli footprints"), ("termo", "Turkana Boy"),
    ("termo", "Lucy Australopithecus"), ("termo", "Cro-Magnon"),
    ("termo", "Homo erectus"), ("termo", "Homo heidelbergensis"),
    ("termo", "Archaic human"), ("termo", "Paleolithic art"),
    ("termo", "Mesolithic"), ("termo", "Epipaleolithic"),
    ("termo", "Natufian"), ("termo", "Jomon pottery"),
    ("termo", "Bandelier"), ("termo", "Clovis point"),
    ("termo", "prehistoric map"), ("termo", "cave bear"),
    ("termo", "cave lion"), ("termo", "mammoth ivory"),
    ("termo", "Venus of Willendorf"), ("termo", "Venus of Dolni Vestonice"),
    ("termo", "Red Lady of Paviland"), ("termo", "Lion Man"),
    ("termo", "prehistoric skull"), ("termo", "prehistoric bone"),
    ("termo", "ancient DNA"), ("termo", "genome"),
    ("categoria", "Category:Human evolution"),
    ("categoria", "Category:Prehistoric art"),
    ("categoria", "Category:Neanderthal"),
    ("categoria", "Category:Acheulean"),
    ("categoria", "Category:Paleolithic"),
    ("categoria", "Category:Neolithic"),
    ("categoria", "Category:Megalithic monuments"),
    ("categoria", "Category:Cave paintings"),
    ("categoria", "Category:Prehistoric Africa"),
    ("categoria", "Category:Prehistory of Europe"),
    ("categoria", "Category:Prehistoric Asia"),
    ("categoria", "Category:Stone Age"),
]

for tipo, valor in CONSULTAS:
    try:
        t = (buscar_arquivos(termo=valor, limite=14) if tipo == "termo"
             else buscar_arquivos(categoria=valor, limite=14))
        fs = fichas(t) if t else []
    except Exception as e:  # noqa: BLE001
        print(f"!! {valor}: {e}", file=sys.stderr)
        continue
    bons = [f for f in fs if f["grupo"] != "NAO-USAR"
            and f["mime"] in ("image/jpeg", "image/png")
            and (f["largura_original"] or 0) >= 800]
    print(f"### {valor} — {len(bons)}")
    for f in bons[:6]:
        print("   [%s] %sx%s %-18s %-22s %s" % (
            f["grupo"][:4], f["largura_original"], f["altura_original"],
            (f["licenca"] or "")[:18], (f["artista"] or "")[:22], f["arquivo"][5:]))
    time.sleep(0.3)

print(f"\n==> {len(CONSULTAS)} consultas feitas")

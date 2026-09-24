#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""rodada2.py — segunda rodada de busca (lacunas do dossiê). Grava JSON."""
from __future__ import annotations

import json
import pathlib
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import commons_api  # noqa: E402
commons_api.MIN_INTERVALO = 2.6          # a API está limitando; ir mais devagar
from commons_api import buscar_arquivos, fichas  # noqa: E402

CONSULTAS = [
    ("termo", "Sumer map"), ("termo", "Map of Sumer"), ("termo", "Sumer city map"),
    ("termo", "Weld-Blundell prism"), ("termo", "Sumerian king list tablet"),
    ("termo", "Ur-Nammu laws tablet"), ("termo", "Code of Ur-Nammu"),
    ("termo", "Eridu ziggurat"), ("termo", "Ur excavation Woolley"),
    ("termo", "seeder plough Sumerian"), ("termo", "Sumerian boat model"),
    ("termo", "Mesopotamian potter's wheel"), ("termo", "Gudea stele music"),
    ("termo", "Shulgi"), ("termo", "Sumerian terracotta plaque"),
    ("termo", "ziggurat reconstruction"), ("termo", "Uruk cylinder seal"),
    ("termo", "Sumerian woman statue"), ("termo", "Sumerian brick inscription"),
    ("termo", "Sumerian lyre musician"), ("termo", "Isin-Larsa"),
    ("termo", "Ur standard war panel"), ("termo", "Uruk Trough"),
    ("categoria", "Category:Sumerian language"), ("categoria", "Category:Cuneiform"),
    ("categoria", "Category:Warka Vase"), ("categoria", "Category:Ur-Nammu"),
    ("categoria", "Category:Enheduanna"), ("categoria", "Category:Uruk Vase"),
    ("categoria", "Category:Maps of Sumer"), ("categoria", "Category:Nippur"),
    ("categoria", "Category:Eridu"), ("categoria", "Category:Gilgamesh"),
    ("categoria", "Category:Mesopotamian seals"),
]

saida = {}
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
    saida[f"{tipo}:{valor}"] = [
        {"arquivo": f["arquivo"], "grupo": f["grupo"], "licenca": f["licenca"],
         "artista": f["artista"], "data": f["data"], "acervo": f["acervo"],
         "pagina": f["pagina"], "largura": f["largura_original"],
         "altura": f["altura_original"], "descricao": f["descricao_fonte"][:300]}
        for f in bons]
    print(f"### {valor} — {len(bons)}")
    for f in bons[:5]:
        print("   [%s] %sx%s %-18s %-20s %s" % (
            f["grupo"][:4], f["largura_original"], f["altura_original"],
            (f["licenca"] or "")[:18], (f["artista"] or "")[:20], f["arquivo"][5:]))
    time.sleep(0.4)

pathlib.Path(RAIZ / "dossies/sumeria/_bruto_candidatos2.json").write_text(
    json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n==> {len(saida)} consultas salvas")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pesquisar_figuras.py — levantamento de candidatos a figura para o dossiê da
Suméria (4 formatos). Usa o commons_api.py do acervo (throttle + cache +
classificação de licença): nada entra por memória, tudo é reconferido na API.

    python dossies/sumeria/pesquisar_figuras.py            # relatório na tela
    python dossies/sumeria/pesquisar_figuras.py --json bruto.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import fichas, buscar_arquivos  # noqa: E402

CONSULTAS = [
    ("termo", "Sumer"),
    ("termo", "Sumerian"),
    ("termo", "Sumeria"),
    ("termo", "Uruk"),
    ("termo", "Warka Vase"),
    ("termo", "Mask of Warka"),
    ("termo", "Ziggurat of Ur"),
    ("termo", "Standard of Ur"),
    ("termo", "Royal Cemetery of Ur"),
    ("termo", "Ram in a Thicket"),
    ("termo", "Puabi"),
    ("termo", "Lyres of Ur"),
    ("termo", "Gudea"),
    ("termo", "Stele of the Vultures"),
    ("termo", "Ur-Nammu"),
    ("termo", "Enheduanna"),
    ("termo", "Sumerian King List"),
    ("termo", "proto-cuneiform tablet Uruk"),
    ("termo", "cuneiform tablet Sumerian"),
    ("termo", "Sumerian votive statue"),
    ("termo", "Tell Asmar statues"),
    ("termo", "Eshnunna"),
    ("termo", "Eridu"),
    ("termo", "Nippur tablet"),
    ("termo", "cylinder seal Sumerian"),
    ("termo", "Sargon of Akkad"),
    ("termo", "Naram-Sin"),
    ("termo", "Code of Ur-Nammu"),
    ("termo", "Lagash"),
    ("termo", "Eannatum"),
    ("termo", "Sumerian relief"),
    ("termo", "Mesopotamia map ancient"),
    ("termo", "Gilgamesh tablet"),
    ("termo", "Sumerian plaque"),
    ("termo", "Ishtar gate Babylon"),  # descartar: babilônico, só p/ contraste
    ("termo", "Sumerian harp music"),
    ("categoria", "Category:Sumer"),
    ("categoria", "Category:Sumerian art"),
    ("categoria", "Category:Sumerian cuneiform"),
    ("categoria", "Category:Uruk"),
    ("categoria", "Category:Ur"),
    ("categoria", "Category:Gudea"),
    ("categoria", "Category:Standard of Ur"),
    ("categoria", "Category:Ziggurat of Ur"),
    ("categoria", "Category:Royal Cemetery at Ur"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--todos", action="store_true")
    args = ap.parse_args()

    tudo = {}
    for tipo, valor in CONSULTAS:
        try:
            if tipo == "termo":
                titulos = buscar_arquivos(termo=valor, limite=14)
            else:
                titulos = buscar_arquivos(categoria=valor, limite=14)
        except Exception as e:  # noqa: BLE001
            print(f"!! {tipo} {valor}: {e}", file=sys.stderr)
            continue
        if not titulos:
            print(f"\n### {tipo}: {valor}  (nada)")
            continue
        fs = fichas(titulos)
        bons = [f for f in fs
                if f["grupo"] != "NAO-USAR"
                and f["mime"] in ("image/jpeg", "image/png")
                and (f["largura_original"] or 0) >= 800]
        print(f"\n### {tipo}: {valor}  — {len(bons)}/{len(fs)} utilizáveis")
        for f in bons[:8]:
            print(f"  [{f['grupo'][:4]}] {f['largura_original']}x{f['altura_original']}"
                  f" | {f['licenca'][:22]:22} | {(f['artista'] or '')[:28]:28}"
                  f" | {f['arquivo']}")
        tudo[f"{tipo}:{valor}"] = [
            {"arquivo": f["arquivo"], "grupo": f["grupo"], "licenca": f["licenca"],
             "artista": f["artista"], "data": f["data"], "acervo": f["acervo"],
             "pagina": f["pagina"], "largura": f["largura_original"],
             "altura": f["altura_original"], "descricao": f["descricao_fonte"][:400]}
            for f in (fs if args.todos else bons)
        ]

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(tudo, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n==> {args.json} ({len(tudo)} consultas)")


if __name__ == "__main__":
    main()

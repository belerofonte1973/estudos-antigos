#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imagens_buscar.py — busca imagens no Wikimedia Commons COM os metadados de
licença já prontos para decidir. Primeiro passo de qualquer dossiê que recebe
figuras. Usa scripts/commons_api.py (throttle + cache + backoff).

Uso:
    python scripts/imagens_buscar.py "Samson and Delilah"
    python scripts/imagens_buscar.py --categoria "Category:Samson"
    python scripts/imagens_buscar.py "Baal Ugarit" --limite 10 --largura-min 1200
    python scripts/imagens_buscar.py "Merneptah stele" --json _imagens/cand_merneptah.json

Classificação de licença do acervo:
    LIVRE       domínio público / PDM / CC0      — usar sem obrigação
    ATRIBUICAO  CC BY / CC BY-SA                 — usar citando autor e licença
    NAO-USAR    qualquer outra                   — não entra no acervo
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from commons_api import buscar_arquivos, fichas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("termo", nargs="?")
    ap.add_argument("--categoria")
    ap.add_argument("--limite", type=int, default=8)
    ap.add_argument("--largura-min", type=int, default=900)
    ap.add_argument("--json")
    ap.add_argument("--todos", action="store_true", help="mostra também NAO-USAR e pequenas")
    args = ap.parse_args()

    if not args.termo and not args.categoria:
        sys.exit("informe um termo de busca ou --categoria")

    titulos = buscar_arquivos(termo=args.termo, categoria=args.categoria,
                              limite=args.limite if args.todos else max(args.limite * 3, 12))
    candidatos = fichas(titulos)

    bons = []
    for c in candidatos:
        pequena = (c["largura_original"] or 0) < args.largura_min
        if not args.todos and (pequena or c["mime"] not in ("image/jpeg", "image/png")
                               or c["grupo"] == "NAO-USAR"):
            continue
        bons.append(c)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(bons, fh, ensure_ascii=False, indent=1)
        print(f"candidatos gravados em {args.json}")

    print(f"\n{len(bons)} candidato(s) utilizável(is) de {len(candidatos)} analisado(s)\n")
    print(f"{'licença':<11} {'autor':<26} {'data':<15} {'px':<12} {'KB':>6}  arquivo")
    for c in sorted(bons, key=lambda x: (x["grupo"] != "LIVRE", -(x["largura_original"] or 0))):
        autor = re.sub(r"\s+", " ", c["artista"])[:24] or "—"
        px = f"{c['largura_original']}x{c['altura_original']}"
        print(f"{c['grupo']:<11} {autor:<26} {c['data'][:14]:<15} {px:<12} {c['kb_original']:>6}  {c['arquivo']}")
    print("\npáginas de origem (é o que entra na ficha da figura):")
    for c in bons[:15]:
        print(f"  [{c['grupo']:<10}] {c['licenca']:<22} {c['pagina']}")


if __name__ == "__main__":
    main()

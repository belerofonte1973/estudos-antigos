#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scratch do lote de especificações: roda várias buscas e imprime os candidatos
utilizáveis em forma compacta (licença, autor, data, acervo, descrição, px).
Não grava nada além do cache normal de commons_api."""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import buscar_arquivos, fichas  # noqa: E402


def limpa(t: str, n: int) -> str:
    t = re.sub(r"\s+", " ", (t or "").strip())
    return t[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True, help="termos separados por |")
    ap.add_argument("--categoria", default=None, help="usa categoria em vez de termos")
    ap.add_argument("--limite", type=int, default=8)
    ap.add_argument("--largura-min", type=int, default=900)
    ap.add_argument("--desc", type=int, default=260)
    args = ap.parse_args()

    consultas = [q.strip() for q in args.queries.split("|") if q.strip()]
    for q in consultas:
        try:
            if args.categoria:
                titulos = buscar_arquivos(categoria=q, limite=max(args.limite * 3, 18))
            else:
                titulos = buscar_arquivos(termo=q, limite=max(args.limite * 3, 18))
        except Exception as e:  # noqa: BLE001
            print(f"\n=== {q}\n  !! erro: {e}")
            continue
        cands = fichas(titulos)
        bons = [c for c in cands
                if c["grupo"] != "NAO-USAR"
                and (c["largura_original"] or 0) >= args.largura_min
                and c["mime"] in ("image/jpeg", "image/png")]
        bons.sort(key=lambda x: (x["grupo"] != "LIVRE", -(x["largura_original"] or 0)))
        print(f"\n=== {q}  ({len(bons)} utilizáveis)")
        for c in bons[: args.limite]:
            px = f"{c['largura_original']}x{c['altura_original']}"
            print(f"[{c['grupo']}/{c['licenca']}] {c['arquivo']}")
            print(f"   autor: {limpa(c['artista'], 70)} | data: {limpa(c['data'], 24)} | px: {px}")
            print(f"   acervo: {limpa(c['acervo'], 140)}")
            print(f"   desc: {limpa(c['descricao_fonte'], args.desc)}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

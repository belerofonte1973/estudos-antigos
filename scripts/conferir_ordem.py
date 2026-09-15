#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Confere a invariante de `ordem` no acervo — a que a ordenação do site exige.

O que quebra de verdade, lendo o código das páginas:

- `src/pages/biblioteca/[area].astro` e o índice lateral do `BibliotecaLayout`
  ordenam por `ordem` **dentro de uma área** → duas `ordem` iguais na MESMA área
  deixam Rute e Samuel em ordem arbitrária (foi o caso: ambos com 8, 14/set/2026).
- `EixoHub.astro` agrupa por área e ordena por `ordem` dentro do grupo → a mesma
  exigência vale para cada par (eixo, área).
- Entre áreas diferentes, repetir `ordem` é inofensivo: cada grupo é filtrado de
  uma lista já ordenada e as seções seguem a ordem de AREAS. Por isso `ordem: 0`
  é o valor convencional do **dossiê de abertura** de cada área (as três
  introduções, a Pré-História e a Suméria) — todas em áreas distintas.

Uso:
    python scripts/conferir_ordem.py            # exit 1 se houver colisão
    python scripts/conferir_ordem.py --verboso  # mostra também a sequência
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BIBLIOTECA = RAIZ / "src" / "content" / "biblioteca"


def campo(texto: str, chave: str) -> str:
    m = re.search(rf"^{chave}:\s*(.+)$", texto, re.M)
    return m.group(1).strip().strip("'\"") if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verboso", action="store_true")
    args = ap.parse_args()

    itens = []
    for p in sorted(BIBLIOTECA.glob("*/*.mdx")):
        t = p.open(encoding="utf-8").read()[:1500]
        itens.append(
            {
                "slug": p.stem,
                "area": campo(t, "area"),
                "eixo": campo(t, "eixo"),
                "ordem": int(campo(t, "ordem") or 0),
            }
        )

    colisoes = []
    for chave_nome, chave_fn in (
        ("área", lambda i: (i["area"],)),
        ("(eixo, área)", lambda i: (i["eixo"], i["area"])),
    ):
        grupos = defaultdict(list)
        for i in itens:
            grupos[chave_fn(i)].append(i)
        for g, lista in grupos.items():
            por_ordem = defaultdict(list)
            for i in lista:
                por_ordem[i["ordem"]].append(i["slug"])
            for ordem, slugs in sorted(por_ordem.items()):
                if len(slugs) > 1:
                    colisoes.append(f"{chave_nome} {g[0] if len(g) == 1 else g}: ordem {ordem} → {slugs}")

    if args.verboso:
        for i in sorted(itens, key=lambda x: (x["area"], x["ordem"], x["slug"])):
            print(f"  {i['area']:13s} {i['eixo']:9s} {i['ordem']:3d}  {i['slug']}")

    print("=" * 72)
    if colisoes:
        print("COLISÕES DE `ordem` NO MESMO GRUPO DE EXIBIÇÃO:")
        for c in colisoes:
            print("  ✗", c)
        return 1
    print(f"OK — {len(itens)} dossiês; `ordem` única em cada área e em cada (eixo, área).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

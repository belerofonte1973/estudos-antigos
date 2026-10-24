#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pesquisar_figuras.py — levanta os candidatos a figura do dossiê
Técnicas de Estudo e confere a ficha de cada um na API do Commons.

Por que existe: as 5 figuras do MASTER citam um `File:...` no Commons, mas os
arquivos nunca foram baixados — o HTML referencia `imagens/01-…jpg` que não
existe. Antes de baixar, cada título tem de ser CONFIRMADO na API (existência,
licença, autor, data, acervo): título escrito de memória é o erro que o
caderno de encargos do acervo existe para impedir.

As fichas são pedidas em LOTES (`fichas()`, uma chamada para até 50 títulos) —
chamada por candidato estoura o limite de 429 do Commons.

    python dossies/tecnicas-estudo/pesquisar_figuras.py
"""
from __future__ import annotations

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import buscar_arquivos, fichas  # noqa: E402

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI / "_bruto_candidatos.json"

# O que o MASTER pede, na ordem em que as figuras aparecem.
# `citado` e o File: que a ficha da figura nomeia; `busca` e o termo usado para
# achar um candidato quando o citado nao existe ou nao serve.
PEDIDOS = [
    {"fig": 1, "tema": "ars memoriae de Robert Fludd",
     "citado": "File:Ars Memoriæ.jpg",
     "busca": "Ars Memoriæ Fludd"},
    {"fig": 2, "tema": "regioes do cerebro envolvidas na memoria",
     "citado": "File:Brain regions in memory formation.jpg",
     "busca": "brain regions memory formation"},
    {"fig": 3, "tema": "palacio da memoria / teatro da memoria de Fludd",
     "citado": "File:De praeternaturali utriusque… Fludd, 1621 Wellcome L0016208.jpg",
     "busca": "De praeternaturali utriusque mundi Fludd"},
    {"fig": 4, "tema": "ciclo do aprendizado: atencao, codificacao, consolidacao, recuperacao",
     "citado": "File:Brain regions in memory formation.jpg",
     "busca": "memory consolidation sleep learning cycle"},
    {"fig": 5, "tema": "Sisifo empurrando a pedra (Ticiano)",
     "citado": "File:Tizian 092.jpg",
     "busca": "Sisyphus Titian"},
]

LIMITE_BUSCA = 8


def mostra(ficha: dict, marca: str = "  ") -> None:
    print(f"  {marca} {ficha['arquivo']}")
    print(f"       {ficha['licenca']} [{ficha['grupo']}]  "
          f"{ficha['largura_original']}x{ficha['altura_original']}  "
          f"{ficha['kb_original']} KB  {ficha['mime']}")
    print(f"       artista: {ficha['artista'][:80]}")
    print(f"       data   : {ficha['data'][:60]}")
    print(f"       acervo : {ficha['acervo'][:100]}")


def main() -> None:
    relatorio = []
    titulos: list[str] = []
    for p in PEDIDOS:
        print(f"\n===== Fig. {p['fig']} — {p['tema']}")
        candidatos = buscar_arquivos(p["busca"], limite=LIMITE_BUSCA)
        print(f"  busca: {p['busca']}")
        if p["citado"] not in candidatos:
            candidatos = [p["citado"]] + candidatos
        titulos.extend(candidatos)
        relatorio.append({"fig": p["fig"], "tema": p["tema"], "citado": p["citado"],
                          "candidatos": candidatos})

    # um lote so, com todos os titulos vistos
    fichas_por_titulo = {f["arquivo"]: f for f in fichas(sorted(set(titulos)))}
    print(f"\n\n########## FICHAS ({len(fichas_por_titulo)} titulos resolvidos) ##########")
    for r in relatorio:
        print(f"\n===== Fig. {r['fig']} — {r['tema']}")
        for t in r["candidatos"]:
            f = fichas_por_titulo.get(t)
            if f:
                mostra(f, "->" if t == r["citado"] else "  ")
            else:
                print(f"  --  {t}  (nao resolvido)")
        r["fichas"] = {t: fichas_por_titulo.get(t) for t in r["candidatos"]}

    SAIDA.write_text(json.dumps(relatorio, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nrelatorio: {SAIDA}")


if __name__ == "__main__":
    main()

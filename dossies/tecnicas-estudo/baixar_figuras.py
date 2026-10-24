#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""baixar_figuras.py — baixa as 5 figuras do dossiê Técnicas de Estudo.

Por que este script existe: o MASTER referencia `imagens/01-…jpg` …
`imagens/05-…jpg`, mas esses arquivos nunca foram baixados (o HTML e o PDF saem
com as figuras quebradas) e 4 dos 5 `File:` citados nas fichas estavam errados —
dois não existem no Commons e dois são outra obra (o `File:Tizian 092.jpg` citado
para o Sísifo é, na verdade, o rapto de Lucrécia).

O que vale é o que a API do Commons disser: cada `arquivo` é confirmado aqui, na
hora do download, e licença/autor/data/acervo saem da resposta — o humano só
fornece o `src` que o MASTER referencia.

    python dossies/tecnicas-estudo/baixar_figuras.py --seco   # so relata
    python dossies/tecnicas-estudo/baixar_figuras.py
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import re
import sys
import unicodedata

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from commons_api import fichas                                    # noqa: E402
from imagens_baixar import baixar_arquivo, normalizar, urls_da_figura  # noqa: E402

AQUI = pathlib.Path(__file__).resolve().parent
IMAGENS = AQUI / "imagens"
ESPEC = AQUI / "espec_figuras.json"
MANIFESTO = AQUI / "figuras.json"
MIMES_OK = ("image/jpeg", "image/png")


def apelido(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:58].strip("-") or "figura"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--largura", type=int, default=1100)
    ap.add_argument("--qualidade", type=int, default=84)
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()

    espec = json.loads(ESPEC.read_text(encoding="utf-8"))
    pedidos = [f["arquivo"].strip() for f in espec["figuras"]]
    catalogo = {normalizar(f["arquivo"]): f for f in fichas(pedidos)}

    figuras, recusadas = [], []
    for i, fig in enumerate(espec["figuras"], start=1):
        ficha = catalogo.get(normalizar(fig["arquivo"]))
        if ficha is None:
            recusadas.append((fig["arquivo"], "não existe no Commons (título exato?)"))
            continue
        if ficha["grupo"] == "NAO-USAR":
            recusadas.append((fig["arquivo"], f"licença veda reuso: {ficha['licenca']}"))
            continue
        if ficha["mime"] not in MIMES_OK:
            recusadas.append((fig["arquivo"], f"mime {ficha['mime']}"))
            continue
        if (ficha["largura_original"] or 0) < 700:
            recusadas.append((fig["arquivo"], f"pequena: {ficha['largura_original']}px"))
            continue

        nome = pathlib.Path(fig["src"]).name          # o MASTER dita o nome
        registro = {
            "ordem": i,
            "arquivo_origem": ficha["arquivo"],
            "src": fig["src"],
            "titulo": "",
            "tecnica": "",
            "data": ficha["data"] or "",
            "acervo": ficha["acervo"] or "",
            "artista": ficha["artista"] or "",
            "licenca": ficha["licenca"] or "",
            "licenca_url": ficha["licenca_url"] or "",
            "grupo_licenca": ficha["grupo"],
            "fonte": ficha["pagina"],
            "secao": str(fig["secao"]),
            "posicao": fig.get("posicao", "fim"),
            "largura_original": ficha["largura_original"],
            "altura_original": ficha["altura_original"],
            "descricao_fonte": ficha["descricao_fonte"][:400],
        }
        print(f"\nFig. {i}  {fig['arquivo']}")
        print(f"   {ficha['licenca']} [{ficha['grupo']}]  "
              f"{ficha['largura_original']}x{ficha['altura_original']}  {ficha['mime']}")
        print(f"   artista: {ficha['artista'][:80]}")
        print(f"   data   : {ficha['data'][:60]}")
        print(f"   acervo : {ficha['acervo'][:100]}")
        print(f"   desc   : {' '.join(ficha['descricao_fonte'].split())[:200]}")
        if args.seco:
            figuras.append(registro)
            continue

        IMAGENS.mkdir(parents=True, exist_ok=True)
        alvo = IMAGENS / nome
        bruto = baixar_arquivo(urls_da_figura(ficha, args.largura))
        if bruto is None:
            recusadas.append((fig["arquivo"], "falha no download (429/rede)"))
            continue
        try:
            im = Image.open(io.BytesIO(bruto))
        except Exception as e:  # noqa: BLE001
            recusadas.append((fig["arquivo"], f"não é imagem: {e}"))
            continue
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        if im.width > args.largura:
            im = im.resize((args.largura, round(im.height * args.largura / im.width)),
                           Image.LANCZOS)
        im.save(alvo, "JPEG", quality=args.qualidade, optimize=True, progressive=True)
        dados = alvo.read_bytes()
        registro["bytes"] = len(dados)
        registro["sha256"] = hashlib.sha256(dados).hexdigest()[:16]
        registro["largura_final"] = im.width
        registro["altura_final"] = im.height
        print(f"   -> {alvo.name}  {im.width}x{im.height}  {len(dados)/1024:.1f} KB")
        figuras.append(registro)

    MANIFESTO.write_text(
        json.dumps({"slug": espec["slug"], "figuras": figuras},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nmanifesto: {MANIFESTO}  ({len(figuras)} figuras)")
    if recusadas:
        print("\nRECUSADAS:")
        for arq, motivo in recusadas:
            print(f"  - {arq}: {motivo}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

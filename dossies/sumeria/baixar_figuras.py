#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
baixar_figuras.py — baixa as figuras do dossiê 4-formatos da Suméria.

Diferente do pipeline do site (`scripts/imagens_baixar.py`, que serve
`public/imagens/<slug>/` em webp para o Astro), este grava JPEG em
`dossies/sumeria/imagens/`, que é o que o HTML local e o fpdf2 consomem bem.

O que vale é o que a API do Commons disser: licença, autor, data, acervo e URL
da fonte são reconferidos aqui, na hora do download. O único campo de texto que
vem do humano é o `arquivo` (`File:...`) e a legenda editorial.

    python dossies/sumeria/baixar_figuras.py            # baixa e grava o manifesto
    python dossies/sumeria/baixar_figuras.py --seco     # só relata
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
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
    import re
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
    catalogo: dict[str, dict] = {}
    for i in range(0, len(pedidos), 40):
        for f in fichas(pedidos[i:i + 40]):
            catalogo[normalizar(f["arquivo"])] = f

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
        if (ficha["largura_original"] or 0) < 800:
            recusadas.append((fig["arquivo"], f"pequena: {ficha['largura_original']}px"))
            continue

        nome = f"{i:02d}-{apelido(fig['titulo'])}.jpg"
        # acervo "-" = deixe em branco (o valor da API era boilerplate)
        acervo = fig.get("acervo", "")
        acervo = "" if acervo.strip() == "-" else (acervo.strip() or ficha["acervo"] or "")
        registro = {
            "ordem": i,
            "arquivo_origem": ficha["arquivo"],
            "src": f"imagens/{nome}",
            "titulo": fig["titulo"],
            "alt": fig.get("alt", ""),
            "legenda": fig["legenda"],
            "tecnica": fig.get("tecnica") or "",
            "data": (fig.get("data") or "").strip() or ficha["data"] or "",
            "acervo": acervo,
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
        figuras.append(registro)
        print(f"  ok  {nome}  ({im.width}x{im.height}, {len(dados)//1024} KB, "
              f"{registro['grupo_licenca']} — {registro['licenca']})")

    manifesto = {
        "slug": "sumeria-4f",
        "gerado_por": "dossies/sumeria/baixar_figuras.py",
        "formato": "jpeg",
        "largura_max": args.largura,
        "qualidade": args.qualidade,
        "total": len(figuras),
        "livres": sum(1 for f in figuras if f["grupo_licenca"] == "LIVRE"),
        "atribuicao": sum(1 for f in figuras if f["grupo_licenca"] == "ATRIBUICAO"),
        "figuras": figuras,
        "recusadas": recusadas,
    }
    if not args.seco:
        MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=1),
                             encoding="utf-8")

    print(f"\n{len(figuras)} figuras baixadas "
          f"({manifesto['livres']} LIVRE, {manifesto['atribuicao']} ATRIBUICAO); "
          f"{len(recusadas)} recusadas")
    for a, motivo in recusadas:
        print(f"  RECUSADA {a}: {motivo}")
    if not args.seco:
        print(f"manifesto: {MANIFESTO}")


if __name__ == "__main__":
    main()

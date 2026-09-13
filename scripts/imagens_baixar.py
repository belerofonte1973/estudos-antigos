#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imagens_baixar.py — transforma uma ESPECIFICAÇÃO editorial de figuras num
conjunto de arquivos prontos para o site, com ficha completa e verificável.

Entrada: um JSON por dossiê, com o que o dossiê precisa mostrar e qual obra do
Commons serve (ver `_imagens/espec_<slug>.json`). Só o campo `arquivo`
(File:...) e os textos são do humano; TODO o resto — licença, autor, data,
acervo, URL da fonte — é reconferido na API do Commons na hora do download, e
o que a API disser vence.

    {
      "slug": "juizes",
      "figuras": [
        {
          "arquivo": "File:Peter Paul Rubens - Samson and Delilah - Google Art Project.jpg",
          "titulo": "Sansão e Dalila",
          "legenda": "Dalila adormece Sansão sobre os joelhos...",
          "passagem": "Jz 16,4-22",
          "artista": "Peter Paul Rubens",         # opcional: em PT-BR se quiser
          "data": "c. 1609-1610",
          "tecnica": "óleo sobre tela",
          "acervo": "The National Gallery, Londres",
          "secao": "6",                            # seção do dossiê que recebe
          "posicao": "fim"                         # "fim" (padrão) ou "inicio"
        }
      ]
    }

O que grava:
    public/imagens/<slug>/<nn>-<apelido>.jpg   (JPEG progressivo, largura máx. 1400)
    _imagens/<slug>.json                       (manifesto com a ficha de cada figura)

Recusa (e não grava nada daquela figura) quando: arquivo não existe, licença não
permite reuso (grupo NAO-USAR), formato não é jpeg/png, ou largura original
abaixo do mínimo. Nunca inventa metadado: campo ausente na API fica ausente.

Uso:
    python scripts/imagens_baixar.py --spec _imagens/espec_juizes.json
    python scripts/imagens_baixar.py --spec ... --seco     # só relata, não baixa
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import re
import unicodedata
import urllib.request

from PIL import Image

from commons_api import ficha as ficha_commons

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO_IMG = RAIZ / "public" / "imagens"
DESTINO_META = RAIZ / "_imagens"
UA = "EstudosAntigos/1.0 (site didatico de Antiguidade Biblica; pesquisa de imagens)"
MIMES_OK = ("image/jpeg", "image/png")


def apelido(texto: str, n: int) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return f"{n:02d}-{t[:60].strip('-') or 'figura'}"


def processar(spec: dict, largura: int, qualidade: int, formato: str, seco: bool) -> dict:
    slug = spec["slug"]
    pasta = DESTINO_IMG / slug
    manifestadas, recusadas = [], []
    ext = ".webp" if formato == "webp" else ".jpg"

    for i, fig in enumerate(spec.get("figuras", []), start=1):
        arquivo = fig.get("arquivo", "").strip()
        if not arquivo:
            recusadas.append((fig.get("titulo", f"figura {i}"), "sem campo 'arquivo'"))
            continue
        ficha = ficha_commons(arquivo)
        if ficha is None:
            recusadas.append((arquivo, "arquivo não existe no Commons"))
            continue
        if ficha["grupo"] == "NAO-USAR":
            recusadas.append((arquivo, f"licença não permite reuso: {ficha['licenca'] or 'não declarada'}"))
            continue
        if ficha["mime"] not in MIMES_OK:
            recusadas.append((arquivo, f"formato não suportado: {ficha['mime']}"))
            continue
        if (ficha["largura_original"] or 0) < 800:
            recusadas.append((arquivo, f"pequena demais: {ficha['largura_original']}px"))
            continue

        nome = apelido(fig.get("titulo") or ficha["arquivo"], i) + ext
        alvo = pasta / nome
        registro = {
            "ordem": i,
            "src": f"/imagens/{slug}/{nome}",
            "arquivo_origem": ficha["arquivo"],
            "titulo": fig.get("titulo", ""),
            "legenda": fig.get("legenda", ""),
            "passagem": fig.get("passagem", ""),
            "artista": fig.get("artista") or ficha["artista"],
            "data": fig.get("data") or ficha["data"],
            "tecnica": fig.get("tecnica", ""),
            "acervo": fig.get("acervo") or ficha["acervo"],
            "fonte": ficha["pagina"],
            "fonte_rotulo": fig.get("fonte_rotulo", "Wikimedia Commons"),
            "licenca": ficha["licenca"],
            "licenca_url": ficha["licenca_url"],
            "grupo_licenca": ficha["grupo"],
            "largura_original": ficha["largura_original"],
            "altura_original": ficha["altura_original"],
            "secao": str(fig.get("secao", "6")),
            "posicao": fig.get("posicao", "fim"),
            "descricao_fonte": ficha["descricao_fonte"],
        }

        if not seco:
            pasta.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(ficha["url_thumb"], headers={"User-Agent": UA})
            bruto = urllib.request.urlopen(req, timeout=90).read()
            im = Image.open(io.BytesIO(bruto))
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            if im.width > largura:
                im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
            if formato == "webp":
                im.save(alvo, "WEBP", quality=qualidade, method=6)
            else:
                im.save(alvo, "JPEG", quality=qualidade, optimize=True, progressive=True)
            dados = alvo.read_bytes()
            registro["sha256"] = hashlib.sha256(dados).hexdigest()[:16]
            registro["bytes"] = len(dados)
            registro["largura_final"] = im.width
            registro["altura_final"] = im.height
        manifestadas.append(registro)

    resultado = {"slug": slug, "gerado_por": "scripts/imagens_baixar.py",
                 "formato": formato, "largura_max": largura, "qualidade": qualidade,
                 "figuras": manifestadas, "recusadas": recusadas}
    return resultado


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--largura", type=int, default=1300)
    ap.add_argument("--qualidade", type=int, default=80)
    ap.add_argument("--formato", default="webp", choices=("webp", "jpeg"),
                    help="webp (padrão, ~40%% menor) ou jpeg")
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()

    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    resultado = processar(spec, args.largura, args.qualidade, args.formato, args.seco)
    slug = resultado["slug"]

    print(f"dossiê: {slug} · {len(resultado['figuras'])} figura(s) aceita(s) · "
          f"{len(resultado['recusadas'])} recusada(s)")
    for r in resultado["figuras"]:
        tam = f"{r.get('largura_final', '?')}x{r.get('altura_final', '?')} {r.get('bytes', 0) // 1024} KB" \
            if not args.seco else f"(seco) original {r['largura_original']}px"
        print(f"  [{r['grupo_licenca']:<10}] {r['licenca']:<22} {tam:<22} {r['src']}")
    for arq, motivo in resultado["recusadas"]:
        print(f"  RECUSADA: {arq} — {motivo}")

    if args.seco:
        print("\n(--seco: nada foi gravado)")
        return
    if resultado["recusadas"]:
        print(f"\nATENÇÃO: {len(resultado['recusadas'])} figura(s) ficaram de fora. "
              f"O manifesto registra a recusa — não substitua por fonte duvidosa.")
    DESTINO_META.mkdir(parents=True, exist_ok=True)
    saida = DESTINO_META / f"{slug}.json"
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nmanifesto: {saida}")
    print(f"imagens:   {DESTINO_IMG / slug}")


if __name__ == "__main__":
    main()

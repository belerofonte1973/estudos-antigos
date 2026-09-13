#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
commons_api.py — acesso único à API do Wikimedia Commons, com o que a pesquisa
de imagens em lote exige e que a experiência cobrou:

  * THROTTLE: no máximo uma chamada a cada MIN_INTERVALO segundos. A API do
    Commons devolve HTTP 429 quando alguém dispara buscas em série (aconteceu na
    primeira montagem do acervo) — e um 429 tratado como "não achei" viraria
    lacuna de imagem por engano.
  * BACKOFF: 429/5xx são repetidos com espera crescente; falha de rede também.
  * CACHE em disco (_imagens/cache/<sha1>.json): a mesma consulta não é refeita
    — economiza chamadas, torna a execução retomável e deixa rastro auditável.
  * METADADOS: funções prontas para classificar licença e limpar HTML dos campos
    do extmetadata.

Uso típico (em outro script do acervo):

    from commons_api import buscar_arquivos, ficha, classificar
    titulos = buscar_arquivos(termo="Samson lion", limite=10)
    for t in titulos:
        f = ficha(t)
        if f and f["grupo"] != "NAO-USAR":
            print(f["arquivo"], f["licenca"], f["artista"])
"""
from __future__ import annotations

import hashlib
import html
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "EstudosAntigos/1.0 (site didatico de Antiguidade Biblica; pesquisa de imagens; contato pelo site)"
RAIZ = pathlib.Path(__file__).resolve().parent.parent
CACHE = RAIZ / "_imagens" / "cache"

MIN_INTERVALO = 1.1      # segundos entre chamadas
TENTATIVAS = 4
LIVRES = ("public domain", "pdm", "cc0", "public domain mark")
ATRIBUICAO = ("cc by", "cc-by", "attribution")

_ultimo = [0.0]


def _esperar() -> None:
    dt = time.time() - _ultimo[0]
    if dt < MIN_INTERVALO:
        time.sleep(MIN_INTERVALO - dt)
    _ultimo[0] = time.time()


def classificar(licenca: str) -> str:
    """LIVRE (sem obrigação) · ATRIBUICAO (CC BY/BY-SA) · NAO-USAR."""
    b = (licenca or "").strip().lower()
    if not b:
        return "NAO-USAR"
    if any(x in b for x in LIVRES):
        return "LIVRE"
    if any(x in b for x in ATRIBUICAO):
        return "ATRIBUICAO"
    return "NAO-USAR"


def limpar(texto: str) -> str:
    """Tira HTML e espaços repetidos dos campos do extmetadata."""
    t = re.sub(r"<[^>]+>", " ", texto or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def api(params: dict, usar_cache: bool = True) -> dict:
    chave = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()[:20]
    arquivo = CACHE / f"{chave}.json"
    if usar_cache and arquivo.exists():
        return json.loads(arquivo.read_text(encoding="utf-8"))

    params = dict(params)
    params.setdefault("format", "json")
    url = API + "?" + urllib.parse.urlencode(params)
    erro = None
    for tentativa in range(TENTATIVAS):
        _esperar()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            dados = json.loads(urllib.request.urlopen(req, timeout=45).read().decode("utf-8"))
            CACHE.mkdir(parents=True, exist_ok=True)
            arquivo.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
            return dados
        except urllib.error.HTTPError as e:
            erro = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2.0 * (tentativa + 1) ** 2)   # 2s, 8s, 18s
                continue
            raise
        except Exception as e:  # noqa: BLE001 — rede instável
            erro = e
            time.sleep(2.0 * (tentativa + 1))
    raise RuntimeError(f"API do Commons não respondeu após {TENTATIVAS} tentativas: {erro}")


def buscar_arquivos(termo: str | None = None, categoria: str | None = None,
                    limite: int = 10) -> list[str]:
    """Títulos de arquivo (namespace 6) por busca livre ou por categoria."""
    if categoria:
        r = api({"action": "query", "list": "categorymembers", "cmtitle": categoria,
                 "cmtype": "file", "cmlimit": limite})
        return [x["title"] for x in r.get("query", {}).get("categorymembers", [])]
    r = api({"action": "query", "list": "search", "srsearch": termo,
             "srnamespace": 6, "srlimit": limite})
    return [x["title"] for x in r.get("query", {}).get("search", [])]


def ficha(arquivo: str, largura_thumb: int = 1400) -> dict | None:
    """Metadados completos de um arquivo. None se não existir."""
    r = api({"action": "query", "titles": arquivo, "prop": "imageinfo",
             "iiprop": "url|size|mime|extmetadata", "iiurlwidth": largura_thumb})
    paginas = list(r.get("query", {}).get("pages", {}).values())
    if not paginas or "imageinfo" not in paginas[0]:
        return None
    p = paginas[0]
    ii = p["imageinfo"][0]
    em = ii.get("extmetadata", {})

    def g(k: str) -> str:
        return limpar(str(em.get(k, {}).get("value", "")))

    licenca = g("LicenseShortName") or g("License")
    return {
        "arquivo": p["title"],
        "licenca": licenca,
        "grupo": classificar(licenca),
        "licenca_url": g("LicenseUrl"),
        "artista": g("Artist") or "anônimo",
        "data": re.sub(r"date QS:.*", "", g("DateTimeOriginal")).strip(),
        "acervo": g("Credit") or g("Source"),
        "descricao_fonte": g("ImageDescription")[:500],
        "largura_original": ii.get("width"),
        "altura_original": ii.get("height"),
        "mime": ii.get("mime"),
        "kb_original": round((ii.get("size") or 0) / 1024),
        "url_thumb": ii.get("thumburl") or ii.get("url"),
        "url_original": ii.get("url"),
        "pagina": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")),
    }


def fichas(arquivos: list[str], largura_thumb: int = 1400) -> list[dict]:
    """Fichas de vários arquivos numa chamada só (mais econômico)."""
    if not arquivos:
        return []
    r = api({"action": "query", "titles": "|".join(arquivos), "prop": "imageinfo",
             "iiprop": "url|size|mime|extmetadata", "iiurlwidth": largura_thumb})
    saida = []
    for p in r.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        em = ii.get("extmetadata", {})

        def g(k: str) -> str:
            return limpar(str(em.get(k, {}).get("value", "")))

        licenca = g("LicenseShortName") or g("License")
        saida.append({
            "arquivo": p["title"], "licenca": licenca, "grupo": classificar(licenca),
            "licenca_url": g("LicenseUrl"), "artista": g("Artist") or "anônimo",
            "data": re.sub(r"date QS:.*", "", g("DateTimeOriginal")).strip(),
            "acervo": g("Credit") or g("Source"), "descricao_fonte": g("ImageDescription")[:500],
            "largura_original": ii.get("width"), "altura_original": ii.get("height"),
            "mime": ii.get("mime"), "kb_original": round((ii.get("size") or 0) / 1024),
            "url_thumb": ii.get("thumburl") or ii.get("url"), "url_original": ii.get("url"),
            "pagina": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")),
        })
    return saida

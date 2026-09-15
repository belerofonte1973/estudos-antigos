#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
status.py — estado do acervo em ~20 linhas, para caber no contexto.

Por que existe: verificar o acervo lendo a saída inteira do validador (56 blocos
com métricas por dossiê) custa milhares de tokens de contexto — e numa sessão de
300 chamadas esse texto é reenviado no prefixo de todas as seguintes. Este script
imprime SÓ o que decide a próxima ação: contagens, falhas, avisos com o motivo em
duas palavras, artefatos e git.

Uso:
    python scripts/status.py            # tudo (roda o validador: ~40s)
    python scripts/status.py --rapido   # pula o validador (~1s)
    python scripts/status.py --sem-rede # não testa o site publicado
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BIBLIA = RAIZ / "src" / "content" / "biblioteca" / "biblia"
IMAGENS = RAIZ / "public" / "imagens"
SITE = "https://estudos-antigos.netlify.app/"
LINHA = "=" * 66


def mb(n: int) -> str:
    return f"{n / 1024 / 1024:.0f} MB"


def dossies() -> int:
    return len(list(BIBLIA.glob("*.mdx")))


def figuras() -> tuple[int, int, int, int, int]:
    esp = grav = rec = 0
    for spec in sorted((RAIZ / "_imagens").glob("espec_*.json")):
        esp += len(json.loads(spec.read_text(encoding="utf-8")).get("figuras", []))
        man = RAIZ / "_imagens" / spec.name.replace("espec_", "")
        if man.exists():
            m = json.loads(man.read_text(encoding="utf-8"))
            grav += len(m.get("figuras", []))
            rec += len(m.get("recusadas", []))
    webp = [p for p in IMAGENS.rglob("*.webp")] if IMAGENS.exists() else []
    peso = sum(p.stat().st_size for p in webp)
    return esp, grav, rec, len(webp), peso


def validar() -> tuple[str, list[str]]:
    """(linha de resumo, avisos abreviados por dossiê)."""
    r = subprocess.run([sys.executable, str(RAIZ / "validar_dossie.py"), "--todos"],
                       capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
    txt = (r.stdout or "") + (r.stderr or "")
    resumo = next((l.strip() for l in reversed(txt.splitlines()) if "falha" in l), "?")
    atual, avisos = None, []
    for linha in txt.splitlines():
        m = re.match(r"\s+([a-z0-9\-]+)\.mdx\s+\[(OK|FALHA)[^\]]*\]", linha)
        if m:
            atual = m.group(1)
            continue
        if linha.strip().startswith("·") and atual:
            motivo = linha.strip().lstrip("· ").strip()
            motivo = re.sub(r"^\d+(\.\d+)?\s*", "", motivo)
            if "sem as esferas" in motivo:
                motivo = "11.1 sem " + ", ".join(re.findall(r"'([^']+)'", motivo))
            elif "description" in motivo:
                motivo = "descrição longa"
            elif "H2 fora da forma" in motivo:
                motivo = "H2 fora da forma"
            avisos.append(f"{atual}({motivo})")
    return resumo, avisos


def paginas(pasta: pathlib.Path) -> int:
    return len(list(pasta.rglob("*.html"))) if pasta.exists() else 0


def carimbo(p: pathlib.Path) -> str:
    if not p.exists():
        return "ausente"
    recente = max((f.stat().st_mtime for f in p.rglob("*") if f.is_file()), default=0)
    return dt.datetime.fromtimestamp(recente).strftime("%d/%m %H:%M") if recente else "?"


def pdfs() -> tuple[int, int]:
    p = RAIZ / "html-avulso" / "pdf"
    arqs = list(p.glob("*.pdf")) if p.exists() else []
    return len(arqs), sum(a.stat().st_size for a in arqs)


def git() -> str:
    def rodar(*args: str) -> str:
        r = subprocess.run(["git", *args], capture_output=True, text=True,
                           encoding="utf-8", cwd=RAIZ)
        return (r.stdout or "").strip()
    head = rodar("log", "-1", "--format=%h %ad %s", "--date=format:%d/%m")
    sujos = len([l for l in rodar("status", "--short").splitlines() if l.strip()])
    return f"{head} · {'árvore limpa' if sujos == 0 else str(sujos) + ' alteração(ões)'}"


def site() -> str:
    req = urllib.request.Request(SITE, method="HEAD",
                                 headers={"User-Agent": "EstudosAntigos/status"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return "200 (público)"
    except urllib.error.HTTPError as e:
        return f"{e.code} ({'privado' if e.code in (401, 403) else 'erro'})"
    except Exception as e:  # noqa: BLE001
        return f"sem resposta ({e.__class__.__name__})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--sem-rede", action="store_true")
    args = ap.parse_args()

    n = dossies()
    esp, grav, rec, webp, peso = figuras()
    n_pdf, peso_pdf = pdfs()

    print(LINHA)
    print("ESTUDOS ANTIGOS — ESTADO " + dt.datetime.now().strftime("(%d/%m/%Y %H:%M)"))
    print(LINHA)
    print(f"ACERVO     {n} dossiês · {grav} figuras nos dossiês")
    pend = "completo" if rec == 0 and grav == esp else f"{rec} recusa(s) a re-tentar"
    print(f"FIGURAS    {grav}/{esp} especificadas · {pend} · {webp} webp ({mb(peso)})")
    if args.rapido:
        print("VALIDADOR  (pulado: --rapido)")
    else:
        resumo, avisos = validar()
        print(f"VALIDADOR  {resumo}")
        if avisos:
            print("  avisos: " + " ".join(avisos))
    print(f"BUILD      dist {paginas(RAIZ / 'dist')} páginas ({carimbo(RAIZ / 'dist')})")
    print(f"AVULSO     {paginas(RAIZ / 'html-avulso')} páginas · "
          f"{n_pdf} PDFs ({mb(peso_pdf)})")
    print(f"GIT        {git()}")
    if not args.sem_rede:
        print(f"SITE       {SITE.rstrip('/')} → {site()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

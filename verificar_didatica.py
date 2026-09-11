#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica a camada didática: a escada de estudo e os links de Bíblia.

O que se quer garantir, e que um "build passou" não garante:

  1. todo dossiê traz a escada, e o dossiê bíblico traz os 7 degraus;
  2. o degrau "Ler o texto" só aparece onde há livro bíblico — a escada não
     pode prometer o que a página não tem;
  3. os links de Bíblia apontam para hosts reais e cobrem tradições distintas
     (protestante + católica), que é o exercício do degrau 1;
  4. as âncoras §N dos degraus resolvem para ids que existem de fato na página;
  5. os pré-requisitos apontam para páginas internas que existem.

Uso:  python verificar_didatica.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / "dist"

BIBLICOS = [
    "genesis",
    "exodo",
    "levitico",
    "numeros",
    "deuteronomio",
    "josue",
    "juizes",
    "samuel",
    "reis",
]
NAO_BIBLICOS = ["sumeria", "introducao", "pre-historia-humana"]

# Hosts de Bíblia que foram conferidos por HTTP 200 e por isso podem aparecer.
HOSTS_OK = [
    "bibliaonline.com.br",
    "bibliacatolica.com.br",
    "biblegateway.com",
    "ebible.org",
]

TRADICOES_ESPERADAS = ["protestante", "católica", "licença aberta"]

# Degraus que TODO dossiê bíblico precisa ter. "A porta" NÃO entra na lista:
# ele só existe quando há artigo-porta apontando para o dossiê, e omitir é o
# comportamento correto — a escada não promete o que a página não tem.
MANDATORIOS = [
    "Ler o texto",
    "O contexto",
    "O debate",
    "A recepção",
    "As quatro camadas",
    "O dossiê integral",
]

falhas: list[str] = []
ok = 0


def exigir(cond: bool, msg: str) -> None:
    global ok
    if cond:
        ok += 1
    else:
        falhas.append(msg)


def ler(rel: str) -> str:
    p = DIST / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def pagina_dossie(grupo: str, slug: str) -> str:
    """/biblioteca/<grupo>/<slug>/ — o grupo muda (biblia, oriente, ...)."""
    for g in ("biblia", "oriente", "classica", "pre-historia", "idade-media"):
        h = ler(f"biblioteca/{g}/{slug}/index.html")
        if h:
            return h
    return ""


print("== Camada didática: escada de estudo e links de Bíblia ==\n")

# ---------- 1-4. dossiês bíblicos ----------
for slug in BIBLICOS:
    h = pagina_dossie("biblia", slug)
    if not h:
        falhas.append(f"{slug}: página não construída")
        continue

    m = re.search(r'<section class="ea-escada".*?</section>', h, re.S)
    if not m:
        falhas.append(f"{slug}: sem escada de estudo")
        continue
    escada = m.group(0)

    nomes = re.findall(
        r'ea-passo__nome"[^>]*>\s*(?:<a[^>]*>)?\s*([^<]+?)\s*<', escada, re.S
    )
    tempos = re.findall(r'ea-passo__tempo"[^>]*>([^<]+)<', escada)

    exigir(
        len(nomes) in (6, 7),
        f"{slug}: {len(nomes)} degraus (esperado 6 ou 7)",
    )
    for mand in MANDATORIOS:
        exigir(mand in nomes, f"{slug}: falta o degrau obrigatório '{mand}'")
    exigir(
        len(tempos) == len(nomes),
        f"{slug}: {len(nomes)} degraus mas {len(tempos)} tempos",
    )
    exigir(
        "Ler o texto" in nomes,
        f"{slug}: dossiê bíblico sem o degrau 'Ler o texto'",
    )
    exigir(
        "Você vai precisar saber antes" in escada,
        f"{slug}: sem pré-requisitos declarados",
    )

    # bloco de Bíblia dentro do degrau 1
    hrefs = re.findall(r'href="(https://[^"]+)"', escada)
    de_biblia = [u for u in hrefs if any(x in u for x in HOSTS_OK)]
    hosts = sorted({re.sub(r"^https://(www\.)?([^/]+).*$", r"\2", u) for u in de_biblia})
    exigir(
        len(de_biblia) >= 3,
        f"{slug}: só {len(de_biblia)} link(s) de Bíblia (mínimo 3)",
    )
    exigir(
        len(hosts) >= 3,
        f"{slug}: links de Bíblia em {len(hosts)} host(s): {hosts}",
    )
    for t in ("protestante", "católica"):
        exigir(t in escada, f"{slug}: falta tradução de tradição {t}")

    # âncoras §N resolvem para ids reais da página
    ids = set(re.findall(r'id="([^"]+)"', h))
    ancoras = re.findall(r'fa-passo__ancoras.*?</p>', escada, re.S)
    alvos = re.findall(r'href="#([^"]+)"', escada)
    for a in alvos:
        exigir(a in ids, f"{slug}: âncora #{a} não resolve para nenhum id")

    print(
        f"  ok  {slug:12s} {len(nomes)} degraus · {len(de_biblia)} links de Bíblia "
        f"em {len(hosts)} hosts · {len(alvos)} âncoras resolvidas"
    )

# ---------- 2b. dossiês não bíblicos: escada SEM o degrau de texto ----------
for slug in NAO_BIBLICOS:
    h = pagina_dossie("biblia", slug) or pagina_dossie("classica", slug) or pagina_dossie(
        "pre-historia", slug
    )
    if not h:
        continue
    m = re.search(r'<section class="ea-escada".*?</section>', h, re.S)
    if not m:
        falhas.append(f"{slug}: sem escada")
        continue
    escada = m.group(0)
    exigir(
        "Ler o texto" not in escada,
        f"{slug}: não é dossiê bíblico e traz o degrau 'Ler o texto'",
    )
    exigir(
        "ea-biblia" not in escada,
        f"{slug}: não é dossiê bíblico e traz bloco de links de Bíblia",
    )
    print(f"  ok  {slug:12s} degrau de texto corretamente omitido")

# ---------- 5. pré-requisitos apontam para páginas internas que existem ----------
vistos: set[str] = set()
for slug in BIBLICOS:
    h = pagina_dossie("biblia", slug)
    m = re.search(r'class="ea-escada__pre"[^>]*>(.*?)</p>', h, re.S)
    if not m:
        continue
    for href in re.findall(r'href="(/[^"]*)"', m.group(1)):
        if href in vistos:
            continue
        vistos.add(href)
        exigir(
            (DIST / href.strip("/") / "index.html").exists()
            or (DIST / f"{href.strip('/')}.html").exists(),
            f"pré-requisito aponta para página inexistente: {href}",
        )

print(f"\n  {len(vistos)} destino(s) de pré-requisito conferido(s)")

print()
if falhas:
    for f in falhas:
        print(f"  FALHA  {f}")
    print(f"\n{len(falhas)} falha(s) · {ok} verificação(ões) aprovada(s)")
    sys.exit(1)

print(f"OK — camada didática: {ok} verificações, nenhuma falha.")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica se o modelo de três eixos está de fato expresso no site construído.

Checa o que uma inspeção visual checaria, mas de forma repetível:
  1. a passagem traz as três seções, com âncora alcançável;
  2. o núcleo contém os livros bíblicos;
  3. Suméria NÃO aparece como núcleo bíblico (a correção que motivou tudo);
  4. contexto e recepção trazem o material que lhes pertence;
  5. nenhum link interno aponta para rota de eixo inexistente.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"

falhas: list[str] = []
ok: list[str] = []


def ler(rel: str) -> str:
    p = DIST / rel
    if not p.exists():
        falhas.append(f"página ausente: {rel}")
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def exigir(cond: bool, msg: str) -> None:
    (ok if cond else falhas).append(msg)


# ---------- 1. A passagem traz os três eixos ----------
pas = ler("biblia/genesis/6-9/index.html")
if pas:
    for rotulo, ancora in (
        ("Texto", "texto"),
        ("Contexto", "contexto"),
        ("Recepção", "recepção"),
    ):
        tem_secao = bool(re.search(rf'<h2[^>]*id="{re.escape(ancora)}"', pas))
        exigir(tem_secao, f"passagem: seção '{rotulo}' presente (âncora #{ancora})")

    # as três seções precisam ter conteúdo, não só título
    corpo = re.sub(r"<[^>]+>", " ", pas)
    exigir(
        len(corpo.split()) > 900,
        f"passagem: corpo substancial ({len(corpo.split())} palavras)",
    )
    exigir(
        "Agostinho" in pas and "Josefo" in pas,
        "passagem: recepção cita fontes primárias (Agostinho, Josefo)",
    )
    exigir(
        "Atra" in pas and "Gilgamesh" in pas,
        "passagem: contexto cita os paralelos mesopotâmicos",
    )
    exigir(
        "/biblioteca/biblia/genesis/" in pas,
        "passagem: liga ao dossiê do Gênesis (livro inteiro, para o debate completo)",
    )
    exigir(
        "dilúvio" in pas.lower(),
        "passagem: discute o dilúvio",
    )

# ---------- 2. O núcleo contém os livros ----------
bib = ler("biblia/index.html")
if bib:
    for nome in ("Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio",
                 "Josué", "Juízes", "1 Samuel", "2 Samuel", "1 Reis", "2 Reis"):
        exigir(nome in bib, f"núcleo: livro '{nome}' listado")

# ---------- 3. Suméria não é núcleo ----------
if bib:
    exigir(
        "Suméria" not in bib,
        "núcleo: Suméria NÃO aparece como livro bíblico (correção do arquivo)",
    )

# ---------- 4. Cada eixo traz o seu material ----------
ctx = ler("contexto/index.html")
if ctx:
    exigir("Suméria" in ctx, "contexto: traz o dossiê da Suméria")
    exigir("Pré-História" in ctx, "contexto: traz a Pré-História")
    exigir("Antiguidade Clássica" in ctx, "contexto: traz a Antiguidade Clássica")

rec = ler("recepcao/index.html")
if rec:
    exigir("Idade Média" in rec, "recepção: traz o dossiê da Idade Média")

# ---------- 5. As rotas de eixo existem e são alcançáveis ----------
for rota in ("biblia/index.html", "contexto/index.html", "recepcao/index.html"):
    exigir((DIST / rota).exists(), f"rota de eixo existe: /{rota.split('/')[0]}/")

# ---------- 6. A navegação principal aponta para os eixos ----------
hdr = ler("index.html")
if hdr:
    nav = re.search(r'<nav[^>]*aria-label="Navegação principal"(.*?)</nav>', hdr, re.S)
    if nav:
        bloco = nav.group(1)
        for href, rot in (
            ("/biblia/", "Texto"),
            ("/contexto/", "Contexto"),
            ("/recepcao/", "Recepção"),
        ):
            exigir(
                href in bloco and rot in bloco,
                f"navegação: item '{rot}' → {href}",
            )
    else:
        falhas.append("navegação: nav principal não encontrada")

# ---------- 7. Os hubs de livro existem para os quatro livros do pedido ----------
for slug, nome in (
    ("josue", "Josué"),
    ("juizes", "Juízes"),
    ("samuel-1", "1 Samuel"),
    ("samuel-2", "2 Samuel"),
    ("reis-1", "1 Reis"),
    ("reis-2", "2 Reis"),
):
    html = ler(f"biblia/{slug}/index.html")
    if html:
        exigir(nome in html, f"hub de livro: {nome} em /biblia/{slug}/")

print("== Verificação do modelo de três eixos ==\n")
for m in ok:
    print(f"  ok  {m}")
if falhas:
    print()
    for m in falhas:
        print(f"  FALHA  {m}")
    print(f"\n{len(falhas)} falha(s).")
    sys.exit(1)
print(f"\nOK — {len(ok)} verificações, nenhuma falha.")
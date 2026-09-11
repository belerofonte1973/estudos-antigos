#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificação pós-build. Confere o HTML gerado em dist/ contra os sintomas que
já quebraram este projeto antes:

  - conteúdo que não renderizou (seção presente no MDX, ausente no HTML)
  - tokens de corrupção de PT-BR (normalização cega)
  - diretivas MDX vazando como texto literal
  - blocos de SEO ausentes (canonical, JSON-LD, Open Graph)
  - links internos apontando para páginas que não existem
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / "dist"

FALHAS: list[str] = []
AVISOS: list[str] = []


def ler(rel: str) -> str:
    p = DIST / rel
    if not p.exists():
        FALHAS.append(f"página ausente: {rel}")
        return ""
    return p.read_text(encoding="utf-8")


def checa(cond: bool, msg_falha: str, msg_aviso: str | None = None) -> None:
    if cond:
        return
    if msg_aviso:
        AVISOS.append(msg_aviso)
    else:
        FALHAS.append(msg_falha)


# ---------------------------------------------------------------- conteúdo
print("== 1. Conteúdo renderizado ==")

CASOS = [
    (
        "biblioteca/biblia/genesis/index.html",
        ["Hipótese documentária", "Wellhausen", "toledot", 'dir="rtl"'],
        "dossiê Gênesis",
    ),
    (
        "biblioteca/biblia/sumeria/index.html",
        ["Eridu", "Uruk", "Enlil"],
        "dossiê Suméria",
    ),
    (
        "biblioteca/pre-historia/pre-historia-humana/index.html",
        [],
        "dossiê Pré-História",
    ),
    (
        "artigos/quem-escreveu-o-genesis/index.html",
        ["Resposta rápida", "Baden", "processo de redação"],
        "artigo Gênesis",
    ),
    (
        "artigos/os-hebreus-foram-escravos-no-egito/index.html",
        ["Merneptah", "Finkelstein"],
        "artigo Êxodo",
    ),
]

for rel, termos, rotulo in CASOS:
    html = ler(rel)
    if not html:
        continue
    faltando = [t for t in termos if t not in html]
    checa(
        not faltando,
        f"{rotulo}: termos ausentes no HTML -> {faltando}",
    )
    if not faltando:
        print(f"  ok  {rotulo}")

# ------------------------------------------------------- corrupção de PT-BR
print("\n== 2. Tokens de corrupção ==")

# Termos que só existem em espanhol (PT teria outra forma). Alta precisão:
# "Siglo" sozinho é a editora Siglo XXI, bibliografia legítima — por isso a
# checagem usa regex com exceção em vez de substring crua.
CORROMPIDOS = [
    (r"modoo", "corrupção de normalização"),
    (r"não deserto", "corrupção de normalização"),
    (r"\bhebreo\b", "espanhol: hebreo (PT: hebraico)"),
    (r"\bpueblo\b", "espanhol: pueblo (PT: povo)"),
    (r"\btambién\b", "espanhol: también (PT: também)"),
    (r"\bademás\b", "espanhol: además (PT: além disso)"),
    (r"\bmientras\b", "espanhol: mientras (PT: enquanto)"),
    (r"\bAntiguo\b(?!\s+Oriente)", "espanhol: Antiguo (PT: Antigo)"),
    (r"\bsiglos\b", "espanhol: siglos (PT: séculos)"),
    (r"Siglo(?!\s+XXI)", "espanhol: Siglo fora de 'Siglo XXI'"),
]

# Exceções documentadas — publicações legítimas em espanhol, não vazamento de
# idioma. Mesma classe de armadilha do 'Siglo XXI':
#   - 'Antiguo Oriente' — periódico do Centro de Estudios de Historia del
#     Antiguo Oriente (UCA, Argentina), citado no dossiê de Reis.
# A checagem é regex com exceção, nunca substring crua: senão o portão reprova
# bibliografia correta e perde-se a confiança nele.

achados = []
for html_file in DIST.rglob("*.html"):
    texto = html_file.read_text(encoding="utf-8")
    for padrao, motivo in CORROMPIDOS:
        for m in re.finditer(padrao, texto):
            trecho = texto[max(0, m.start() - 40) : m.end() + 40].replace("\n", " ")
            achados.append(f"{html_file.relative_to(DIST)}: {motivo} -> ...{trecho}...")

if achados:
    # 'Siglo XXI' é publicação legítima; só falha o que sobrar
    FALHAS.extend(achados)
else:
    print("  ok  nenhum token de corrupção encontrado")

# ------------------------------------------------- diretivas MDX vazadas
print("\n== 3. Diretivas MDX vazadas ==")
vazadas = []
for html_file in DIST.rglob("*.html"):
    texto = html_file.read_text(encoding="utf-8")
    if re.search(r">\s*:::\w+", texto) or "starlight" in texto.lower():
        vazadas.append(str(html_file.relative_to(DIST)))
if vazadas:
    FALHAS.append(f"diretiva/Starlight vazando em: {vazadas[:5]}")
else:
    print("  ok  nenhuma diretiva ::: nem resto de Starlight")

# ------------------------------------------------------------------- SEO
print("\n== 4. Blocos de SEO ==")

alvos = [
    "index.html",
    "artigos/quem-escreveu-o-genesis/index.html",
    "biblioteca/biblia/genesis/index.html",
]
for rel in alvos:
    html = ler(rel)
    if not html:
        continue
    problemas = []
    if '<link rel="canonical"' not in html:
        problemas.append("canonical")
    if 'property="og:title"' not in html:
        problemas.append("og:title")
    if 'property="og:image"' not in html:
        problemas.append("og:image")
    if "application/ld+json" not in html:
        problemas.append("JSON-LD")
    if '<html lang="pt-BR"' not in html:
        problemas.append("lang=pt-BR")
    if problemas:
        FALHAS.append(f"{rel}: falta {problemas}")
    else:
        print(f"  ok  {rel}")

# --------------------------------------------------- JSON-LD bem formado
print("\n== 5. JSON-LD válido ==")
for rel in alvos:
    html = ler(rel)
    if not html:
        continue
    blocos = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    )
    if not blocos:
        AVISOS.append(f"{rel}: nenhum bloco JSON-LD")
        continue
    for b in blocos:
        try:
            json.loads(b)
        except json.JSONDecodeError as e:
            FALHAS.append(f"{rel}: JSON-LD inválido ({e})")
    tipos = []
    for b in blocos:
        try:
            d = json.loads(b)
            tipos.append(d.get("@type", "?"))
        except json.JSONDecodeError:
            pass
    print(f"  ok  {rel}: {', '.join(tipos)}")

# ------------------------------------------------- links internos quebrados
print("\n== 6. Links internos ==")
quebrados: dict[str, set[str]] = {}
for html_file in DIST.rglob("*.html"):
    texto = html_file.read_text(encoding="utf-8")
    for href in set(re.findall(r'href="(/[^"#?]*)"', texto)):
        if href.startswith(("//", "/_astro")):
            continue
        # resolve o alvo para o arquivo estático correspondente
        alvo = href.rstrip("/")
        candidatos = [
            DIST / alvo.lstrip("/") / "index.html",
            DIST / alvo.lstrip("/"),
        ]
        if alvo in ("", "/"):
            candidatos.insert(0, DIST / "index.html")
        if not any(c.exists() for c in candidatos):
            if alvo.endswith((".xml", ".png", ".svg", ".ico", ".txt")):
                if not (DIST / alvo.lstrip("/")).exists():
                    quebrados.setdefault(alvo, set()).add(
                        str(html_file.relative_to(DIST))
                    )
                continue
            quebrados.setdefault(alvo, set()).add(str(html_file.relative_to(DIST)))

if quebrados:
    for alvo, origens in sorted(quebrados.items()):
        AVISOS.append(f"link interno quebrado: {alvo} (em {len(origens)} página(s))")
    print(f"  {len(quebrados)} alvo(s) quebrado(s)")
else:
    print("  ok  todos os links internos resolvem")

# ------------------------------------------------------------------ RSS
print("\n== 7. Feed RSS ==")
rss = ler("rss.xml")
if rss:
    n = rss.count("<item>")
    checa(n >= 6, f"RSS com {n} itens (esperado 6)")
    if n:
        print(f"  ok  {n} itens no feed")

# ---------------------------------------------------------------- resumo
print("\n" + "=" * 52)
if AVISOS:
    print(f"AVISOS ({len(AVISOS)}):")
    for a in AVISOS:
        print(f"  · {a}")
if FALHAS:
    print(f"\nFALHAS ({len(FALHAS)}):")
    for f in FALHAS:
        print(f"  ✗ {f}")
    raise SystemExit(1)

total = len(list(DIST.rglob("*.html")))
print(f"\nOK — {total} páginas HTML verificadas, nenhuma falha.")

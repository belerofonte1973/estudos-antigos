#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Encurta as meta descrições dos artigos para o limite útil de SERP.

Descrição longa é truncada pelo Google, então o excesso é desperdício — e o
schema da coleção rejeita o build. Limite alvo: 160 caracteres.
"""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent / "src" / "content" / "artigos"

NOVAS = {
    "quem-escreveu-o-genesis.md": (
        "A atribuição a Moisés durou séculos e foi desmontada pela crítica "
        "textual. No lugar dela não há um nome: há um processo de redação."
    ),
    "o-que-e-a-hipotese-documentaria.md": (
        "O modelo que explica o Pentateuco como compilação de quatro fontes "
        "— J, E, D e P — e por que a hipótese foi contestada sem ser abandonada."
    ),
    "diluvio-da-biblia-vem-de-gilgamesh.md": (
        "Os paralelos entre o dilúvio bíblico e os relatos mesopotâmicos são "
        "extensos. A direção do empréstimo, porém, continua em aberto."
    ),
    "quem-foram-os-sumerios.md": (
        "A primeira civilização urbana conhecida: Eridu e Uruk, a invenção da "
        "escrita cuneiforme e uma língua sem parentesco com nenhuma outra."
    ),
    "os-hebreus-foram-escravos-no-egito.md": (
        "A arqueologia não encontrou vestígio de êxodo em massa. A Estela de "
        "Merneptah (c. 1208 a.C.) atesta Israel em Canaã — que é outra coisa."
    ),
    "moises-existiu.md": (
        "Não há evidência direta de Moisés. O relato do seu nascimento segue o "
        "motivo do herói exposto, comum em todo o Antigo Oriente."
    ),
}

LIMITE = 160

falhas = 0
for nome, texto in NOVAS.items():
    caminho = BASE / nome
    if not caminho.exists():
        print(f"! ausente: {nome}")
        falhas += 1
        continue

    if len(texto) > LIMITE:
        print(f"! {nome}: {len(texto)} caracteres (acima de {LIMITE})")
        falhas += 1
        continue

    conteudo = caminho.read_text(encoding="utf-8")
    novo, n = re.subn(r"^descricao:.*$", f"descricao: '{texto}'", conteudo, count=1, flags=re.MULTILINE)
    if n == 0:
        print(f"! {nome}: campo descricao não encontrado")
        falhas += 1
        continue

    caminho.write_text(novo, encoding="utf-8")
    print(f"  {nome:<44} {len(texto):>3} caracteres")

print()
if falhas:
    raise SystemExit(f"{falhas} problema(s) — build não deve prosseguir")
print(f"Todas as descrições dentro de {LIMITE} caracteres.")

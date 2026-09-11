#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Corrige a falta de linha em branco entre o bloco de imports e o conteúdo JSX.

O parser MDX exige que, terminado o bloco de imports, haja uma linha em branco
antes do conteúdo — senão ele tenta interpretar <Aside ...> como JavaScript e
falha com "Unexpected statement in code: only import/exports are supported".
"""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ALVOS = [
    RAIZ / "src" / "content" / "biblioteca",
    RAIZ / "src" / "pages",
]

corrigidos = []
revisados = 0

for base in ALVOS:
    if not base.exists():
        continue
    for arquivo in sorted(base.rglob("*.mdx")):
        revisados += 1
        texto = arquivo.read_text(encoding="utf-8")
        linhas = texto.split("\n")
        saida: list[str] = []
        ultimo_import = -1

        for i, linha in enumerate(linhas):
            saida.append(linha)
            if re.match(r"^import\s+.+from\s+['\"].+['\"];?\s*$", linha):
                ultimo_import = len(saida) - 1

        if ultimo_import == -1:
            continue

        # já há linha em branco depois do último import?
        proximo = ultimo_import + 1
        if proximo < len(saida) and saida[proximo].strip() != "":
            saida.insert(proximo, "")
            arquivo.write_text("\n".join(saida), encoding="utf-8")
            corrigidos.append(str(arquivo.relative_to(RAIZ)))

print(f"Arquivos MDX revisados: {revisados}")
print(f"Corrigidos (linha em branco inserida): {len(corrigidos)}")
for c in corrigidos:
    print(f"  {c}")
if not corrigidos:
    print("  nada a corrigir")

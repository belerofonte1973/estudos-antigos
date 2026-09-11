#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Repointa os imports de constantes de `content.config` para `taxonomia`.

Motivo: `src/content.config.ts` é o módulo de configuração da camada de
conteúdo do Astro — importa `astro:content`. Importá-lo de dentro de um
componente fecha um ciclo em que as constantes chegam indefinidas na
renderização, e o build morre com
`Cannot read properties of undefined (reading 'nome')`.

Só mexe em imports de EIXOS/AREAS/LIVROS. `collections` continua vindo do
content.config, que é o dono legítimo.
"""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent / "src"

PADRAO = re.compile(
    r"^import\s*\{([^}]*)\}\s*from\s*'((?:\.\./)+)content\.config';$",
    re.MULTILINE,
)

CONSTANTES = {"EIXOS", "AREAS", "LIVROS", "rotuloArea", "rotuloLivro", "Eixo", "Area", "Livro"}

mudados: list[str] = []
ignorados: list[str] = []

for arquivo in sorted(RAIZ.rglob("*.astro")) + sorted(RAIZ.rglob("*.ts")) + sorted(
    RAIZ.rglob("*.mdx")
):
    if arquivo.name == "content.config.ts" or arquivo.name == "taxonomia.ts":
        continue
    texto = arquivo.read_text(encoding="utf-8")
    original = texto

    def troca(m: re.Match) -> str:
        nomes = {n.strip().split(" as ")[0].strip() for n in m.group(1).split(",") if n.strip()}
        if not nomes or not nomes <= CONSTANTES:
            ignorados.append(f"{arquivo.relative_to(RAIZ)}: mantido ({', '.join(sorted(nomes))})")
            return m.group(0)
        return f"import {{{m.group(1).strip()}}} from '{m.group(2)}taxonomia';"

    texto = PADRAO.sub(troca, texto)

    if texto != original:
        arquivo.write_text(texto, encoding="utf-8")
        mudados.append(str(arquivo.relative_to(RAIZ)))

print(f"Repointados: {len(mudados)}")
for m in mudados:
    print(f"  {m}")
if ignorados:
    print(f"\nMantidos em content.config: {len(ignorados)}")
    for i in ignorados:
        print(f"  {i}")

# Verificação: nenhum componente pode importar content.config só por constantes
print("\n== Verificação ==")
restantes = []
for arquivo in list(RAIZ.rglob("*.astro")) + list(RAIZ.rglob("*.mdx")):
    texto = arquivo.read_text(encoding="utf-8")
    for m in PADRAO.finditer(texto):
        nomes = {n.strip() for n in m.group(1).split(",") if n.strip()}
        if nomes and nomes <= CONSTANTES:
            restantes.append(f"{arquivo.relative_to(RAIZ)}: {sorted(nomes)}")
if restantes:
    for r in restantes:
        print(f"  ✗ {r}")
    raise SystemExit(1)
print("  ok  nenhum componente importa content.config por constantes")

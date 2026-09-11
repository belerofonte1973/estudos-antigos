#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Etiqueta o conteúdo existente com os eixos do modelo Texto/Contexto/Recepção.

A mudança de fundo: até aqui, `area` carregava sozinha a posição do material,
e por isso a Suméria — que é contexto da Bíblia — estava arquivada dentro de
`biblia`, ao lado do Gênesis. Separar `eixo` de `area` corrige isso sem mover
um único arquivo nem quebrar um único endereço.

Idempotente: rodar duas vezes não duplica campo.
"""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BIB = RAIZ / "src" / "content" / "biblioteca"
ART = RAIZ / "src" / "content" / "artigos"

# dossiê -> (eixo, area, livro)
DOSSIES = {
    "biblia/introducao.mdx": ("nucleo", "biblia", None),
    "biblia/genesis.mdx": ("nucleo", "biblia", "genesis"),
    "biblia/exodo.mdx": ("nucleo", "biblia", "exodo"),
    "biblia/levitico.mdx": ("nucleo", "biblia", "levitico"),
    "biblia/numeros.mdx": ("nucleo", "biblia", "numeros"),
    "biblia/deuteronomio.mdx": ("nucleo", "biblia", "deuteronomio"),
    # a correção principal: Suméria é o mundo em volta do texto, não o texto
    "biblia/sumeria.mdx": ("contexto", "oriente", None),
    "classica/introducao.mdx": ("contexto", "classica", None),
    "pre-historia/pre-historia-humana.mdx": ("contexto", "pre-historia", None),
    "idade-media/introducao.mdx": ("recepcao", "idade-media", None),
}

# artigo -> (eixo, area, livro)
ARTIGOS = {
    "quem-escreveu-o-genesis.md": ("nucleo", "biblia", "genesis"),
    "o-que-e-a-hipotese-documentaria.md": ("nucleo", "biblia", "genesis"),
    "diluvio-da-biblia-vem-de-gilgamesh.md": ("nucleo", "biblia", "genesis"),
    "moises-existiu.md": ("nucleo", "biblia", "exodo"),
    "os-hebreus-foram-escravos-no-egito.md": ("nucleo", "biblia", "exodo"),
    # o artigo da Suméria acompanha o dossiê: contexto
    "quem-foram-os-sumerios.md": ("contexto", "oriente", None),
}

RELATORIO: list[str] = []


def injeta(caminho: Path, eixo: str, area: str, livro: str | None) -> None:
    texto = caminho.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", texto, re.DOTALL)
    if not m:
        RELATORIO.append(f"  ! {caminho.name}: sem frontmatter")
        return

    fm, corpo = m.group(1), m.group(2)
    mudou = []

    # eixo / area — substitui se existir, insere se não
    for chave, valor in (("eixo", eixo), ("area", area)):
        padrao = rf"^{chave}:\s*.*$"
        if re.search(padrao, fm, re.MULTILINE):
            fm = re.sub(padrao, f"{chave}: {valor}", fm, count=1, flags=re.MULTILINE)
        else:
            fm = fm.rstrip("\n") + f"\n{chave}: {valor}\n"
        mudou.append(f"{chave}={valor}")

    if livro:
        if re.search(r"^livro:\s*.*$", fm, re.MULTILINE):
            fm = re.sub(r"^livro:\s*.*$", f"livro: {livro}", fm, count=1, flags=re.MULTILINE)
        else:
            fm = fm.rstrip("\n") + f"\nlivro: {livro}\n"
        mudou.append(f"livro={livro}")

    caminho.write_text(f"---\n{fm}---\n{corpo}", encoding="utf-8")
    RELATORIO.append(f"  {str(caminho.relative_to(RAIZ)):<48} {', '.join(mudou)}")


print("== Biblioteca ==")
for rel, (eixo, area, livro) in DOSSIES.items():
    p = BIB / rel
    if p.exists():
        injeta(p, eixo, area, livro)
    else:
        RELATORIO.append(f"  ! ausente: {rel}")

print("== Artigos ==")
for rel, (eixo, area, livro) in ARTIGOS.items():
    p = ART / rel
    if p.exists():
        injeta(p, eixo, area, livro)
    else:
        RELATORIO.append(f"  ! ausente: {rel}")

for linha in RELATORIO:
    print(linha)

# Verificação: todo arquivo de conteúdo tem eixo e área
print("\n== Verificação ==")
faltando = []
for base in (BIB, ART):
    for f in sorted(base.rglob("*.md*")):
        t = f.read_text(encoding="utf-8")
        for chave in ("eixo:", "area:"):
            if re.search(rf"^{chave}", t, re.MULTILINE) is None:
                faltando.append(f"{f.relative_to(RAIZ)}: sem {chave}")
if faltando:
    for x in faltando:
        print(f"  ✗ {x}")
else:
    print("  ok  todos os arquivos têm eixo e area")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Insere as quatro camadas novas (mitologia comparada, filosofia, teologia-debates,
ciência) nos dossiês bíblicos, a partir dos fragmentos em `_camadas/`.

Por que inserir em vez de pedir ao redator que edite o dossiê: os dossiês têm
20–30 KB de conteúdo já verificado. Um subagente que reescreve o arquivo inteiro
para acrescentar quatro seções pode perder o que estava lá. O fragmento é
escrito à parte, conferido, e só então inserido — e a inserção é feita por script,
determinística e reversível.

O que faz, por dossiê:
  1. confere que o fragmento existe e traz as quatro seções na ordem certa;
  2. recusa-se a inserir duas vezes (idempotente);
  3. renomeia a seção existente `## 9. Lacunas…` para `## 13. Lacunas…`;
  4. insere o fragmento imediatamente antes dela;
  5. guarda backup em `_camadas/_backup/`.

Uso:
    python inserir_camadas.py --seco      # mostra o que faria
    python inserir_camadas.py             # aplica
    python inserir_camadas.py --reverter  # restaura dos backups
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DOSSIES = RAIZ / "src" / "content" / "biblioteca" / "biblia"
FRAGMENTOS = RAIZ / "_camadas"
BACKUP = FRAGMENTOS / "_backup"

SLUGS = [
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

# Títulos exatos que o fragmento precisa trazer, na ordem.
SECOES = [
    "## 9. Mitologia e Literatura Comparada",
    "## 10. Filosofia — as perguntas que o texto levanta",
    "## 11. Teologia — os debates",
    "## 12. Ciência — o que as ciências dizem, e onde não têm competência",
]

# A seção existente que vai ser renumerada de 9 para 13.
RE_LACUNAS = re.compile(r"^##\s*9\.\s*LACUNA", re.IGNORECASE)

MARCA_JA_INSERIDO = "## 9. Mitologia e Literatura Comparada"


def ler(caminho: Path) -> str:
    # newline='' preserva os terminadores originais (os arquivos são CRLF)
    with caminho.open("r", encoding="utf-8", newline="") as f:
        return f.read()


def escrever(caminho: Path, texto: str) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as f:
        f.write(texto)


def validar_fragmento(texto: str, slug: str) -> list[str]:
    """Devolve a lista de problemas encontrados no fragmento."""
    problemas: list[str] = []
    for titulo in SECOES:
        if titulo not in texto:
            problemas.append(f"falta a seção: {titulo}")

    posicoes = [texto.find(t) for t in SECOES]
    if all(p >= 0 for p in posicoes) and posicoes != sorted(posicoes):
        problemas.append("as quatro seções não estão na ordem esperada")

    if texto.lstrip().startswith("---"):
        problemas.append("o fragmento traz frontmatter — não deve ter")

    if "import " in texto:
        problemas.append("o fragmento traz import — não deve ter")

    # MDX: '<' solto na prosa quebra a compilação. Aceitamos apenas as tags
    # que o projeto usa de fato em conteúdo.
    for m in re.finditer(r"<(?!/?(?:Aside|Card|CardGrid|LinkButton|span|br|em|strong)\b)[^\s>]", texto):
        linha = texto[: m.start()].count("\n") + 1
        problemas.append(f"possível '<' solto na prosa (linha {linha})")

    if len(texto.encode("utf-8")) < 6000:
        problemas.append(
            f"curto demais ({len(texto.encode('utf-8'))} bytes) — esperado 10–16 KB"
        )

    return problemas


def inserir(slug: str, seco: bool) -> tuple[bool, str]:
    dossie = DOSSIES / f"{slug}.mdx"
    fragmento = FRAGMENTOS / f"{slug}.md"

    if not dossie.exists():
        return False, "dossiê ausente"
    if not fragmento.exists():
        return False, "fragmento ausente (o redator não entregou)"

    frag = ler(fragmento)
    problemas = validar_fragmento(frag, slug)
    if problemas:
        return False, "fragmento reprovado: " + "; ".join(problemas)

    corpo = ler(dossie)

    if MARCA_JA_INSERIDO in corpo:
        return True, "já inserido antes (nada a fazer)"

    linhas = corpo.splitlines(keepends=True)
    idx = next((i for i, l in enumerate(linhas) if RE_LACUNAS.match(l)), None)
    if idx is None:
        return False, "não achei a seção '## 9. Lacunas…' para renumerar"

    # renumera 9 -> 13 preservando o texto do título
    titulo_antigo = linhas[idx].rstrip("\r\n")
    titulo_novo = re.sub(r"^(##\s*)9(\s*\.)", r"\g<1>13\g<2>", titulo_antigo, count=1)
    if titulo_novo == titulo_antigo:
        return False, f"não consegui renumerar: {titulo_antigo!r}"

    frag_limpo = frag.strip() + "\n\n"
    if not seco:
        BACKUP.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dossie, BACKUP / f"{slug}.mdx.bak")

    novas = linhas[:idx] + [frag_limpo, titulo_novo + "\n"] + linhas[idx + 1 :]
    if not seco:
        escrever(dossie, "".join(novas))

    return True, f"inserido antes de '{titulo_antigo}' (renumerada para 13)"


def reverter() -> int:
    if not BACKUP.exists():
        print("nenhum backup encontrado.")
        return 1
    n = 0
    for bak in sorted(BACKUP.glob("*.mdx.bak")):
        destino = DOSSIES / bak.name[: -len(".bak")]
        shutil.copy2(bak, destino)
        print(f"  restaurado {destino.name}")
        n += 1
    print(f"\n{n} dossiê(s) restaurado(s).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true", help="não escreve nada")
    ap.add_argument("--reverter", action="store_true", help="restaura dos backups")
    args = ap.parse_args()

    if args.reverter:
        return reverter()

    print(f"== Inserção das quatro camadas{' (SIMULAÇÃO)' if args.seco else ''} ==\n")
    ok = pulados = falhas = 0
    for slug in SLUGS:
        sucesso, msg = inserir(slug, args.seco)
        if sucesso:
            if "já inserido" in msg:
                pulados += 1
                print(f"  --  {slug:12s} {msg}")
            else:
                ok += 1
                print(f"  ok  {slug:12s} {msg}")
        else:
            falhas += 1
            print(f"  FALHA  {slug:12s} {msg}")

    print(f"\n{ok} inserido(s) · {pulados} já estava(m) · {falhas} falha(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())

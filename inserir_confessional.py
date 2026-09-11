#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Insere a subseção de comentaristas por esfera confessional no FIM da seção 11
(Teologia) de cada dossiê bíblico.

Por que uma subseção e não uma seção nova: a exigência é a dimensão confessional
da teologia, e a própria receita (`references/comentaristas-por-esfera-confessional.md`)
diz que ela "é a seção 11 levada a sério". Então entra como `### 11.1` dentro da
11, antes do `## 12. Ciência`. Vantagem prática: não renumera nada de novo.

Mesmo desenho de segurança do `inserir_camadas.py`: fragmento escrito à parte,
validado antes de entrar, backup por dossiê, idempotente e reversível.

Uso:
    python inserir_confessional.py --seco
    python inserir_confessional.py
    python inserir_confessional.py --reverter
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

CABECALHO = "### 11.1. Comentaristas por esfera confessional"
ANCORA_INSERCAO = re.compile(r"^##\s*12\.\s*Ci", re.IGNORECASE)

# As cinco esferas são conferidas no verificador (verificar_camadas.py); aqui só
# se valida a forma do fragmento, para não duplicar a régua em dois lugares.


def ler(caminho: Path) -> str:
    with caminho.open("r", encoding="utf-8", newline="") as f:
        return f.read()


def escrever(caminho: Path, texto: str) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as f:
        f.write(texto)


def validar(texto: str) -> list[str]:
    problemas: list[str] = []

    if not texto.lstrip().startswith(CABECALHO):
        problemas.append(f"não começa com o cabeçalho exato: {CABECALHO!r}")

    if len(re.findall(r"^###\s*11\.1", texto, re.M)) != 1:
        problemas.append("deve haver exatamente um cabeçalho '### 11.1'")

    # um fragmento de subseção não pode trazer cabeçalho de nível 2
    if re.search(r"^##\s", texto, re.M):
        problemas.append("traz cabeçalho '##' — deve ser só '### 11.1'")

    if texto.lstrip().startswith("---"):
        problemas.append("traz frontmatter — não deve ter")

    if re.search(r"^import ", texto, re.M):
        problemas.append("traz import — não deve ter")

    for m in re.finditer(
        r"<(?!/?(?:Aside|Card|CardGrid|LinkButton|span|br|em|strong)\b)[^\s>]", texto
    ):
        linha = texto[: m.start()].count("\n") + 1
        problemas.append(f"possível '<' solto na prosa (linha {linha})")

    tam = len(texto.encode("utf-8"))
    if tam < 4000:
        problemas.append(f"curto demais ({tam} bytes) — esperado 6–10 KB")

    return problemas


def inserir(slug: str, seco: bool) -> tuple[bool, str]:
    dossie = DOSSIES / f"{slug}.mdx"
    fragmento = FRAGMENTOS / f"{slug}-confessional.md"

    if not dossie.exists():
        return False, "dossiê ausente"
    if not fragmento.exists():
        return False, "fragmento ausente (o redator não entregou)"

    frag = ler(fragmento)
    problemas = validar(frag)
    if problemas:
        return False, "fragmento reprovado: " + "; ".join(problemas)

    corpo = ler(dossie)

    if CABECALHO in corpo:
        return True, "já inserido antes (nada a fazer)"

    linhas = corpo.splitlines(keepends=True)
    idx = next((i for i, l in enumerate(linhas) if ANCORA_INSERCAO.match(l)), None)
    if idx is None:
        return False, "não achei a seção '## 12. Ciência' para ancorar"

    frag_limpo = frag.strip() + "\n\n"
    if not seco:
        BACKUP.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dossie, BACKUP / f"{slug}.mdx.pre-confessional")

    novas = linhas[:idx] + [frag_limpo] + linhas[idx:]
    if not seco:
        escrever(dossie, "".join(novas))

    return True, f"inserido antes de '{linhas[idx].strip()}'"


def reverter() -> int:
    baks = sorted(BACKUP.glob("*.mdx.pre-confessional")) if BACKUP.exists() else []
    if not baks:
        print("nenhum backup 'pre-confessional' encontrado.")
        return 1
    for bak in baks:
        destino = DOSSIES / bak.name.replace(".pre-confessional", "")
        shutil.copy2(bak, destino)
        print(f"  restaurado {destino.name}")
    print(f"\n{len(baks)} dossiê(s) restaurado(s).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true", help="não escreve nada")
    ap.add_argument("--reverter", action="store_true", help="restaura dos backups")
    args = ap.parse_args()

    if args.reverter:
        return reverter()

    print(f"== Comentaristas por esfera{' (SIMULAÇÃO)' if args.seco else ''} ==\n")
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

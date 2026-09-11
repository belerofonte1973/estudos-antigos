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

CABECALHO_BASE = "Comentaristas por esfera confessional"
CABECALHO_ESCRITO = f"### 11.1. {CABECALHO_BASE}"
ANCORA_INSERCAO = re.compile(r"^##\s*12\.\s*Ci", re.IGNORECASE)

# Numeração das subseções: NÃO é fixa. Deuteronômio já usa `### 11.1` a `11.8` e
# Josué `11.1` a `11.4` — inserir `11.1` colidiria. O script descobre o próximo
# número livre na seção 11 e renumera o cabeçalho do fragmento ao inserir.
RE_SUBSECAO_11 = re.compile(r"^###\s*11\.(\d+)", re.MULTILINE)
RE_CABECALHO_FRAG = re.compile(r"^###\s*11\.\d+\.\s*" + CABECALHO_BASE, re.MULTILINE)


def proximo_numero(corpo: str) -> int:
    """Próximo número livre em `### 11.N` dentro da seção 11."""
    m = re.search(r"^##\s*11\..*?(?=^##\s*12\.)", corpo, re.MULTILINE | re.DOTALL)
    trecho = m.group(0) if m else corpo
    existentes = [int(n) for n in RE_SUBSECAO_11.findall(trecho)]
    return max(existentes) + 1 if existentes else 1

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

    if not texto.lstrip().startswith(CABECALHO_ESCRITO):
        problemas.append(f"não começa com o cabeçalho exato: {CABECALHO_ESCRITO!r}")

    if len(RE_CABECALHO_FRAG.findall(texto)) != 1:
        problemas.append("deve haver exatamente um cabeçalho de comentaristas")

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

    if CABECALHO_BASE in corpo:
        return True, "já inserido antes (nada a fazer)"

    linhas = corpo.splitlines(keepends=True)
    idx = next((i for i, l in enumerate(linhas) if ANCORA_INSERCAO.match(l)), None)
    if idx is None:
        return False, "não achei a seção '## 12. Ciência' para ancorar"

    # renumera o cabeçalho do fragmento para o próximo número livre da seção 11
    n = proximo_numero(corpo)
    frag_num = RE_CABECALHO_FRAG.sub(
        f"### 11.{n}. {CABECALHO_BASE}", frag, count=1
    )
    nota = f" (renumerado para 11.{n})" if n != 1 else ""

    frag_limpo = frag_num.strip() + "\n\n"
    if not seco:
        BACKUP.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dossie, BACKUP / f"{slug}.mdx.pre-confessional")

    novas = linhas[:idx] + [frag_limpo] + linhas[idx:]
    if not seco:
        escrever(dossie, "".join(novas))

    return True, f"inserido como 11.{n} antes de '{linhas[idx].strip()}'{nota}"


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

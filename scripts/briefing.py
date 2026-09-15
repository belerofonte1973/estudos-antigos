#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
briefing.py — monta o briefing de UM dossiê para delegação, do disco.

Por que existe: o briefing do redator era composto à mão em cada lote e incluía
`skill_view('pesquisador-bibliografico')` — 142 kB de skill (≈36 mil tokens)
reenviados em TODOS os turnos de cada subagente. Aqui o briefing sai do
`_briefings/nucleo-dossie.md` (≈4,4 kB) + o bloco específico do livro, e é isso
que vai no `context` da delegação. O pai não precisa escrever nem carregar nada.

Uso:
    python scripts/briefing.py habacuque            # briefing completo
    python scripts/briefing.py habacuque --curto    # só o bloco específico
    python scripts/briefing.py --proximo            # livro da taxonomia sem dossiê
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BIBLIA = RAIZ / "src" / "content" / "biblioteca" / "biblia"
NUCLEO = RAIZ / "_briefings" / "nucleo-dossie.md"
EXTENSOES = ("mdx", "md")


def dossies() -> dict[str, pathlib.Path]:
    return {p.stem: p for ext in EXTENSOES for p in BIBLIA.glob(f"*.{ext}")}


def frontmatter(p: pathlib.Path) -> dict[str, str]:
    if not p.exists():
        return {}
    m = re.match(r"---\n(.*?)\n---", p.read_text(encoding="utf-8"), re.S)
    return dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M)) if m else {}


def proxima_ordem() -> int:
    ordens = []
    for p in dossies().values():
        v = frontmatter(p).get("ordem", "")
        if v.strip().isdigit():
            ordens.append(int(v.strip()))
    return (max(ordens) + 1) if ordens else 1


def irmaos(n: int = 3) -> list[tuple[str, str]]:
    """Dossiês mais recentes do acervo — o modelo de forma a ser seguido."""
    itens = sorted(BIBLIA.glob("*.mdx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [(p.stem, frontmatter(p).get("title", "").strip("'")[:52]) for p in itens[:n]]


def bloco(slug: str) -> str:
    p = dossies().get(slug)
    fm = frontmatter(p) if p else {}
    ordem = fm.get("ordem", str(proxima_ordem()))
    existe = "sim (revisão)" if p else "não (dossiê novo)"
    irm = irmaos()
    linhas = [
        f"## Específico deste dossiê — {slug}",
        "",
        f"- Arquivo alvo: `src/content/biblioteca/biblia/{slug}.mdx` — existe: {existe}",
        f"- Frontmatter: area: biblia · eixo: nucleo · ordem: {ordem} · livro: {slug}",
        "- Espelhe a FORMA (não o conteúdo) destes dossiês, os mais recentes:",
    ]
    linhas += [f"  - `{s}.mdx` — {t}" for s, t in irm]
    linhas += [
        "",
        "### Seções H2, nesta ordem",
        "",
        "    1. Lead e Ficha                8. Audiovisual e Games",
        "    2. Contexto e Autoria          9. Mitologia e Literatura Comparada",
        "    3. Estrutura                  10. Filosofia",
        "    4. Conteúdos-chave com Debate 11. Teologia (com ### 11.1)",
        "    5. Temas                      12. Ciência",
        "    6. Recepção                   13. Lacunas e Correções de Atribuição",
        "    7. Traduções PT e Comentários PT     + ## Bibliografia-âncora",
        "",
        "### Antes de devolver",
        "",
        f"    python validar_dossie.py {slug}",
        "",
    ]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--curto", action="store_true", help="só o bloco específico")
    ap.add_argument("--proximo", action="store_true", help="lista livros da taxonomia sem dossiê")
    args = ap.parse_args()

    if args.proximo:
        taxonomia = RAIZ / "src" / "taxonomia.ts"
        if not taxonomia.exists():
            sys.exit("sem src/taxonomia.ts")
        slugs = set(re.findall(r"slug:\s*'([a-z0-9\-]+)'", taxonomia.read_text(encoding="utf-8")))
        feitos = set(dossies())
        faltam = sorted(s for s in slugs if s not in feitos)
        print(f"livros na taxonomia sem dossiê: {len(faltam)}")
        for s in faltam:
            print("   ", s)
        return 0

    if not args.slug:
        sys.exit("informe o slug (ou use --proximo)")
    if not args.curto:
        if not NUCLEO.exists():
            sys.exit(f"núcleo ausente: {NUCLEO}")
        print("<!-- Briefing de dossiê — Estudos Antigos (núcleo + específico do livro) -->")
        print(NUCLEO.read_text(encoding="utf-8").rstrip())
        print()
    print(bloco(args.slug))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

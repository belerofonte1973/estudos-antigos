#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Baixa de novo as especificações que ficaram pendentes ou fora do padrão.

Critérios de refazer (o manifesto é a fonte da verdade, não o log):
  * não existe `_imagens/<slug>.json`;
  * o manifesto foi gerado com `largura_max` diferente do padrão atual
    (as primeiras especificações do lote saíram em 1300 px, antes de o padrão
    ser fixado em 950 px);
  * faltam figuras: as especificadas menos as recusadas não batem com as
    gravadas no manifesto (caso da especificação interrompida por HTTP 429).

Uso:
    python scripts/baixar_pendentes.py            # relata e baixa o que falta
    python scripts/baixar_pendentes.py --seco     # só relata
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PADRAO = 950


def motivo(spec_path: pathlib.Path) -> str | None:
    slug = spec_path.stem.replace("espec_", "")
    espec = json.loads(spec_path.read_text(encoding="utf-8"))
    esperadas = len(espec.get("figuras", []))
    manifesto = RAIZ / "_imagens" / f"{slug}.json"
    if not manifesto.exists():
        return f"sem manifesto ({esperadas} figuras especificadas)"
    m = json.loads(manifesto.read_text(encoding="utf-8"))
    if m.get("largura_max") != PADRAO:
        return f"largura {m.get('largura_max')}px (padrão {PADRAO}px)"
    gravadas = len(m.get("figuras", []))
    recusadas = m.get("recusadas", [])
    # recusa de LICENÇA/tamanho é definitiva; recusa de REDE é transitória e
    # precisa de nova tentativa (o upload.wikimedia.org devolve 429 em lote)
    recusa_rede = [r for r in recusadas if isinstance(r, list) and
                   len(r) > 1 and ("429" in r[1] or "rede" in r[1] or "imagem válida" in r[1])]
    if recusa_rede:
        return f"{len(recusa_rede)} recusa(s) de rede a re-tentar"
    if gravadas != esperadas - len(recusadas):
        return f"incompleto: {gravadas} gravadas de {esperadas} especificadas ({len(recusadas)} recusadas)"
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()

    pendentes = []
    for spec in sorted((RAIZ / "_imagens").glob("espec_*.json")):
        m = motivo(spec)
        if m:
            pendentes.append((spec, m))

    if not pendentes:
        print("nada pendente: todos os manifestos estão completos e no padrão")
        return
    print(f"{len(pendentes)} especificação(ões) a refazer:")
    for spec, m in pendentes:
        print(f"  {spec.stem.replace('espec_',''):<18} {m}")
    if args.seco:
        return

    falhas = []
    for spec, _ in pendentes:
        slug = spec.stem.replace("espec_", "")
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "imagens_baixar.py"),
                            "--spec", str(spec)], cwd=RAIZ, capture_output=True,
                           text=True, encoding="utf-8")
        saida = (r.stdout or "") + (r.stderr or "")
        resumo = [l for l in saida.splitlines() if "aceita" in l or "RECUSADA" in l or "erro" in l.lower()]
        print(f"\n=== {slug} ===")
        for l in resumo[:8]:
            print("   ", l.strip())
        if r.returncode != 0:
            falhas.append(slug)
    print(f"\nrefeitas: {len(pendentes) - len(falhas)} · com falha: {len(falhas)} {falhas}")


if __name__ == "__main__":
    main()

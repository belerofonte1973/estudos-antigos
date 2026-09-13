#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
aplicar_figuras.py — aplica em lote os manifestos de figuras nos dossiês.

Para cada slug com manifesto em `_imagens/<slug>.json`:
  1. insere as figuras no `.mdx` (via imagens_inserir, mesma lógica, sem backup
     duplicado quando já existe);
  2. roda `validar_dossie.py` e guarda o resultado.

Ao fim, imprime a tabela: dossiê, figuras inseridas, palavras antes/depois,
falhas e avisos do validador. Nenhum dossiê é dado por bom sem o validador.

Uso:
    python scripts/aplicar_figuras.py                 # todos os manifestos
    python scripts/aplicar_figuras.py juizes genesis  # só alguns
    python scripts/aplicar_figuras.py --seco          # mostra sem gravar
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONTENT = RAIZ / "src" / "content" / "biblioteca" / "biblia"
META = RAIZ / "_imagens"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()

    manifestos = sorted(p for p in META.glob("*.json")
                        if p.name not in ("cache",) and not p.name.startswith("espec_"))
    if args.slugs:
        manifestos = [m for m in manifestos if m.stem in args.slugs]
    if not manifestos:
        sys.exit("nenhum manifesto encontrado")

    linhas, problemas = [], []
    for m in manifestos:
        slug = m.stem
        mdx = CONTENT / f"{slug}.mdx"
        if not mdx.exists():
            problemas.append(f"{slug}: dossiê não existe")
            continue
        dados = json.loads(m.read_text(encoding="utf-8"))
        n_manifesto = len(dados.get("figuras", []))   # já exclui as recusadas
        recusadas = len(dados.get("recusadas", []))
        antes = len(mdx.read_text(encoding="utf-8").split())

        cmd = [sys.executable, str(RAIZ / "scripts" / "imagens_inserir.py"), "--slug", slug]
        if args.seco:
            cmd.append("--seco")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
        saida = (r.stdout or "") + (r.stderr or "")
        inseridas = len(re.findall(r"^   .*\+ /imagens/", saida, re.M))
        nao_inseridas = len(re.findall(r"NÃO INSERIDA", saida))
        texto_mdx = mdx.read_text(encoding="utf-8")
        depois = len(texto_mdx.split())
        figuras_no_mdx = texto_mdx.count("<Figura")

        # validador
        v = subprocess.run([sys.executable, str(RAIZ / "validar_dossie.py"), slug],
                           capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
        vsaida = (v.stdout or "") + (v.stderr or "")
        falhas = len(re.findall(r"\[FALHA", vsaida)) or (1 if "falha(s)" in vsaida and " 0 falha" not in vsaida else 0)
        avisos = len(re.findall(r"· ", vsaida.split("palavras")[-1])) if "aviso" in vsaida else 0
        m_av = re.search(r"(\d+) falha\(s\) · (\d+) aviso\(s\)", vsaida)
        if m_av:
            falhas, avisos = int(m_av.group(1)), int(m_av.group(2))

        linhas.append((slug, n_manifesto, inseridas, figuras_no_mdx, depois - antes, falhas, avisos, recusadas))
        if nao_inseridas:
            problemas.append(f"{slug}: {nao_inseridas} figura(s) sem seção de destino")
        if falhas:
            problemas.append(f"{slug}: {falhas} FALHA(S) no validador")
        if figuras_no_mdx != n_manifesto:
            problemas.append(f"{slug}: manifesto {n_manifesto} × no dossiê {figuras_no_mdx}")

    print(f"\n{'dossiê':<18} {'manif':>5} {'novas':>5} {'no mdx':>6} {'palavras':>9} {'falhas':>6} {'avisos':>6} {'recus':>5}")
    for slug, manif, novas, nomdx, dpal, f, av, rec in linhas:
        print(f"{slug:<18} {manif:>5} {novas:>5} {nomdx:>6} {dpal:>+9} {f:>6} {av:>6} {rec:>5}")

    tot_fig = sum(l[3] for l in linhas)
    tot_rec = sum(l[7] for l in linhas)
    tot_fal = sum(l[5] for l in linhas)
    print(f"\ndossiês: {len(linhas)} · figuras nos dossiês: {tot_fig} · recusadas: {tot_rec} · falhas: {tot_fal}")
    if problemas:
        print(f"\nATENÇÃO ({len(problemas)}):")
        for p in problemas:
            print("   -", p)
        sys.exit(1)
    print("tudo verde")


if __name__ == "__main__":
    main()

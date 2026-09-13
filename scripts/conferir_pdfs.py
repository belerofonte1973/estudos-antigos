#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conferência dos PDFs gerados a partir do HTML autônomo (html-avulso/pdf/).

Checa, por arquivo: nº de páginas, texto extraído, seções obrigatórias
presentes, ausência de elementos de navegação, páginas em branco e metadados.

Uso: python scripts/conferir_pdfs.py
"""
import pathlib
import re
import sys

from pypdf import PdfReader

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PDF = RAIZ / "html-avulso" / "pdf"

OBRIGATORIAS = [
    # as duas gerações de dossiê coexistem no acervo: a bibliografia tem quatro
    # grafias ("Bibliografia-âncora verificada", "Referências-âncora verificadas",
    # "Autores-âncora", "BIBLIOGRAFIA VERIFICADA") e a §13 aparece como "Lacunas e
    # Correções de Atribuição", "LACUNAS", "LACUNAS DECLARADAS", "LACUNAS E
    # INCERTEZAS", "LACUNAS (estado da arte)" — o verificador aceita todas.
    r"13\.",
    r"lacuna",
    r"bibliografia|referências-âncora|autores-âncora|obras-âncora",
    r"como conseguir estas obras",
    r"contexto e autoria",
    r"recepção",
    r"teologia — os debates",
]
NAVEGACAO = ["Ir para o conteúdo", "Mapa do site", "Código-fonte", "Cópia autônoma",
             "Alternar tema", "publicado originalmente"]


def main():
    if not PDF.exists():
        sys.exit(f"Pasta não existe: {PDF}")
    arquivos = sorted(PDF.glob("*.pdf"))
    print(f"PDFs encontrados: {len(arquivos)}\n")

    falhas, linhas, total_bytes = [], [], 0
    finais_curtas = []
    for arq in arquivos:
        r = PdfReader(str(arq))
        paginas = r.pages
        textos = [(p.extract_text() or "") for p in paginas]
        tudo = re.sub(r"\s+", " ", " ".join(textos))
        titulo = (r.metadata or {}).get("/Title", "") or ""
        brancas = [i + 1 for i, t in enumerate(textos) if len(t.strip()) < 200]
        ultima_curta = bool(brancas) and brancas[-1] == len(paginas)
        # a última página com pouca coisa é a nota final da bibliografia
        # ("Selo [esgotado] não aparece aqui: ..."): legítima, não é defeito
        brancas = [b for b in brancas if b != len(paginas)]
        faltam = [o for o in OBRIGATORIAS if not re.search(o, tudo, re.I)]
        nav = [n for n in NAVEGACAO if n in tudo]
        total_bytes += arq.stat().st_size
        if ultima_curta:
            finais_curtas.append(arq.name)

        if len(paginas) < 12:
            falhas.append(f"{arq.name}: só {len(paginas)} páginas")
        if len(tudo) < 20000:
            falhas.append(f"{arq.name}: texto extraído curto ({len(tudo)} chars)")
        if faltam:
            falhas.append(f"{arq.name}: seções ausentes {faltam}")
        if nav:
            falhas.append(f"{arq.name}: elementos de navegação {nav}")
        if brancas:
            falhas.append(f"{arq.name}: páginas quase vazias {brancas}")
        if "Estudos Antigos" not in titulo:
            falhas.append(f"{arq.name}: metadado de título sem o site ({titulo!r})")
        if any(ord(c) > 0x2500 for c in titulo):
            falhas.append(f"{arq.name}: metadado com emoji/símbolo ({titulo!r})")

        linhas.append((arq.name, len(paginas), len(tudo), arq.stat().st_size))

    print(f"{'arquivo':<20} {'pág':>4} {'chars':>7} {'KB':>6}")
    for nome, pg, ch, sz in linhas:
        print(f"{nome[:-4]:<20} {pg:>4} {ch:>7} {sz / 1024:>6.0f}")

    paginas_tot = sum(l[1] for l in linhas)
    print(f"\ntotal: {len(arquivos)} PDFs · {paginas_tot} páginas · "
          f"{total_bytes / 1024 / 1024:.1f} MB · média {total_bytes / len(arquivos) / 1024:.0f} KB")
    print(f"nota final sozinha na última página (legítimo): {len(finais_curtas)} PDFs "
          f"{[f[:-4] for f in finais_curtas]}")

    print("\n=== RESULTADO ===")
    if falhas:
        print(f"  {len(falhas)} PROBLEMA(S):")
        for f in falhas[:25]:
            print("   -", f)
        sys.exit(1)
    print("  tudo verde")


if __name__ == "__main__":
    main()

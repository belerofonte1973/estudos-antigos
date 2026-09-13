#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
comprimir_pdf.py — reduz o peso dos PDFs gerados pelo Chrome headless.

Por quê: ao imprimir com `Page.printToPDF`, o Skia embute cada figura em tamanho
natural e sem compressão com perdas — um dossiê de 9 figuras saiu com 20 MB,
quase tudo em bitmap (as mesmas imagens em WebP somavam 1,8 MB). O texto continua
leve; o peso está nas figuras.

O que faz: reescreve cada imagem embutida como JPEG com perdas, opcionalmente
reduzindo a largura, e grava um PDF novo. As páginas, o texto e a ordem das
figuras não mudam.

Uso:
    python scripts/comprimir_pdf.py html-avulso/pdf/juizes.pdf --teste
    python scripts/comprimir_pdf.py html-avulso/pdf/*.pdf
    python scripts/comprimir_pdf.py html-avulso/pdf/ --largura 950 --qualidade 72
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from PIL import Image
from pypdf import PdfReader, PdfWriter


def comprimir(origem: pathlib.Path, largura: int, qualidade: int, teste: bool = False) -> tuple[int, int, int]:
    """Devolve (bytes_antes, bytes_depois, n_imagens)."""
    leitor = PdfReader(str(origem))
    escritor = PdfWriter(clone_from=str(origem))
    n = 0
    for pagina in escritor.pages:
        for img in pagina.images:
            try:
                pil = img.image
            except Exception:  # noqa: BLE001 — imagem exótica: deixa como está
                continue
            if pil.width > largura:
                pil = pil.resize((largura, round(pil.height * largura / pil.width)), Image.LANCZOS)
            if pil.mode not in ("RGB", "L"):
                pil = pil.convert("RGB")
            try:
                img.replace(pil, quality=qualidade, optimize=True, progressive=True)
                n += 1
            except Exception:  # noqa: BLE001
                continue

    titulo = (leitor.metadata or {}).get("/Title")
    if titulo:
        escritor.add_metadata({"/Title": titulo})

    destino = origem if not teste else origem.with_name("_teste_" + origem.name)
    tmp = destino.with_name(destino.stem + ".tmp.pdf")
    with open(tmp, "wb") as fh:
        escritor.write(fh)
    # segunda passada: normaliza o /Size do trailer (sem ela o pypdf avisa
    # "Object count ... exceeds defined trailer size" e leitores estritos reclamam)
    escritor2 = PdfWriter(clone_from=str(tmp))
    with open(destino, "wb") as fh:
        escritor2.write(fh)
    tmp.unlink(missing_ok=True)
    return origem.stat().st_size, destino.stat().st_size, n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("caminhos", nargs="+", help="arquivo(s) PDF ou pasta")
    ap.add_argument("--largura", type=int, default=950)
    ap.add_argument("--qualidade", type=int, default=72)
    ap.add_argument("--teste", action="store_true", help="grava _teste_<nome>.pdf em vez de substituir")
    args = ap.parse_args()

    alvos: list[pathlib.Path] = []
    for c in args.caminhos:
        p = pathlib.Path(c)
        alvos.extend(sorted(p.glob("*.pdf")) if p.is_dir() else [p])
    alvos = [a for a in alvos if not a.name.startswith("_teste_")]
    if not alvos:
        sys.exit("nenhum PDF encontrado")

    antes_tot = depois_tot = 0
    print(f"{'arquivo':<22} {'antes':>9} {'depois':>9} {'ganho':>7}  imagens")
    for a in alvos:
        antes, depois, n = comprimir(a, args.largura, args.qualidade, args.teste)
        antes_tot += antes
        depois_tot += depois
        ganho = 100 * (1 - depois / antes) if antes else 0
        print(f"{a.name[:-4]:<22} {antes/1024/1024:>8.1f}M {depois/1024/1024:>8.1f}M {ganho:>6.0f}%  {n}")

    if len(alvos) > 1:
        ganho = 100 * (1 - depois_tot / antes_tot) if antes_tot else 0
        print(f"{'TOTAL':<22} {antes_tot/1024/1024:>8.1f}M {depois_tot/1024/1024:>8.1f}M {ganho:>6.0f}%")
    print("\n(o texto e a ordem das páginas não mudam; só as figuras são recomprimidas)")


if __name__ == "__main__":
    main()

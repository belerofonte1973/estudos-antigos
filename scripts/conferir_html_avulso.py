#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conferência do conjunto HTML autônomo (html-avulso/).

Checa, contra o build do Astro (fonte de verdade):
  1. texto visível idêntico ao build em TODAS as páginas
  2. autonomia: CSS inline, sem /_astro/, sem <link> de CSS remanescente
  3. tema claro/escuro presente (botão + script + localStorage)
  4. todo link local (./) tem destino; contagem de links sem par local
  5. fontes locais: todo url(./fonts/...) existe; sem @import remoto
  6. resumo do destino

Uso: python scripts/conferir_html_avulso.py
"""
import html as H
import pathlib
import re
import sys

from gerar_html_avulso import BUILD, DESTINO_PADRAO, mapa_de_rotas, rota_de

OUT = pathlib.Path(DESTINO_PADRAO)
AVISO_RE = re.compile(r"Cópia autônoma do site Estudos Antigos.*?do topo\.", re.S)


def texto(caminho):
    t = caminho.read_text(encoding="utf-8")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", H.unescape(t)).strip()


def main():
    if not OUT.exists():
        sys.exit(f"Destino não existe: {OUT} — rode gerar_html_avulso.py antes.")
    mapa = mapa_de_rotas()
    paginas = {n for n in mapa.values() if n.endswith(".html")}  # só as páginas
    dossies = {
        nome for rota, nome in mapa.items()
        if rota.startswith("/biblioteca/biblia/") and rota != "/biblioteca/biblia/"
    }
    falhas = []

    print("=== 1. INTEGRIDADE DO TEXTO (build x cópia autônoma) ===")
    identicos, divergentes = 0, []
    for p in sorted(BUILD.rglob("*.html")):
        nome = mapa[rota_de(p)]
        a = texto(p)
        b = texto(OUT / nome)
        b = re.sub(r"\s+", " ", AVISO_RE.sub("", b)).strip()
        if a == b:
            identicos += 1
        else:
            divergentes.append(nome)
            if len(divergentes) == 1:
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        print(f"  {nome}: divergência no char {i}")
                        print(f"     build  : ...{a[max(0, i-70):i+70]}")
                        print(f"     gerado : ...{b[max(0, i-70):i+70]}")
                        break
                else:
                    print(f"  {nome}: só diferença de comprimento ({len(a)} x {len(b)})")
    print(f"  idênticos: {identicos}/{len(paginas)}")
    if divergentes:
        falhas.append(f"texto divergente em: {divergentes[:5]}")

    print("\n=== 2. AUTONOMIA (CSS inline, sem /_astro/) ===")
    problemas = []
    for nome in sorted(paginas):
        t = (OUT / nome).read_text(encoding="utf-8")
        if "/_astro/" in t:
            problemas.append(f"{nome}: referencia /_astro/")
        if "<style>" not in t:
            problemas.append(f"{nome}: sem CSS inline")
        if '<link rel="stylesheet"' in t:
            problemas.append(f"{nome}: <link> de CSS remanescente")
    print(f"  páginas: {len(paginas)} · problemas: {len(problemas)}")
    for p in problemas[:5]:
        print("   ", p)
    if problemas:
        falhas.append(f"autonomia: {problemas[:3]}")

    print("\n=== 3. TEMA CLARO/ESCURO ===")
    sem_tema = [
        n for n in sorted(paginas)
        if not all(x in (OUT / n).read_text(encoding="utf-8")
                   for x in ("ea-theme-toggle", "ea-theme", "dataset.theme"))
    ]
    print(f"  páginas com botão + script de tema: {len(paginas) - len(sem_tema)}/{len(paginas)}")
    if sem_tema:
        falhas.append(f"sem alternância de tema: {sem_tema[:5]}")

    print("\n=== 4. LINKS LOCAIS ===")
    quebrados, inertes, externos = [], 0, 0
    for nome in sorted(paginas):
        t = (OUT / nome).read_text(encoding="utf-8")
        inertes += t.count("data-remoto")
        externos += len(re.findall(r'href="https?://', t))
        for alvo in re.findall(r'href="\./([^"#]+)', t):
            if not (OUT / alvo).exists():
                quebrados.append(f"{nome} -> {alvo}")
    print(f"  quebrados: {len(quebrados)}")
    print(f"  links internos sem par local (viraram texto): {inertes}")
    print(f"  links externos preservados: {externos}")
    if quebrados:
        for q in quebrados[:10]:
            print("   ", q)
        falhas.append(f"{len(quebrados)} links quebrados")

    print("\n=== 5. FONTES E RECURSOS LOCAIS ===")
    refs = set()
    for nome in sorted(paginas):
        refs |= set(re.findall(r"url\(\./fonts/([^)]+)\)", (OUT / nome).read_text(encoding="utf-8")))
    existentes = {p.name for p in (OUT / "fonts").glob("*.woff2")} if (OUT / "fonts").exists() else set()
    faltam = sorted(refs - existentes)
    peso = sum(p.stat().st_size for p in (OUT / "fonts").glob("*.woff2")) // 1024
    print(f"  fonts/: {len(existentes)} arquivos ({peso} KB) · referenciados: {len(refs)} · faltando: {len(faltam)}")
    com_import = [n for n in sorted(paginas) if "@import" in (OUT / n).read_text(encoding="utf-8")
                  or "fonts.googleapis" in (OUT / n).read_text(encoding="utf-8")]
    print(f"  páginas que ainda dependem de rede para fonte: {len(com_import)}")
    if faltam:
        falhas.append(f"fontes ausentes: {faltam}")
    if com_import:
        falhas.append(f"@import remoto em {com_import[:3]}")

    print("\n=== 6. DESTINO ===")
    htmls = sorted(paginas)
    extras = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.suffix != ".html")
    print(f"  {OUT}")
    print(f"  páginas .html: {len(htmls)} · outros arquivos: {extras}")
    print(f"  pasta fonts/: {len(existentes)} woff2")
    idx = (OUT / "index.html").read_text(encoding="utf-8")
    links_idx = set(re.findall(r'href="\./([a-z0-9\-]+\.html)', idx))
    faltam_idx = [d for d in sorted(dossies) if d not in links_idx]
    print(f"  index.html linka {len(links_idx)} páginas · dossiês fora do índice: {faltam_idx or 'nenhum'}")

    print("\n=== RESULTADO ===")
    if falhas:
        print(f"  {len(falhas)} PROBLEMA(S):")
        for f in falhas:
            print("   -", f)
        sys.exit(1)
    print("  tudo verde")


if __name__ == "__main__":
    main()

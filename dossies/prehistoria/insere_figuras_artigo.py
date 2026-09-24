#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""insere_figuras_artigo.py — insere figuras em artigo .md."""
import pathlib
AQUI = pathlib.Path(__file__).resolve().parent.parent.parent
ARTIGO = AQUI / "src/content/artigos/quando-comeca-a-historia-humana.md"
BAK = ARTIGO.with_suffix(".md.bak-figuras")

# mapeia texto do cabeçalho -> (alt, src)
ALVO = {
    "O crânio de Jebel Irhoud": (
        "Crânio de Jebel Irhoud (Homo sapiens)",
        "/imagens/pre-historia/05-cranio-de-jebel-irhoud-homo-sapiens.webp",
    ),
    "Não houve substituição pura": (
        "Reconstrução de neandertal",
        "/imagens/pre-historia/06-reconstrucao-de-neandertal.webp",
    ),
    "Comportamento simbólico": (
        "Cavalo chinês de Lascaux",
        "/imagens/pre-historia/09-cavalo-chines-de-lascaux.webp",
    ),
    "O Neolítico e o sedentarismo": (
        "Pilares monumentais de Göbekli Tepe",
        "/imagens/pre-historia/14-pilares-monumentais-de-gobekli-tepe.webp",
    ),
    "Quatro coisas": (
        "Pegadas de Laetoli (réplica)",
        "/imagens/pre-historia/11-pegadas-de-laetoli-replica.webp",
    ),
}

texto = ARTIGO.read_text(encoding="utf-8")
linhas = texto.split("\n")
novo, inseridas = [], 0

for linha in linhas:
    novo.append(linha)
    if linha.strip().startswith("## "):
        for trecho, (alt, src) in ALVO.items():
            if trecho in linha:
                novo.append(f"\n![{alt}]({src})\n")
                inseridas += 1
                break

novo_texto = "\n".join(novo)
if novo_texto != texto:
    if not BAK.exists():
        BAK.write_text(texto, encoding="utf-8")
    ARTIGO.write_text(novo_texto, encoding="utf-8")
    print(f"{inseridas} figuras inseridas")
    print(f"backup: {BAK}")
else:
    print("nada a fazer")

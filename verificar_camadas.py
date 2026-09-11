#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica se as quatro camadas novas realmente entraram nos nove dossiês
bíblicos — e se entraram com conteúdo, não com enchimento.

Não basta a seção existir. A exigência do skill é **argumento com autor, não
menção de tema**: cada camada precisa nomear autores extra-bíblicos. Então este
verificador conta nomes, não palavras.

Uso:  python verificar_camadas.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist" / "biblioteca" / "biblia"

DOSSIES = [
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

# Título da seção renderizada → (mínimo de palavras, quantos nomes exigir, nomes)
CAMADAS: dict[str, tuple[int, int, list[str]]] = {
    "Mitologia e Literatura Comparada": (
        250,
        2,
        [
            "Enūma", "Enuma", "Atrahasis", "Atra-hasis", "Gilgamesh", "Ugarit",
            "Baal", "Hammurabi", "Amenemope", "Hesíodo", "Hesiodo", "Corão",
            "Heródoto", "Sargão", "Sargao", "Mesha", "Senaqueribe", "Menfita",
            "Deir Alla", "necro", "Katumuwa", "Sfire", "Rank", "Burkert",
            "Girard", "Adapa", "Dilmun", "Ziusudra", "Keret", "Aqhat",
            "Siloé", "Siloé", "obelisco", "prisma", "epônimo", "eponimo",
        ],
    ),
    "Filosofia": (
        250,
        2,
        [
            "Espinosa", "Spinoza", "Leibniz", "Kant", "Mackie", "Rowe", "Hume",
            "Kierkegaard", "Agostinho", "Hobbes", "Douglas", "Girard", "Freud",
            "Maimônides", "Maimonides", "Trible", "Plantinga", "Draper",
            "Eutífron", "Auerbach", "Walzer", "Niditch", "Anselmo", "Platão",
            "Platao", "Voltaire", "Jonas", "Levinas", "Buber", "Ricoeur",
            "Gadamer", "Bal", "Kermode", "Alter", "Assmann", "Prior",
            "Sugirtharajah", "Said", "Dostoievski", "Abelardo", "Rost",
        ],
    ),
    "Teologia": (
        250,
        3,
        [
            "von Rad", "Noth", "Childs", "Brueggemann", "Barr", "Levenson",
            "Gutiérrez", "Gutierrez", "Trible", "Sugirtharajah", "Rashi",
            "Corão", "Maimônides", "Cross", "Douglas", "Westermann", "Eichrodt",
            "Frymer-Kensky", "Schüssler", "Cone", "Pixley", "Heschel",
            "Soloveitchik", "Milgrom", "Albertz", "Friedman", "Provan",
            "Sandmel", "Marcion", "Mendelssohn", "Händel", "Handel", "midrash",
            "Talmude", "Seder", "Zabūr", "Sulaymān", "Dāwūd", "tahrīf",
        ],
    ),
    "Ciência": (
        250,
        2,
        [
            "Finkelstein", "Dever", "Whitcomb", "Patterson", "Ussher",
            "Skorecki", "radiocarbono", "Hurvitz", "Kenyon", "Thiele",
            "Milgrom", "Lemaître", "Lemaitre", "Collins", "Darwin", "Rezetko",
            "Ehrensvärd", "Callaway", "Kenyon", "Mazar", "Ben-Tor", "Yadin",
            "Levy", "Reich", "Merneptah", "Walton", "Young", "Hill",
            "genética", "genetica", "estratigrafia", "cronologia",
        ],
    ),
}

# A seção de ciência tem de dizer onde a ciência NÃO decide. Sem isso, ela
# ultrapassa a competência e o dossiê fica tendencioso em algum sentido.
MARCADORES_LIMITE = [
    "não tem competência",
    "nao tem competencia",
    "não decide",
    "nao decide",
    "não pode decidir",
    "não é competência",
    "não compete",
    "fora do alcance",
    "não pode afirmar",
    "não responde",
    "não é uma questão científica",
    "não é questão científica",
    "não cabe à ciência",
    "não cabe a ciência",
    "limite de competência",
    "não alcança",
]


def texto_visivel(html: str) -> str:
    """Remove tags e normaliza entidades, mantendo o texto legível."""
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = (
        html.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
    )
    return re.sub(r"\s+", " ", html)


def recortar_secao(texto: str, titulo: str, proximos: list[str]) -> str:
    """
    Recorta o corpo de uma seção: do título até o próximo título conhecido.
    Evita o erro de contar palavras de seções vizinhas.
    """
    m = re.search(re.escape(titulo), texto)
    if not m:
        return ""
    inicio = m.end()
    fim = len(texto)
    for p in proximos:
        if p == titulo:
            continue
        m2 = re.search(re.escape(p), texto[inicio:])
        if m2:
            fim = min(fim, inicio + m2.start())
    return texto[inicio:fim]


def main() -> int:
    falhas: list[str] = []
    ok = 0

    titulos = list(CAMADAS.keys())
    # ordem real das seções no dossiê, para o recorte
    ordem = titulos + ["Lacunas", "LACUNAS", "Bibliografia", "BIBLIOGRAFIA",
                       "Autores-âncora", "Referências-âncora", "Anexo", "ANEXO",
                       "Relatório", "RELATÓRIO"]

    print("== Verificação das quatro camadas nos nove dossiês ==\n")

    for slug in DOSSIES:
        pagina = DIST / slug / "index.html"
        if not pagina.exists():
            falhas.append(f"{slug}: página não construída em {pagina}")
            continue
        texto = texto_visivel(pagina.read_text(encoding="utf-8", errors="replace"))
        print(f"--- {slug}")

        for titulo, (min_palavras, min_nomes, nomes) in CAMADAS.items():
            if titulo not in texto:
                falhas.append(f"{slug}: falta a seção {titulo}")
                print(f"    FALHA  seção ausente: {titulo}")
                continue

            corpo = recortar_secao(texto, titulo, ordem)
            palavras = len(corpo.split())

            if palavras < min_palavras:
                falhas.append(
                    f"{slug}/{titulo}: só {palavras} palavras (mínimo {min_palavras})"
                )

            achados = sorted({n for n in nomes if n in corpo})
            if len(achados) < min_nomes:
                falhas.append(
                    f"{slug}/{titulo}: só {len(achados)} autor(es) nomeado(s) "
                    f"({', '.join(achados) or 'nenhum'}) — mínimo {min_nomes}"
                )

            marca = "ok " if palavras >= min_palavras and len(achados) >= min_nomes else "FALHA"
            if marca == "ok ":
                ok += 1
            print(
                f"    {marca} {titulo[:34]:34s} {palavras:5d} palavras · "
                f"{len(achados):2d} nomes"
            )

        # o limite de competência é exigido só na seção de ciência
        corpo_ci = recortar_secao(texto, "Ciência", ordem)
        if corpo_ci and not any(m.lower() in corpo_ci.lower() for m in MARCADORES_LIMITE):
            falhas.append(
                f"{slug}: a seção Ciência não declara onde a ciência não tem competência"
            )
            print("    FALHA  ciência não declara o limite de competência")

    print()
    if falhas:
        for f in falhas:
            print(f"  FALHA  {f}")
        print(f"\n{len(falhas)} falha(s) · {ok} camada(s) aprovada(s)")
        return 1

    print(f"OK — 9 dossiês × 4 camadas: {ok} camadas aprovadas, nenhuma falha.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

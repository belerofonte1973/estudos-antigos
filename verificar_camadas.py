#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica se as quatro camadas novas realmente entraram nos nove dossiês
bíblicos — e se entraram com conteúdo, não com enchimento.

Não basta a seção existir. A exigência do skill é **argumento com autor, não
menção de tema**: cada camada precisa nomear autores extra-bíblicos. Então este
verificador conta nomes, não palavras.

A extração da seção opera sobre os elementos `<h2>` do HTML, e não sobre o texto
plano. Isso importa: o sumário lateral repete os títulos das seções, e ancorar na
primeira ocorrência do título em texto plano faz o recorte começar no sumário e
terminar antes do corpo — o que produzia falso negativo em "Teologia" e
"Mitologia" (11-set-2026).

Uso:  python verificar_camadas.py
"""
from __future__ import annotations

import html as htmlmod
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

# Número da seção → (título, mínimo de palavras, quantos nomes exigir, nomes)
CAMADAS: dict[str, tuple[str, int, int, list[str]]] = {
    "9": (
        "Mitologia e Literatura Comparada",
        250,
        2,
        [
            "Enūma", "Enuma", "Atrahasis", "Atra-hasis", "Gilgamesh", "Ugarit",
            "Baal", "Hammurabi", "Hamurabi", "Amenemope", "Hesíodo", "Hesiodo",
            "Corão", "Heródoto", "Sargão", "Sargao", "Mesha", "Mesa",
            "Senaqueribe", "Menfita", "Deir Alla", "necro", "Katumuwa",
            "Kuttamuwa", "Sefire", "Sfire", "Rank", "Burkert", "Girard",
            "Adapa", "Dilmun", "Ziusudra", "Keret", "Aqhat", "Siloé", "Siloé",
            "obelisco", "prisma", "epônimo", "eponimo", "asakku", "herem",
            "Younger", "Milgrom", "Mendenhall", "kuppuru", "Akitu", "Šurpu",
            "Ebal", "Zincirli", "Idrimi", "Younger", "Niditch", "Aten",
            "Akhenaton", "mīs pî", "Nehushtan", "Balaão", "Biléão",
            "Sêneca", "Roma", "Eneida", "Filão", "Massoretic",
        ],
    ),
    "10": (
        "Filosofia",
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
            "Levinson", "Nietzsche", "Russell", "Feuerbach", "Marx",
            "Jaspers", "Maimônides", "Aristóteles", "Eutífron", "Locke",
            "Madison", "Rawls", "Ehrman", "Avalos",
        ],
    ),
    "11": (
        "Teologia",
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
            "Ismael", "Isaque", "Agostinho", "Calvino", "Barth", "Belarmino",
            "RnB", "Nostra Aetate", "Basílio", "Crisóstomo", "Orígenes",
            "Rabano", "Beda", "Aquino", "Lutero", "Calvino", "Wesley",
            "Cranmer", "Teodoreto", "Cirilo", "Mesters", "Boff",
        ],
    ),
    "12": (
        "Ciência",
        250,
        2,
        [
            "Finkelstein", "Dever", "Whitcomb", "Patterson", "Ussher",
            "Skorecki", "radiocarbono", "Hurvitz", "Kenyon", "Thiele",
            "Milgrom", "Lemaître", "Lemaitre", "Collins", "Darwin", "Rezetko",
            "Ehrensvärd", "Callaway", "Mazar", "Ben-Tor", "Yadin", "Yadin",
            "Levy", "Reich", "Merneptah", "Walton", "Young", "Hill",
            "genética", "genetica", "estratigrafia", "cronologia", "14C",
            "calibração", "Hazor", "Láquis", "Lachish", "Arad", "Timna",
            "Siloé", "Senaqueribe", "Herzog", "Faust", "Feldman", "Regev",
            "Ben-Yosef", "ben-Yosef", "Höflmayer", "Hoflmayer",
        ],
    ),
}

# A seção de ciência tem de dizer onde a ciência NÃO decide. Sem isso ela
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
    "não tem o que dizer",
    "não decide nada",
]


def texto_visivel(fragmento_html: str) -> str:
    """Remove tags e normaliza entidades, mantendo o texto legível."""
    fragmento_html = re.sub(
        r"<(script|style)[^>]*>.*?</\1>", " ", fragmento_html, flags=re.S | re.I
    )
    sem_tags = re.sub(r"<[^>]+>", " ", fragmento_html)
    return re.sub(r"\s+", " ", htmlmod.unescape(sem_tags)).strip()


def secoes_por_h2(html: str) -> dict[str, str]:
    """
    Devolve {texto do h2: corpo visível até o próximo h2}.

    Operar nos <h2> é o que evita o sumário lateral: as entradas do sumário são
    âncoras, não cabeçalhos, então nunca entram neste mapa.
    """
    matches = list(re.finditer(r"<h2\b[^>]*>(.*?)</h2>", html, re.S))
    mapa: dict[str, str] = {}
    for i, m in enumerate(matches):
        titulo = texto_visivel(m.group(1))
        inicio = m.end()
        fim = matches[i + 1].start() if i + 1 < len(matches) else len(html)
        if titulo:
            mapa[titulo] = texto_visivel(html[inicio:fim])
    return mapa


def achar_secao(mapa: dict[str, str], numero: str, titulo: str) -> str | None:
    """Localiza a seção pelo cabeçalho numerado, tolerando variação de título."""
    alvo = re.compile(rf"^{re.escape(numero)}\.\s*{re.escape(titulo[:12])}", re.I)
    for cabeçalho, corpo in mapa.items():
        if alvo.match(cabeçalho):
            return corpo
    return None


def main() -> int:
    falhas: list[str] = []
    ok = 0

    print("== Verificação das quatro camadas nos nove dossiês ==\n")

    for slug in DOSSIES:
        pagina = DIST / slug / "index.html"
        if not pagina.exists():
            falhas.append(f"{slug}: página não construída em {pagina}")
            continue

        html = pagina.read_text(encoding="utf-8", errors="replace")
        mapa = secoes_por_h2(html)
        print(f"--- {slug}")

        for numero, (titulo, min_palavras, min_nomes, nomes) in CAMADAS.items():
            corpo = achar_secao(mapa, numero, titulo)
            if corpo is None:
                falhas.append(f"{slug}: falta a seção {numero}. {titulo}")
                print(f"    FALHA  seção ausente: {numero}. {titulo}")
                continue

            palavras = len(corpo.split())
            achados = sorted({n for n in nomes if n in corpo})

            bom = palavras >= min_palavras and len(achados) >= min_nomes
            if palavras < min_palavras:
                falhas.append(
                    f"{slug}/{titulo}: só {palavras} palavras (mínimo {min_palavras})"
                )
            if len(achados) < min_nomes:
                falhas.append(
                    f"{slug}/{titulo}: só {len(achados)} autor(es) nomeado(s) "
                    f"({', '.join(achados) or 'nenhum'}) — mínimo {min_nomes}"
                )
            if bom:
                ok += 1
            print(
                f"    {'ok ' if bom else 'FALHA'} {titulo[:34]:34s} "
                f"{palavras:5d} palavras · {len(achados):2d} nomes"
            )

        # o limite de competência é exigido só na seção de ciência
        corpo_ci = achar_secao(mapa, "12", "Ciência")
        if corpo_ci is not None and not any(
            m.lower() in corpo_ci.lower() for m in MARCADORES_LIMITE
        ):
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
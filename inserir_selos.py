#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Insere a seção "Como conseguir estas obras" no fim da bibliografia de cada dossiê.

Por que uma TABELA consolidada e não um selo colado em cada linha da bibliografia:
as bibliografias são prosa longa, com o link de acesso no meio da frase. Cravar
um selo por linha exigiria reescrever nove arquivos grandes que já estão
verificados — exatamente o que a skill proíbe. A tabela é aditiva: não toca em
uma linha do texto existente e ainda dá melhor leitura, porque ordena as obras
por acessibilidade (o que o leitor lê hoje primeiro) em vez de por ordem de
citação.

Ordenação: [livre] -> [empréstimo] -> [biblioteca] -> [compra] -> [esgotado].
O leitor que não tem dinheiro nem biblioteca lê a tabela de cima para baixo e
sabe até onde consegue ir.

Uso:
    python inserir_selos.py --seco      # relatório, não escreve
    python inserir_selos.py             # aplica (backup .bak por arquivo)
    python inserir_selos.py --reverter  # desfaz a inserção
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DOSSIES = RAIZ / "src" / "content" / "biblioteca" / "biblia"
JSONS = RAIZ / "_selos"

MARCADOR = "### Como conseguir estas obras"
IMPORT = "import SeloAcesso from '../../../components/SeloAcesso.astro';"

ORDEM = ["livre", "emprestimo", "biblioteca", "compra", "esgotado"]

NOME_DOMINIO = {
    "archive.org": "Internet Archive",
    "openlibrary.org": "Open Library",
    "jstor.org": "JSTOR",
    "books.google.com": "Google Books",
    "sacred-texts.com": "Sacred Texts",
    "rosetta.reltech.org": "Rosetta (PDF)",
    "academia.edu": "Academia.edu",
    "brill.com": "Brill",
    "degruyterbrill.com": "De Gruyter/Brill",
}


def limpar_rotulo(r: str) -> str:
    """
    Encurta o rótulo para a tabela.

    A armadilha que isto evita: cortar em "Palavra:" parece funcionar ("OL:
    <url>", "JSTOR: <url>"), mas decepa títulos que legitimamente têm dois-pontos
    — "Boling, Judges: Introduction, Translation, and Commentary (Anchor Bible
    6A; Doubleday, 1975)" virava só "Boling,". O corte certo é no URL: a
    referência vem antes, o link vem depois.
    """
    r = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", r)  # link markdown -> texto
    r = r.replace("**", "").replace("*", "")
    r = re.sub(r"\[[VW—][^\]]*\]", "", r)

    # 1. corta no primeiro URL, com ou sem esquema
    r = re.split(r"\s*(?:https?://|www\.)", r)[0]
    # 2. sobra um rótulo de site pendurado ("OL:", "JSTOR:", "Internet Archive:",
    #    "Bible Archaeology:"). Duas sutilezas, ambas por defeito observado:
    #    (a) precisa aceitar MAIS DE UMA palavra — com um só token o corte deixava
    #        "Internet" e "Bible" órfãos no fim da linha;
    #    (b) NÃO pode aceitar ponto dentro do token — com ponto, "Its Interpreters.
    #        JHS:" casava inteiro e a referência virava "…(2 Samuel 7) and".
    #        Ponto final de frase é justamente onde a referência terminou.
    r = re.sub(
        r"\s+[A-Z][A-Za-z&\-]*(?:\s+[A-Z][A-Za-z&\-]*){0,3}:\s*$",
        "",
        r,
    )
    # 3. ou um domínio solto no fim ("archive.org")
    r = re.sub(r"\s+\w[\w-]*\.(?:org|com|net|edu|br|pt|uk|de)\s*$", "", r, flags=re.I)

    r = re.sub(r"\s+", " ", r).strip(" .·—-:,")
    # "Brian Lewis. — The Sargon Legend": a API põe ponto no fim do autor
    r = re.sub(r"\.\s*—\s*", " — ", r)
    # fecha parêntese que ficou pela metade
    while r.count("(") > r.count(")"):
        r = r[: r.rfind("(")].strip(" .—-,")
    return (r[:96] + "…") if len(r) > 96 else r


# Rótulo curto demais para identificar uma obra. Descartado em vez de publicado:
# "Genesis" ou "Bíblia Sagrada" como linha de tabela não dizem AO LEITOR que obra
# é, e uma linha que não informa ocupa o lugar de uma que informaria. As
# traduções PT ficam de fora de propósito — o degrau 1 da escada já dá o texto
# online de graça, com quatro traduções; esta tabela é para as obras acadêmicas.
MIN_ROTULO = 22


def rotulo_dominio(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url)
    if not m:
        return url
    host = m.group(1)
    if host in NOME_DOMINIO:
        return NOME_DOMINIO[host]
    return host[4:] if host.startswith("www.") else host


def escapar(celula: str) -> str:
    """Escape para célula de tabela markdown."""
    return celula.replace("|", r"\|")


def bloco(dados: dict) -> str:
    obras = dados.get("obras", [])
    if not obras:
        return ""

    # Dedup por rótulo limpo; a primeira ocorrência vence.
    vistos: set[str] = set()
    limpas: list[dict] = []
    descartados = 0
    for o in obras:
        r = limpar_rotulo(o["rotulo"])
        if not r or r.lower().startswith("isbn"):
            descartados += 1
            continue
        if len(r) < MIN_ROTULO:
            descartados += 1
            continue
        chave = r.lower()[:40]
        if chave in vistos:
            descartados += 1
            continue
        vistos.add(chave)
        limpas.append({**o, "rotulo": r})

    if descartados:
        print(f"        ({descartados} linha(s) descartada(s): rótulo curto ou repetido)")

    if not limpas:
        return ""

    limpas.sort(key=lambda o: ORDEM.index(o["selo"]) if o["selo"] in ORDEM else 99)

    contagem: dict[str, int] = {}
    for o in limpas:
        contagem[o["selo"]] = contagem.get(o["selo"], 0) + 1
    resumo = " · ".join(f"{contagem[s]} {s}" for s in ORDEM if s in contagem)

    linhas = [
        MARCADOR,
        "",
        "A bibliografia de um site didático não é a de uma tese: cita o que importa "
        "**e o leitor consegue alcançar**. O selo diz por onde — e a tabela está "
        "ordenada por acessibilidade, do que se lê hoje ao que só se compra.",
        "",
        f"*{resumo}.*",
        "",
        "| Obra | Acesso | Onde |",
        "| --- | --- | --- |",
    ]
    for o in limpas:
        onde = f"[{rotulo_dominio(o['url'])}]({o['url']})" if o.get("url") else "—"
        linhas.append(
            f"| {escapar(o['rotulo'])} | <SeloAcesso tipo=\"{o['selo']}\" /> | {onde} |"
        )

    linhas += [
        "",
        "Selo `[esgotado]` não aparece aqui: quando a obra não é alcançável de "
        "nenhuma forma, o texto aponta o substituto acessível ao lado dela.",
        "",
    ]
    return "\n".join(linhas)


def limite_bibliografia(texto: str) -> int | None:
    """Posição onde inserir: fim da seção de bibliografia, antes do próximo '## '."""
    padroes = (
        r"^##\s+Bibliografia[^\n]*\n",
        r"^##\s+BIBLIOGRAFIA[^\n]*\n",
        r"^##\s+Autores-âncora[^\n]*\n",
        r"^##\s+Referências-âncora[^\n]*\n",
        r"^##\s+ANEXO[^\n]*\n",
    )
    for p in padroes:
        m = re.search(p, texto, re.MULTILINE)
        if not m:
            continue
        resto = texto[m.end() :]
        prox = re.search(r"^##\s", resto, re.MULTILINE)
        return m.end() + prox.start() if prox else len(texto)
    return None


def aplicar(slug: str, seco: bool) -> str:
    fonte = DOSSIES / f"{slug}.mdx"
    dados_f = JSONS / f"{slug}.json"
    if not dados_f.exists():
        return "sem JSON"
    texto = fonte.read_text(encoding="utf-8")
    if MARCADOR in texto:
        return "já tem (pulado)"

    b = bloco(json.loads(dados_f.read_text(encoding="utf-8")))
    if not b:
        return "sem obras classificadas"

    pos = limite_bibliografia(texto)
    if pos is None:
        return "sem seção de bibliografia"

    novo = texto[:pos].rstrip() + "\n\n" + b + "\n" + texto[pos:]
    if IMPORT not in novo:
        novo = novo.replace(
            "import Aside from '../../../components/Aside.astro';",
            "import Aside from '../../../components/Aside.astro';\n" + IMPORT,
            1,
        )
    if IMPORT not in novo:
        return "não achei onde pôr o import"

    n_linhas = b.count("\n| ") - 1
    if seco:
        return f"{n_linhas} obras (seco)"

    shutil.copy2(fonte, fonte.with_suffix(".mdx.bak"))
    fonte.write_text(novo, encoding="utf-8")
    return f"{n_linhas} obras inseridas"


def reverter(slug: str) -> str:
    """
    Restaura o backup. Não tento recortar o bloco do texto: reconstruir o estado
    anterior por subtração é mais frágil do que copiar de volta um arquivo que eu
    guardei inteiro antes de mexer.
    """
    fonte = DOSSIES / f"{slug}.mdx"
    bak = fonte.with_suffix(".mdx.bak")
    if not bak.exists():
        return "sem backup"
    shutil.copy2(bak, fonte)
    return "restaurado do backup"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--reverter", action="store_true")
    args = ap.parse_args()

    acao = reverter if args.reverter else lambda s: aplicar(s, args.seco)
    print("== Selo de acesso: seção 'Como conseguir estas obras' ==\n")
    for slug in sorted(p.stem for p in DOSSIES.glob("*.mdx")):
        print(f"--- {slug:14s} {acao(slug)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

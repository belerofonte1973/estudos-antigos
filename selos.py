#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deriva o SELO DE ACESSO de cada obra a partir do que o dossiê já registrou.

A ideia que economiza o trabalho: os dossiês já fizeram a descoberta — as
bibliografias dos cinco mais recentes já trazem o link da Internet Archive, o
da Open Library, o da editora. O selo não é informação nova a pesquisar; é o
RÓTULO do que já está lá. Classificar o domínio do link é suficiente.

Os quatro dossiês do Pentateuco usam o estilo antigo (lista de ISBN, sem links).
Para esses, o selo vem de checar o ISBN contra Open Library e Internet Archive —
também por máquina.

O que o script NÃO faz: adivinhar. Item cujo domínio não está na tabela cai em
"indeterminado" e é listado para revisão, em vez de receber selo errado. Selo
errado é pior que selo nenhum: afirma ao leitor que ele consegue obter o que
talvez não consiga.

Uso:
    python selos.py                 # relatório, não escreve nada
    python selos.py --json saida/   # grava um JSON por dossiê
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) estudos-antigos/1.0"

RAIZ = Path(__file__).resolve().parent
DOSSIES = RAIZ / "src" / "content" / "biblioteca" / "biblia"

SLUGS = [
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

# Domínio -> selo. Ordem importa: o primeiro que casar vence.
DOMINIOS: list[tuple[str, str]] = [
    # acesso livre e legal
    ("sacred-texts.com", "livre"),
    ("ccel.org", "livre"),
    ("gutenberg.org", "livre"),
    ("rosetta.reltech.org", "livre"),
    ("mdpi.com", "livre"),
    ("scielo.org", "livre"),
    ("bibleodyssey.org", "livre"),
    ("thetorah.com", "livre"),
    ("biblicalarchaeology.org", "livre"),
    ("library.biblicalarchaeology.org", "livre"),
    ("biblearchaeology", "livre"),
    ("deadseascrolls.org.il", "livre"),
    ("tanach.us", "livre"),
    ("sefaria.org", "livre"),
    ("bibelwissenschaft.de", "livre"),
    ("stepbible.org", "livre"),
    ("biblehub.com", "livre"),
    ("academia.edu", "livre"),
    ("ixtheo.de", "livre"),
    ("cojs.org", "livre"),
    ("jhsonline.org", "livre"),
    ("quran.com", "livre"),
    ("divinity.cam.ac.uk", "livre"),
    ("sots.ac.uk", "livre"),
    ("cjconroy.net", "livre"),
    ("britannica.com", "livre"),
    ("plato.stanford.edu", "livre"),
    ("iep.utm.edu", "livre"),
    # acervo: empréstimo digital ou consulta
    ("archive.org", "emprestimo"),
    ("openlibrary.org", "emprestimo"),
    ("jstor.org", "biblioteca"),
    ("journals.sagepub.com", "biblioteca"),
    ("degruyterbrill.com", "biblioteca"),
    ("brill.com", "biblioteca"),
    ("worldcat.org", "biblioteca"),
    # comércio
    ("books.google.com", "compra"),
    ("loyola.com.br", "compra"),
    ("vidanova.com.br", "compra"),
    ("paulus.com.br", "compra"),
    ("quetzaleditores.pt", "compra"),
    ("wook.pt", "compra"),
    ("martinsfontespaulista.com.br", "compra"),
    ("estantevirtual.com.br", "compra"),
    ("zondervanacademic.com", "compra"),
    ("eerdmans.com", "compra"),
    ("yalebooks.yale.edu", "compra"),
    ("wwnorton.co.uk", "compra"),
    ("wwnorton.com", "compra"),
]

# Domínios que NÃO são obra a obter — são artefato, filme, música ou imagem.
# Ficam fora da tabela: já têm o link no próprio texto, com sua natureza dita.
NAO_OBRA = [
    "imdb.com",
    "britishmuseum.org",
    "louvre.fr",
    "louvrebible.org.uk",
    "nationalgallery.org.uk",
    "collezionegalleriaborghese.it",
    "galleriaaccademiafirenze.it",
    "vam.ac.uk",
    "operatoday.com",
    "philharmonia.org",
    "englishconcert.co.uk",
    "sfcv.org",
    "harmoniamundi.com",
    "lso.co.uk",
    "milton.host.dartmouth.edu",
    "ministrymagazine.org",
    "thegospelcoalition.org",
    "chabad.org",
    "aish.com",
    "reformjudaism.org",
    "wordproject.org",
    "bible.ca",
    "tyndalehouse.com",
    "en.wikipedia.org",
    "pt.wikipedia.org",
    "es.wikipedia.org",
]


def selo_do_link(url: str) -> str | None:
    u = url.lower()
    for dom, selo in DOMINIOS:
        if dom in u:
            return selo
    return None


def eh_nao_obra(url: str) -> bool:
    u = url.lower()
    return any(d in u for d in NAO_OBRA)


def limpar(md: str) -> str:
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)  # links markdown -> texto
    t = t.replace("*", "").replace("**", "")
    t = re.sub(r"\[[VW—][^\]]*\]", "", t)
    return re.sub(r"\s+", " ", t).strip(" ·—-")


def secao_bibliografia(texto: str) -> str:
    """Recorta da bibliografia/âncora até o fim ou o próximo '## '."""
    for padrao in (
        r"^##\s+Bibliografia[^\n]*\n",
        r"^##\s+BIBLIOGRAFIA[^\n]*\n",
        r"^##\s+Autores-âncora[^\n]*\n",
        r"^##\s+Referências-âncora[^\n]*\n",
        r"^##\s+ANEXO[^\n]*\n",
    ):
        m = re.search(padrao, texto, re.MULTILINE)
        if m:
            resto = texto[m.end() :]
            prox = re.search(r"^##\s", resto, re.MULTILINE)
            return resto[: prox.start()] if prox else resto
    return ""


def isbns_do_arquivo(texto: str) -> list[str]:
    """
    ISBNs em QUALQUER lugar do arquivo, não só nas bibliografias em lista.

    Pitfall que isto corrige: os dossiês mais antigos põem a lista de autores em
    PROSA ("Alter (2004, ... ISBN 9780393019551) · Propp (vol. I... ISBN
    9780385246934)"), não em bullets. Ler só as linhas de bullet dava zero para o
    Êxodo — e zero silencioso, que é a pior forma de errar uma contagem.
    """
    achados: list[str] = []
    for i in re.findall(r"\b(97[89]\d{10}|\d{9}[\dXx])\b", texto):
        if i not in achados:
            achados.append(i)
    return achados


ISBN_RE = r"\b(97[89]\d{10}|\d{9}[\dXx])\b"


def _limpa_rotulo(bruto: str) -> str:
    """Limpa um candidato a rótulo: separadores, 'ISBN' pendurado, parêntese aberto."""
    rot = limpar(bruto)
    rot = re.split(r"\s*[·;|]\s*", rot)[-1]
    rot = re.sub(ISBN_RE, "", rot)
    rot = re.sub(
        r"[\s,;:—–-]*\b(ISBN|isbn|ed|ed\.|vol|vol\.|p|pp)\b[\s.,;:]*$", "", rot
    )
    rot = rot.strip(" .*()—-:,")
    # fecha parêntese que ficou pela metade ("Bíblia de Jerusalém (Paulus 2001")
    while rot.count("(") > rot.count(")"):
        rot = rot[: rot.rfind("(")].strip(" .—-,")
    return rot


def _pontuar_rotulo(linha: str, rot: str) -> int:
    """
    Quanto este candidato parece uma ENTRADA BIBLIOGRÁFICA?

    A varredura pega todas as menções do ISBN no arquivo, e a primeira costuma
    estar em prosa ("...reimp. 2017, ISBN 9780300157475..."), que rende rótulo
    inútil. Pontuar e escolher o melhor dá o rótulo da lista de obras, que é o que
    a tabela precisa — sem isso saía "reimp. 2017, ISBN" como se fosse uma obra.
    """
    p = 0
    if re.match(r"\s*(?:-|\d+\.)\s", linha):
        p += 4  # linha de lista = entrada bibliográfica
    if re.search(r"\b(?:19|20)\d{2}\b", rot):
        p += 2  # ano: referência completa
    if 14 <= len(rot) <= 110:
        p += 2
    if "(" in rot and ")" in rot:
        p += 1
    if re.match(r"^[a-zçáéíóú]", rot):
        p -= 4  # começa em minúscula: fragmento de frase
    if len(rot) > 110:
        p -= 2
    return p


def rotulos_por_isbn(texto: str) -> dict[str, str]:
    """
    Mapeia cada ISBN -> a referência COMO O DOSSIÊ A ESCREVE.

    Por que o rótulo não vem da API: a consulta a 9780300157475 devolveu, no Open
    Library, o autor "Samuel P. Huntington" para *The Death and Resurrection of
    the Beloved Son* — que é de Jon D. Levenson. A Perlego reproduz o mesmo
    "Samuel P. Huntington, 1983", ou seja, o erro está na origem do feed e já se
    propagou. O ISBN está certo (a edição eletrônica da Yale é mesmo essa); o
    autor é que veio podre.

    A regra que resolve: o rótulo é do dossiê, que passou por verificação; a API
    só fornece o SELO e a URL. Assim nunca se publica um autor que a API
    atribuiu errado.
    """
    melhores: dict[str, tuple[int, str]] = {}
    for linha in texto.splitlines():
        for m in re.finditer(ISBN_RE, linha):
            isbn = m.group(1)
            rot = _limpa_rotulo(linha[: m.start()])
            if not rot:
                continue
            p = _pontuar_rotulo(linha, rot)
            if isbn not in melhores or p > melhores[isbn][0]:
                melhores[isbn] = (p, rot)
    return {k: v[1] for k, v in melhores.items()}


def analisar(slug: str) -> dict:
    texto = (DOSSIES / f"{slug}.mdx").read_text(encoding="utf-8")
    bloco = secao_bibliografia(texto)

    obras: list[dict] = []
    indeterminados: list[str] = []
    isbns = isbns_do_arquivo(texto)

    for linha in bloco.splitlines():
        s = linha.strip()
        if not s.startswith("-") and not re.match(r"^\d+\.", s):
            continue

        urls = re.findall(r"https?://[^\s\)\]<>]+", s)
        if not urls:
            continue

        de_obra = [u for u in urls if not eh_nao_obra(u)]
        if not de_obra:
            continue

        selos = {selo_do_link(u) for u in de_obra}
        selos.discard(None)

        rotulo = limpar(s)[:110]
        if not rotulo:
            continue

        if not selos:
            indeterminados.append(rotulo)
            continue

        # precedência: livre > empréstimo > biblioteca > compra
        ordem = ["livre", "emprestimo", "biblioteca", "compra"]
        selo = next((o for o in ordem if o in selos), "compra")
        prova = next((u for u in de_obra if selo_do_link(u) == selo), de_obra[0])

        obras.append({"rotulo": rotulo, "selo": selo, "url": prova})

    return {
        "slug": slug,
        "anos": len(obras),
        "obras": obras,
        "indeterminados": indeterminados,
        "isbns": isbns,
        # Rótulos locais expostos aqui porque `texto` é local desta função: quem
        # precisa deles (o modo --online, em main) não tem o texto em mãos.
        "rotulos": rotulos_por_isbn(texto),
        "tem_bibliografia": bool(bloco.strip()),
    }


# Títulos de fichas ADMINISTRATIVAS do Internet Archive que casam com a busca por
# ISBN e não são livros. Sem este filtro a tabela publica "Pallets from BWB for
# 2022-11-01" como se fosse bibliografia.
JUNK_IA = [
    "pallets from",
    "donation from",
    "better world books",
    "box ",
    "shipping",
    "inventory",
]


def normalizar(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[áàâãä]", "a", s)
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[íìîï]", "i", s)
    s = re.sub(r"[óòôõö]", "o", s)
    s = re.sub(r"[úùûü]", "u", s)
    s = re.sub(r"[ç]", "c", s)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", normalizar(s)) if len(t) >= 4}


def titulos_concordam(a: str, b: str) -> bool:
    """
    O título do registro do IA corresponde ao título do catálogo do OL?

    Este teste existe por causa de um caso concreto: a consulta por ISBN de
    *Death and Resurrection of the Beloved Son* devolveu um registro do IA cujo
    campo `creator` dizia "Samuel P. Huntington" — autor errado. O ISBN resolveu,
    o registro existe, e mesmo assim a atribuição estava trocada. Testar que o
    identificador resolve NÃO testa que ele sustenta a afirmação; testar a
    sobreposição de título testa.

    Sobreposição medida contra o menor dos dois conjuntos, exigindo 40%: títulos
    de edições diferentes variam em subtítulo e série, e uma razão sobre o maior
    conjunto reprovaria pares legítimos.
    """
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / min(len(ta), len(tb)) >= 0.4


def ia_por_isbn(isbn: str) -> tuple[str, str, str] | None:
    """
    Consulta o Internet Archive por ISBN e devolve (selo, url, título) só quando o
    registro é confiável. Devolve None quando não é — e None é a resposta certa
    para um registro administrativo ou com título divergente.
    """
    try:
        q = urllib.parse.quote(f"isbn:{isbn}")
        url = (
            "https://archive.org/advancedsearch.php"
            f"?q={q}&fl%5B%5D=identifier&fl%5B%5D=access-restricted-item"
            "&fl%5B%5D=title&fl%5B%5D=creator&fl%5B%5D=year&fl%5B%5D=mediatype"
            "&rows=5&page=1&output=json"
        )
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        dados = json.loads(urllib.request.urlopen(req, timeout=20).read())
        for d in dados.get("response", {}).get("docs", []):
            titulo = d.get("title", "")
            if isinstance(titulo, list):
                titulo = titulo[0] if titulo else ""
            if not titulo:
                continue
            if d.get("mediatype") not in ("texts", None):
                continue
            if any(j in normalizar(titulo) for j in JUNK_IA):
                continue
            restrito = str(d.get("access-restricted-item", "")).lower()
            selo = "emprestimo" if restrito == "true" else "livre"
            return selo, f"https://archive.org/details/{d['identifier']}", titulo
    except Exception:
        pass
    return None


def ol_por_isbn(isbn: str) -> tuple[str, str] | None:
    """Título e autor do catálogo do Open Library. Devolve (título, autor)."""
    try:
        req = urllib.request.Request(
            f"https://openlibrary.org/isbn/{isbn}.json",
            headers={"Accept": "application/json", "User-Agent": UA},
        )
        d = json.loads(urllib.request.urlopen(req, timeout=20).read())
        titulo = d.get("title", "")
        autor = ""
        bs = d.get("by_statement", "")
        if bs:
            autor = re.sub(r"^by\s+", "", bs, flags=re.I)
        elif d.get("authors"):
            try:
                a = d["authors"][0]["key"]
                req2 = urllib.request.Request(
                    f"https://openlibrary.org{a}.json",
                    headers={"Accept": "application/json", "User-Agent": UA},
                )
                autor = json.loads(urllib.request.urlopen(req2, timeout=15).read()).get(
                    "name", ""
                )
            except Exception:
                pass
        if titulo or autor:
            return titulo, autor
    except Exception:
        pass
    return None


def selo_por_isbn(isbn: str) -> tuple[str, str, str]:
    """
    Determina o selo de um ISBN. Devolve (selo, url, rótulo).

    ORDEM DAS FONTES, e a razão dela: o Open Library dá o RÓTULO (é catálogo de
    biblioteca, metadado curado); o Internet Archive dá o SELO (é quem tem o
    arquivo e sabe se é emprestável). Quando os dois divergem no título, o selo do
    IA é descartado — um registro do IA com metadado trocado diria "emprestável" a
    respeito de outra obra.

      IA confiável                  -> [empréstimo] / [livre]
      só ficha no OL                -> [biblioteca]
      nada, ou IA divergente        -> indeterminado (NÃO chutar)
    """
    ol = ol_por_isbn(isbn)
    ia = ia_por_isbn(isbn)

    if ia and ol:
        titulo_ia = ia[2]  # a tupla é (selo, url, título) — não confundir com a URL
        titulo_ol, autor_ol = ol
        if titulos_concordam(titulo_ia, titulo_ol):
            ano = ""
            m = re.search(r"(19|20)\d{2}", titulo_ol)
            rotulo = f"{autor_ol} — {titulo_ol}".strip(" —") if autor_ol else titulo_ol
            if m:
                rotulo = f"{rotulo} ({m.group(0)})"
            return ia[0], ia[1], rotulo
        # divergem: fico com o rótulo do OL e rebaixo para [biblioteca]
        rotulo = f"{autor_ol} — {titulo_ol}".strip(" —") if autor_ol else titulo_ol
        return "biblioteca", f"https://openlibrary.org/isbn/{isbn}", rotulo or isbn

    if ia and not ol:
        # Sem OL não há como conferir o título do IA: fico com o IA, mas o rótulo
        # vem dele, e o risco é só de rótulo — não de selo.
        return ia[0], ia[1], ia[2]

    if ol:
        titulo_ol, autor_ol = ol
        rotulo = f"{autor_ol} — {titulo_ol}".strip(" —") if autor_ol else titulo_ol
        return (
            "biblioteca",
            f"https://openlibrary.org/isbn/{isbn}",
            rotulo or isbn,
        )

    return "indeterminado", "", isbn


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", metavar="DIR", help="grava um JSON por dossiê")
    ap.add_argument(
        "--online",
        action="store_true",
        help="checa os ISBNs contra Internet Archive e Open Library (rede)",
    )
    args = ap.parse_args()

    destino = Path(args.json) if args.json else None
    if destino:
        destino.mkdir(parents=True, exist_ok=True)

    total = ind = 0
    print("== Selo de acesso derivado do que o dossiê já registra ==\n")

    for slug in SLUGS:
        r = analisar(slug)

        # Dossiês sem link na bibliografia: o selo sai do ISBN.
        if args.online and not r["obras"] and r["isbns"]:
            print(f"--- {slug}: {len(r['isbns'])} ISBNs, checando online...")
            locais = r["rotulos"]
            # Em paralelo: em série, um punhado de consultas lentas transforma
            # 60 ISBNs em vários minutos de espera.
            with ThreadPoolExecutor(max_workers=8) as pool:
                res = list(pool.map(selo_por_isbn, r["isbns"]))
            for isbn, (selo, url, rot_api) in zip(r["isbns"], res):
                if selo == "indeterminado":
                    r.setdefault("isbns_sem_selo", []).append(isbn)
                    continue
                # O rótulo do dossiê tem precedência sobre o da API (ver
                # rotulos_por_isbn: a API atribui autor errado em metadado podre).
                rotulo = locais.get(isbn) or rot_api
                r["obras"].append(
                    {"rotulo": rotulo, "selo": selo, "url": url, "isbn": isbn}
                )

        total += len(r["obras"])
        ind += len(r["indeterminados"])

        contagem: dict[str, int] = {}
        for o in r["obras"]:
            contagem[o["selo"]] = contagem.get(o["selo"], 0) + 1

        partes = " · ".join(f"{k}:{v}" for k, v in sorted(contagem.items()))
        print(
            f"--- {slug:12s} {r['obras'].__len__():3d} obras · "
            f"{len(r['indeterminados']):2d} indeterminados · {len(r['isbns']):2d} ISBNs"
        )
        if partes:
            print(f"          {partes}")

        if destino:
            (destino / f"{slug}.json").write_text(
                json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8"
            )

    print(f"\n{total} obras classificadas · {ind} indeterminados (revisar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

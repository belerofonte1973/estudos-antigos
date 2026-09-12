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

# Abaixo disto, o caminho por ISBN rendeu pouco e vale tentar o caminho por
# título (a bibliografia do dossiê de Números não traz ISBN nenhum).
MIN_OBRAS = 6

# Marcador da seção que este próprio script insere nos dossiês.
MARCADOR = "### Como conseguir estas obras"

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


def _rotulo_forte(rot: str) -> bool:
    """
    O rótulo do dossiê é informativo o bastante para ir à tabela?

    Os dossiês do Pentateuco citam em PROSA, e ali o ISBN às vezes vem logo depois
    do sobrenome e nada mais ("Wellhausen", "Childs", "Lewis"). Publicar
    "Wellhausen" como linha de tabela não diz ao leitor que obra é. Nesses casos
    vale mais o rótulo da API, que traz título e autor.
    """
    if len(rot) < 22:
        return False
    if not re.search(r"\b(?:19|20)\d{2}\b", rot) and len(rot.split()) < 4:
        return False
    return True


# Prefixos de identificador do Internet Archive que NÃO são livros: "bwb_" é
# ficha de estoque da Better World Books, "imslp" é partitura. O filtro por
# título não os pega — o identificador é que denuncia.
JUNK_ID = ("bwb_", "imslp", "sim_", "cvb_")


def id_suspeito(ident: str) -> bool:
    i = (ident or "").lower()
    return any(i.startswith(p) for p in JUNK_ID)


def sobrenomes(nome: str) -> set[str]:
    """
    Sobrenome(s) plausíveis de um nome de autor. Cobre as duas ordens: "Budd,
    Philip J" (catálogo) e "Philip J. Budd" (prosa).

    Existe por causa de um caso concreto: buscar no Internet Archive
    title:"Numbers" AND creator:"Budd" devolveu em PRIMEIRO lugar *The hand of God
    as revealed by the light of numbers to **Budd** Reeve* — o campo `creator`
    continha "Budd" (o prenome do autor) e o título continha "numbers". O
    comentário certo, `numbers0005budd` de "Budd, Philip J", vinha em segundo.
    Comparar só título aceita o primeiro; comparar o sobrenome aceita o segundo.
    """
    n = (nome or "").strip()
    if not n:
        return set()
    if "," in n:
        return {normalizar(n.split(",")[0]).strip()}
    toks = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ.'-]{2,}", n)
    if not toks:
        return set()
    if len(toks) == 1:
        return {normalizar(toks[0])}
    return {normalizar(toks[-1]), normalizar(toks[0])}


def autor_concorda(pedido: str, creator: str) -> bool:
    a, b = sobrenomes(pedido), sobrenomes(creator)
    return bool(a and b and (a & b))


def titulo_especifico(t: str) -> bool:
    """
    O título distingue a obra sozinho? Título de uma palavra não distingue: há
    dezenas de comentários chamados só "Numbers" ou "Genesis".
    """
    return len(tokens(t)) >= 3


def titulo_contido(req: str, rec: str) -> bool:
    """
    O título do registro é ESSENCIALMENTE o título pedido, ou apenas o contém?

    Para título curto a diferença é decisiva, e há dois casos concretos que a
    mostram: buscar "Numbers" + "Davies" aceitou *University Arithmetic:
    Embracing the Science of Numbers* — livro de matemática de Charles Davies
    (1846), não o comentário de Números de E. W. Davies. O sobrenome conferia e o
    título continha a palavra.

    Regra: além da sobreposição, o registro não pode acrescentar muito ao título
    pedido. "Numbers" vs "Numbers: A Commentary" passa (1 token a mais); vs
    "University Arithmetic: Embracing the Science of Numbers..." não passa.
    """
    tr, tc = tokens(req), tokens(rec)
    if not tr or not tc:
        return False
    if len(tr & tc) / min(len(tr), len(tc)) < 0.4:
        return False
    limite = 2 if len(tr) <= 2 else 6
    return len(tc - tr) <= limite


def ol_por_titulo(autor: str, titulo: str) -> tuple[str, str] | None:
    """Ficha do Open Library buscando por título+autor. Devolve (título, chave)."""
    try:
        q = urllib.parse.quote(f"{titulo} {autor}".strip())
        url = (
            "https://openlibrary.org/search.json"
            f"?q={q}&limit=5&fields=key,title,author_name,first_publish_year"
        )
        req = urllib.request.Request(
            url, headers={"Accept": "application/json", "User-Agent": UA}
        )
        d = json.loads(urllib.request.urlopen(req, timeout=25).read())
        for doc in d.get("docs", []):
            t = doc.get("title", "")
            if not t or not titulo_contido(titulo, t):
                continue
            # Só aceito se o TÍTULO conferir: buscar por texto livre devolve
            # vizinhos temáticos ("Numbers" casa com qualquer comentário de
            # Números), e sem este teste a obra errada entraria na tabela.
            nomes = doc.get("author_name") or []
            if nomes:
                if not any(autor_concorda(autor, n) for n in nomes):
                    continue
            elif not titulo_especifico(titulo):
                # Sem autor no registro e título genérico: não dá para dizer que é
                # esta obra. Prefiro não ter linha a ter linha errada.
                continue
            return t, doc.get("key", "")
    except Exception:
        pass
    return None


def ia_por_titulo(titulo: str, autor: str) -> tuple[str, str, str] | None:
    """
    Cópia no Internet Archive buscando por título+autor. None se não confiável.

    Exige TÍTULO DISTINTIVO (3+ palavras). Um título de uma só palavra não é
    verificável por busca, e a tentativa produz lixo: buscar "Numbers" achou
    *University Arithmetic: Embracing the Science of Numbers* (Charles Davies,
    1846), *Numbers, Op. 28* (partitura de Walford Davies) e uma ficha de estoque
    da Better World Books. Título curto vai pelo Open Library, que é catálogo
    curado; se nem lá resolver, a obra fica sem selo — que é a resposta honesta.
    """
    if not titulo_especifico(titulo):
        return None
    try:
        q = urllib.parse.quote(f'title:("{titulo}") AND creator:("{autor}")')
        url = (
            "https://archive.org/advancedsearch.php"
            f"?q={q}&fl%5B%5D=identifier&fl%5B%5D=access-restricted-item"
            "&fl%5B%5D=title&fl%5B%5D=creator&fl%5B%5D=mediatype&rows=8&page=1&output=json"
        )
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        dados = json.loads(urllib.request.urlopen(req, timeout=25).read())
        for d in dados.get("response", {}).get("docs", []):
            t = d.get("title", "")
            if isinstance(t, list):
                t = t[0] if t else ""
            if not t or d.get("mediatype") not in ("texts", None):
                continue
            if id_suspeito(d.get("identifier", "")):
                continue
            if any(j in normalizar(t) for j in JUNK_IA):
                continue
            if not titulo_contido(titulo, t):
                continue
            cr = d.get("creator", "")
            if isinstance(cr, list):
                cr = cr[0] if cr else ""
            if cr:
                if not autor_concorda(autor, cr):
                    continue
            elif not titulo_especifico(titulo):
                continue
            restrito = str(d.get("access-restricted-item", "")).lower()
            selo = "emprestimo" if restrito == "true" else "livre"
            return selo, f"https://archive.org/details/{d['identifier']}", t
    except Exception:
        pass
    return None


# Formato "horizontal" da bibliografia do dossiê de Números: várias obras por
# linha, separadas por `|`, SEM ISBN — só "**Gray 1903**, *Título* (Série, Ed.)".
# Sem este caminho o dossiê rendia 2 linhas de tabela contra as 26 obras que o
# próprio relatório dele declara.
ENTRADA_H = re.compile(r"\*\*([^*]{2,44}?)\*\*\s*,?\s*\*([^*]{3,130})\*")


def entradas_horizontais(texto: str) -> list[dict]:
    bloco = secao_bibliografia(texto)
    fora: list[dict] = []
    vistos: set[tuple[str, str]] = set()
    for m in ENTRADA_H.finditer(bloco):
        cabeca, titulo = m.group(1).strip(), m.group(2).strip()
        ma = re.match(r"([A-Za-zÀ-ÿ.'&\-\s]{2,40}?)\s+((?:1[5-9]|20)\d{2})\b", cabeca)
        if not ma:
            continue
        autor, ano = ma.group(1).strip(), ma.group(2)
        chave = (autor.lower(), titulo.lower()[:30])
        if chave in vistos:
            continue
        vistos.add(chave)
        fora.append({"autor": autor, "ano": ano, "titulo": titulo})
    return fora


def selo_por_titulo(autor: str, titulo: str) -> tuple[str, str, str]:
    """Selo para uma obra buscada por título+autor. Mesma escada do ISBN."""
    ia = ia_por_titulo(titulo, autor)
    if ia:
        rotulo = f"{autor} {titulo}".strip()
        return ia[0], ia[1], rotulo
    ol = ol_por_titulo(autor, titulo)
    if ol:
        t, key = ol
        url = f"https://openlibrary.org{key}" if key else ""
        if url:
            return "biblioteca", url, f"{autor} — {t}".strip(" —")
    return "indeterminado", "", f"{autor} {titulo}".strip()


def analisar(slug: str) -> dict:
    texto = (DOSSIES / f"{slug}.mdx").read_text(encoding="utf-8")

    # O próprio script insere a seção 'Como conseguir estas obras' dentro da
    # bibliografia. Sem cortá-la aqui, a segunda execução leria a tabela que ele
    # mesmo escreveu como se fosse bibliografia — e duplicaria as obras. Cortar
    # torna a re-execução idempotente.
    i = texto.find(MARCADOR)
    if i != -1:
        texto = texto[:i]

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
        # Entre os links que sustentam o mesmo selo, prefiro https. Alguns
        # servidores acadêmicos são http-only (rosetta.reltech.org responde 200 em
        # http e não atende em https): o link http continua servindo e por isso
        # NÃO é descartado — só perde para um https equivalente.
        cands = [u for u in de_obra if selo_do_link(u) == selo]
        prova = next((u for u in cands if u.startswith("https://")), cands[0])

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
        "entradas": entradas_horizontais(texto),
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
            if id_suspeito(d.get("identifier", "")):
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
        if args.online and r["isbns"]:
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
                # rotulos_por_isbn: a API atribui autor errado em metadado podre),
                # mas só quando é informativo — senão vale o da API, que ao menos
                # traz o título.
                rot_local = locais.get(isbn, "")
                rotulo = rot_local if _rotulo_forte(rot_local) else (rot_api or rot_local)
                r["obras"].append(
                    {
                        "rotulo": rotulo,
                        "rotulo_local": rot_local,
                        "rotulo_api": rot_api,
                        "selo": selo,
                        "url": url,
                        "isbn": isbn,
                    }
                )

        # Caminho por TÍTULO: o dossiê de Números lista as obras sem ISBN nenhum
        # ("**Gray 1903**, *A Critical...* (ICC, T&T Clark)"), separadas por `|`.
        # O caminho por ISBN rendia 2 linhas contra as 26 obras que o relatório do
        # próprio dossiê declara. Rodo quando o resultado ficou magro.
        if args.online and len(r["obras"]) < MIN_OBRAS and r["entradas"]:
            ent = r["entradas"]
            print(f"--- {slug}: {len(ent)} entradas sem ISBN, buscando por título...")
            with ThreadPoolExecutor(max_workers=6) as pool:
                res2 = list(
                    pool.map(lambda e: selo_por_titulo(e["autor"], e["titulo"]), ent)
                )
            for e, (selo, url, _rot) in zip(ent, res2):
                if selo == "indeterminado":
                    continue
                r["obras"].append(
                    {
                        "rotulo": f"{e['autor']} {e['ano']}, {e['titulo']}",
                        "selo": selo,
                        "url": url,
                    }
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extrai o roteiro de narração a partir de um artigo da revista.

Princípio: não inventar. O texto falado sai do que já está escrito e
verificado no artigo — a pergunta que o artigo responde, a resposta rápida
(que já é prosa direta) e frases de abertura de seção do corpo.

A ordem importa para retenção: pergunta primeiro, resposta depois. É o
inverso do artigo, onde a resposta aparece logo abaixo do título — no vídeo,
a pergunta precisa abrir porque é ela que prende nos primeiros 2 segundos.

Três armadilhas que este módulo trata explicitamente, todas descobertas
quebrando a narração na prática:

1. **Abreviações que terminam frase.** "a.C." fecha oração de verdade;
   "séc." nunca fecha. Proteger as duas do mesmo jeito ou perde a fronteira
   de frase depois de "a.C.", ou parte "séc. V" ao meio. São dois grupos.
2. **Título de seção colado na frase seguinte.** Remover o `##` e juntar as
   linhas produz "A resposta tradicional: Moisés A tradição rabínica...".
   As seções precisam ser separadas ANTES de limpar o markdown.
3. **Frase com pronome órfão.** Uma frase colhida do meio do parágrafo pode
   começar com "Isso mostra..." ou "apontá-las" sem antecedente. Narrada
   sozinha, fica incompreensível. Tais frases são descartadas.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Grupo A — abreviações cujo ponto NUNCA fecha frase: o ponto é consumido.
# "c" (de "c. 1208 a.C.") é obrigatório aqui: sem ele a frase parte no meio
# da data e a narração sai picada.
ABREV_FECHADA = [
    "séc", "sécs", "cap", "caps", "cf", "c", "ed", "eds", "trad", "org", "orgs",
    "p", "pp", "aprox", "vol", "vols", "n", "no", "etc", "ex", "fig", "figs",
    "lit", "art", "arts", "esp", "coord", "dir", "prof", "dr", "dra",
]

# Grupo B — abreviações que PODEM fechar frase: só as letras são consumidas,
# o ponto final é preservado para o divisor de frases poder atuar.
ABREV_ABERTA = ["a.C", "d.C", "a.c", "d.c"]

# Inícios que indicam dependência do que veio antes — ruins para narração solta
ANAFORICOS = re.compile(
    r"^(isso|isto|aquilo|essa|esse|esta|este|estas|estes|aquela|aquele|"
    r"elas|eles|ela|ele|tal|tais|daí|então|assim|a partir|por isso|"
    r"além disso|no entanto|porém|contudo|todavia|também|ainda|"
    r"o mesmo|a mesma|os mesmos|as mesmas|seus|suas|seu|sua|"
    r"estava|estavam|era|eram|foi|foram|havia|tinha|tinham)\b",
    re.IGNORECASE,
)

# Pronomes oblíquos soltos no início do predicado — sinal de antecedente perdido
PRONOME_ORFAO = re.compile(r"\b(lo|la|los|las|lhe|lhes|apontá-\w+|dele|dela)\b")

# Verbo de terceira pessoa abrindo a frase, sem sujeito expresso: sobra de
# parágrafo ("Conta a criação da humanidade..." sem dizer quem conta).
# Narrada sozinha, a frase fica sem sujeito.
VERBO_SEM_SUJEITO = re.compile(
    r"^(conta|contam|descreve|descrevem|apresenta|apresentam|mostra|mostram|"
    r"indica|indicam|relata|relatam|narra|narram|trata|tratam|refere|referem|"
    r"propõe|propõem|argumenta|argumentam|defende|defendem|sustenta|sustentam|"
    r"atesta|atesta|documenta|documentam|registra|registram)\b",
    re.IGNORECASE,
)


@dataclass
class Roteiro:
    """Roteiro pronto: falas na ordem, mais metadados para o vídeo."""
    titulo: str
    pergunta: str
    area: str
    slugs: dict = field(default_factory=dict)
    falas: list[tuple[str, str]] = field(default_factory=list)  # (papel, texto)

    @property
    def narracao(self) -> str:
        return " ".join(t for _, t in self.falas)

    @property
    def palavras(self) -> int:
        return len(self.narracao.split())


# ------------------------------------------------------- frontmatter mínimo
def ler_frontmatter(texto: str) -> dict[str, str]:
    """Lê apenas escalares do frontmatter — o suficiente para o roteiro."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", texto, re.DOTALL)
    if not m:
        raise ValueError("artigo sem frontmatter válido")

    bruto, corpo = m.group(1), m.group(2)
    dados: dict[str, str] = {}

    for linha in bruto.split("\n"):
        if not linha or linha.startswith((" ", "\t", "-")):
            continue
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        valor = valor.strip()
        if valor[:1] in ("'", '"') and valor[-1:] == valor[:1]:
            valor = valor[1:-1]
        dados[chave.strip()] = valor

    return dados | {"_corpo": corpo}


# ------------------------------------------------------------ limpeza de MD
def limpar_markdown(texto: str) -> str:
    t = texto
    t = re.sub(r"```.*?```", " ", t, flags=re.DOTALL)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", t)
    t = re.sub(r"^\s*\|.*$", " ", t, flags=re.MULTILINE)      # tabelas
    t = re.sub(r"^\s*>\s?", " ", t, flags=re.MULTILINE)       # citação
    t = re.sub(r"^\s*[-*+]\s+", " ", t, flags=re.MULTILINE)   # listas
    t = re.sub(r"^\s*\d+\.\s+", " ", t, flags=re.MULTILINE)
    t = re.sub(r"^\s{0,3}#{1,6}\s*", " ", t, flags=re.MULTILINE)
    t = re.sub(r"\[(V|W|—|-)\]", "", t)                       # marcadores do dossiê
    t = re.sub(r"<[^>]+>", " ", t)                            # jsx/html
    t = re.sub(r"[ \t]+", " ", t)
    # tira o espaço das linhas antes de colapsar: sobras de tabela limpam para
    # linhas só com espaços, que sobrevivem ao colapso de "\n{2,}" e colam
    # parágrafos distintos
    t = "\n".join(ln.strip() for ln in t.split("\n"))
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def dividir_em_secoes(corpo: str) -> list[tuple[str, str]]:
    """
    Separa o corpo em (título da seção, texto da seção).

    Feito ANTES de limpar o markdown de propósito: limpar primeiro cola o
    título na primeira frase, e a frase colhida sai híbrida.
    """
    linhas = corpo.split("\n")
    secoes: list[tuple[str, list[str]]] = []
    titulo_atual = ""
    buffer: list[str] = []

    for linha in linhas:
        m = re.match(r"^\s{0,3}(#{2,4})\s+(.*)$", linha)
        if m:
            if buffer or titulo_atual:
                secoes.append((titulo_atual, buffer))
            titulo_atual = m.group(2).strip()
            buffer = []
        else:
            buffer.append(linha)

    if buffer or titulo_atual:
        secoes.append((titulo_atual, buffer))

    return [
        (tit, limpar_markdown("\n".join(corpo_secao)))
        for tit, corpo_secao in secoes
        if limpar_markdown("\n".join(corpo_secao)).strip()
    ]


# Sentinelas de proteção. Área de uso privado do Unicode: não colidem com
# nenhum caractere real do conteúdo, e ao contrário de '\x00' não quebram o
# parser de substituição do módulo `re`.
_S = "\ue000"
_SF = "\ue001"


def dividir_frases(texto: str) -> list[str]:
    """
    Divide em frases com dois cuidados:

    - abreviações fechadas ("séc.") têm o ponto consumido, e nunca dividem;
    - abreviações abertas ("a.C.") preservam o ponto, mas a divisão só ocorre
      quando vem maiúscula depois — assim "séc. V a.C. Não há" divide, e
      "no séc. V a.C. e depois" não divide.
    """
    protegido = texto

    for i, abrev in enumerate(ABREV_FECHADA):
        protegido = re.sub(
            rf"\b{re.escape(abrev)}\.",
            lambda _m, i=i: f"{_S}F{i}{_SF}",
            protegido,
        )

    for i, abrev in enumerate(ABREV_ABERTA):
        protegido = re.sub(
            rf"\b{re.escape(abrev)}(?=\.)",
            lambda _m, i=i: f"{_S}A{i}{_SF}",
            protegido,
        )

    # iniciais de nomes próprios: "Thomas L. Thompson" não é fim de frase
    protegido = re.sub(
        r"\b([A-ZÀ-Ú])\.(?=\s+[A-ZÀ-Ú])",
        lambda m: f"{_S}I{m.group(1)}{_SF}",
        protegido,
    )

    partes = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-Ú0-9“\"—])", protegido)

    frases = []
    for p in partes:
        for i, abrev in enumerate(ABREV_FECHADA):
            p = p.replace(f"{_S}F{i}{_SF}", f"{abrev}.")
        for i, abrev in enumerate(ABREV_ABERTA):
            p = p.replace(f"{_S}A{i}{_SF}", abrev)
        p = re.sub(rf"{_S}I([A-ZÀ-Ú]){_SF}", lambda m: m.group(1) + ".", p)
        p = p.strip()
        if p:
            frases.append(p)
    return frases


def _util(
    frase: str,
    min_palavras: int = 6,
    max_palavras: int = 42,
    exigir_autonoma: bool = False,
) -> bool:
    """Filtra fragmentos, frases longas demais e frases dependentes de contexto."""
    n = len(frase.split())
    if n < min_palavras or n > max_palavras:
        return False
    if not re.search(r"[a-zà-ú]", frase):
        return False
    if _tem_lingua_antiga(frase):
        return False

    if exigir_autonoma:
        # começa com maiúscula: fragmento cortado ("2300 a.C.) é a primeira...")
        # ou cauda de lista quase nunca começa assim
        if not re.match(r"^[A-ZÀ-Ú“\"]", frase):
            return False
        if ANAFORICOS.match(frase):
            return False
        if VERBO_SEM_SUJEITO.match(frase):
            return False
        if PRONOME_ORFAO.search(frase.split(",")[0]):
            return False
        if frase.rstrip().endswith((":", ";")):
            return False
        # Dois-pontos dentro da frase costuma indicar que ela introduz
        # estrutura (lista, enumeração) — lida isolada, fica pendurada.
        if ":" in frase:
            return False
    return True


def _tem_lingua_antiga(texto: str) -> bool:
    return bool(re.search(r"[\u0590-\u05FF\u0370-\u03FF\u1F00-\u1FFF]", texto))


# ----------------------------------------------------------------- roteiro
def montar_roteiro(
    caminho: Path,
    orcamento_palavras: int = 150,
) -> Roteiro:
    """
    Monta o roteiro respeitando um orçamento de palavras — aproximadamente
    60 segundos de fala a ~150 palavras por minuto.
    """
    texto = caminho.read_text(encoding="utf-8")
    fm = ler_frontmatter(texto)

    titulo = fm.get("titulo", caminho.stem)
    pergunta = fm.get("pergunta", titulo)

    roteiro = Roteiro(
        titulo=titulo,
        pergunta=pergunta,
        area=fm.get("area", "biblia"),
        slugs={"dossie": fm.get("dossie", ""), "slug": caminho.stem},
    )

    roteiro.falas.append(("gancho", pergunta))
    gasto = 0

    def adicionar(papel: str, frase: str) -> None:
        nonlocal gasto
        roteiro.falas.append((papel, frase))
        gasto += len(frase.split())

    # --- resposta rápida: o miolo do vídeo, já escrito como prosa direta
    resposta = limpar_markdown(fm.get("respostaRapida", ""))
    for f in dividir_frases(resposta):
        if gasto >= orcamento_palavras * 0.70:
            break
        # frases de resposta rápida são longas por natureza; teto maior
        if _util(f, min_palavras=5, max_palavras=60):
            adicionar("fala", f)

    # --- virada: a primeira frase de uma seção do corpo, que é autônoma
    #     por construção (abre o assunto em vez de continuá-lo)
    secoes = dividir_em_secoes(fm.get("_corpo", ""))
    candidatas: list[str] = []
    vistas = {t for _, t in roteiro.falas}

    for _titulo, corpo_secao in secoes:
        for f in dividir_frases(corpo_secao)[:2]:
            if f in vistas:
                continue
            if _util(f, min_palavras=12, max_palavras=36, exigir_autonoma=True):
                candidatas.append(f)
                vistas.add(f)
                break   # uma por seção: evita amontoar do mesmo assunto

    # prefere frases com carga histórica concreta (data ou nome próprio)
    candidatas.sort(
        key=lambda f: (
            0 if re.search(r"\b\d{3,4}\b", f) else 1,
            0 if re.search(r"\b[A-ZÀ-Ú][a-zà-ú]{3,}\b", f) else 1,
            len(f.split()),
        )
    )

    for f in candidatas[:2]:
        if gasto + len(f.split()) > orcamento_palavras:
            break
        adicionar("virada", f)

    adicionar("cta", "O material completo, com as fontes, está em Estudos Antigos.")

    return roteiro


def relatar(roteiro: Roteiro) -> str:
    linhas = [
        f"Roteiro: {roteiro.titulo}",
        f"  área: {roteiro.area}  ·  dossiê: {roteiro.slugs.get('dossie') or '—'}",
        f"  {len(roteiro.falas)} falas · {roteiro.palavras} palavras "
        f"(~{roteiro.palavras / 150 * 60:.0f}s)",
        "",
    ]
    for papel, texto in roteiro.falas:
        linhas.append(f"  [{papel:>6}] {texto}")
    return "\n".join(linhas)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Valida um ou mais dossiês ANTES do build.

Por que existe: o relatório do subagente não é evidência. Um redator pode
declarar "13 seções, PT-BR limpo" e entregar 9 seções com vazamento de espanhol
— já aconteceu. A regra da casa é verificar o ARTEFATO (o arquivo em disco), e
este script faz a parte mecânica disso de forma repetível.

Separa duas coisas que se confundem:
  FALHAS  — o que torna o artefato inválido: frontmatter, imports, linha em
            branco do MDX, seção ausente, ordem, espanhol, tamanho fora da faixa.
  AVISOS  — qualidade editorial a revisar: densidade de autores por camada,
            esferas confessionais faltando, marcadores escassos.

Tolerância importante: o acervo tem DUAS gerações de dossiês. Os do Pentateuco
usam títulos em caixa alta e nomeados de outro modo ('2. CONTEXTO E AUTORIA',
'4. NARRATIVAS-CHAVE E DEBATE ACADÊMICO'); os de Josué a Reis usam a forma
consagrada ('2. Contexto e Autoria', '4. Conteúdos-chave com Debate'). O
validador aceita as duas e REPORTA qual geração o arquivo segue — um portão que
reprova dossiê íntegro é pior que portão nenhum, e foi o que aconteceu na
primeira versão deste script.

Uso:
    python validar_dossie.py isaias jeremias     # por slug
    python validar_dossie.py --todos
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BIBLIOTECA = RAIZ / "src" / "content" / "biblioteca" / "biblia"

# (número, [grafias aceitas para a seção]) — a comparação é case-insensitive.
SECOES: list[tuple[str, list[str]]] = [
    ("1", ["lead e ficha"]),
    ("2", ["contexto e autoria", "contexto histórico"]),
    ("3", ["estrutura"]),
    ("4", ["conteúdos-chave", "conteúdos chave", "narrativas-chave", "narrativas chave"]),
    ("5", ["temas"]),
    ("6", ["recepção"]),
    ("7", ["traduções pt", "traduções"]),
    ("8", ["audiovisual", "mídias audiovisuais"]),
    ("9", ["mitologia"]),
    ("10", ["filosofia"]),
    ("11", ["teologia"]),
    ("12", ["ciência"]),
    ("13", ["lacunas"]),
]

IMPORTS = [
    "import Card from '../../../components/Card.astro';",
    "import CardGrid from '../../../components/CardGrid.astro';",
    "import Aside from '../../../components/Aside.astro';",
    "import SeloAcesso from '../../../components/SeloAcesso.astro';",
    "import LinkButton from '../../../components/LinkButton.astro';",
]

ESPANHOL = [
    (r"\bhebreo\b", "hebreo"),
    (r"\bpueblo\b", "pueblo"),
    (r"\btambién\b", "también"),
    (r"\bademás\b", "además"),
    (r"\bmientras\b", "mientras"),
    (r"\bsiglos\b", "siglos"),
    (r"\bAntiguo\b(?!\s+Oriente)", "Antiguo"),
    (r"Siglo(?!\s+XXI)", "Siglo"),
    (r"\bmodoo\b", "modoo (normalização cega)"),
    (r"não deserto", "não deserto (normalização cega)"),
]

MIN_PALAVRAS = 6500
MAX_PALAVRAS = 11000


def titulos_de(corpo: str) -> list[tuple[int, str, int, int]]:
    """(nível, texto, início, fim) de cada cabeçalho — com a POSIÇÃO.

    A posição não é luxo: o sumário lateral e as âncoras repetem o texto dos
    títulos, então `corpo.find(titulo)` ancora na primeira ocorrência (o
    sumário) e devolve corpo truncado ou vazio. Foi exatamente o que produziu
    "autores 0/0/0/0" em dossiê que tem autores nas quatro camadas — um
    verificador que reprova seção existente custa mais que nenhum.
    """
    out = []
    for m in re.finditer(r"^(#{2,3})\s+(.+?)\r?$", corpo, re.M):
        out.append((len(m.group(1)), m.group(2), m.start(), m.end()))
    return out


def validar(caminho: Path) -> tuple[list[str], list[str], dict]:
    falhas: list[str] = []
    avisos: list[str] = []
    info: dict = {}
    texto = caminho.read_text(encoding="utf-8")

    if not texto.startswith("---\n"):
        return ["não começa com frontmatter YAML"], [], {}
    fim_fm = texto.find("\n---\n", 4)
    if fim_fm == -1:
        return ["frontmatter sem fecho '---'"], [], {}
    fm = texto[4:fim_fm]
    corpo = texto[fim_fm + 5 :]

    # ---- escopo ------------------------------------------------------------
    # Este validador confere a forma do DOSSIÊ BÍBLICO. Um dossiê de contexto
    # (Suméria, Pré-História) ou uma introdução têm outra forma de propósito, e
    # reprová-los aqui seria ruído — a checagem deles é a do verificar_site.py.
    area_fm = re.search(r"^area:\s*(\S+)", fm, re.M)
    if area_fm and area_fm.group(1) != "biblia":
        return [], [], {"pulado": f"area={area_fm.group(1)} (forma própria, fora do escopo)"}
    # Página de área (introdução de Bíblia, Clássica etc.) também não é dossiê
    # de livro: não tem `livro`/`livros` e segue a forma curta de panorama.
    if "livro" not in fm and "livros" not in fm:
        return [], [], {"pulado": "página de área (sem livro/livros no frontmatter)"}

    # ---- frontmatter -------------------------------------------------------
    chaves = dict(re.findall(r"^(\w+):\s*(.*)$", fm, re.M))
    for exigida in ("title", "description", "area", "ordem", "eixo"):
        if exigida not in chaves:
            falhas.append(f"frontmatter sem '{exigida}'")
    if not ("livro" in chaves or "livros" in chaves):
        falhas.append("frontmatter sem 'livro' nem 'livros'")
    desc = chaves.get("description", "").strip().strip("'\"")
    info["descricao_chars"] = len(desc)
    if len(desc) > 160:
        # O max(160) do schema vale para `artigos` (meta description de SERP).
        # A coleção `biblioteca` não impõe limite: aqui é recomendação.
        avisos.append(f"description com {len(desc)} chars (o Google trunca em ~160)")
    if chaves.get("area") != "biblia":
        falhas.append(f"area = {chaves.get('area')!r} (esperado 'biblia')")
    if chaves.get("eixo") != "nucleo":
        falhas.append(f"eixo = {chaves.get('eixo')!r} (esperado 'nucleo')")

    # ---- imports e a linha em branco que o MDX exige -----------------------
    m = re.match(r"\s*\n((?:import [^\n]+\n)+)", corpo)
    if not m:
        falhas.append("sem bloco de imports depois do frontmatter")
    else:
        bloco = m.group(1)
        for imp in IMPORTS:
            if imp not in bloco and not (imp == IMPORTS[3] and "SeloAcesso" not in corpo):
                falhas.append(f"import ausente: {imp.split(' from ')[0]}")
        if not corpo[m.end() : m.end() + 1].startswith("\n"):
            falhas.append("SEM LINHA EM BRANCO depois dos imports (quebra o build MDX)")

    # ---- seções ------------------------------------------------------------
    titulos = titulos_de(corpo)
    texto_titulos = [(n, t) for n, t, _i, _f in titulos if n == 2]
    geracao_nova = 0
    for numero, alternativas in SECOES:
        achou = None
        for _, t in texto_titulos:
            if not re.match(rf"{numero}\.\s", t):
                continue
            baixo = t.lower()
            if any(alt in baixo for alt in alternativas):
                achou = t
                break
        if not achou:
            # segunda tentativa: só o número, para não perder seção renomeada
            solto = [t for _, t in texto_titulos if re.match(rf"{numero}\.\s", t)]
            if solto:
                falhas.append(f"seção {numero} com título fora do padrão: {solto[0]!r}")
            else:
                falhas.append(f"seção {numero} ausente")
        elif achou == f"{numero}. " + achou.split(". ", 1)[1] and achou[0].isdigit():
            if achou.split(". ", 1)[1][:1].isupper() and not achou.split(". ", 1)[1].isupper():
                geracao_nova += 1
    info["geracao"] = "consagrada" if geracao_nova >= 6 else "primária (títulos em caixa alta)"

    # A bibliografia tem duas grafias no acervo: 'Bibliografia-âncora verificada'
    # (a maioria) e 'Referências-âncora verificadas' (Levítico). Aceitar as duas —
    # o validador existe para pegar ausência, não para impor sinônimo.
    # O acervo usa QUATRO grafias para a bibliografia — todas legítimas:
    #   'Bibliografia-âncora verificada' (a maioria)
    #   'Referências-âncora verificadas' (Levítico)
    #   'Autores-âncora (validação OL, título+autor)' (Êxodo)
    #   'ANEXO — OBRAS-ÂNCORA E VERIFICAÇÃO' (Gênesis)
    # O validador existe para pegar AUSÊNCIA, não para impor sinônimo.
    for extra, grafias in (
        ("bibliografia", ["bibliografia", "referências", "âncora", "fontes"]),
        ("como conseguir estas obras", ["como conseguir estas obras", "como obter"]),
    ):
        if not any(any(g in t.lower() for g in grafias) for _, t, _i, _f in titulos):
            falhas.append(f"bloco ausente: '{extra}'")

    # ordem: os números de seção precisam aparecer crescentes
    nums = [int(m2.group(1)) for _, t in texto_titulos if (m2 := re.match(r"^(\d+)\.\s", t))]
    nums = [n for n in nums if n <= 13]
    if nums != sorted(nums):
        falhas.append(f"seções fora de ordem: {nums}")

    # ---- tamanho -----------------------------------------------------------
    palavras = len(re.sub(r"<[^>]+>", " ", corpo).split())
    info["palavras"] = palavras
    if palavras < MIN_PALAVRAS:
        falhas.append(f"corpo com {palavras} palavras (piso {MIN_PALAVRAS})")
    if palavras > MAX_PALAVRAS:
        falhas.append(f"corpo com {palavras} palavras (teto {MAX_PALAVRAS})")

    # ---- marcadores --------------------------------------------------------
    info["V"] = len(re.findall(r"\[V\]", corpo))
    info["W"] = len(re.findall(r"\[W\]", corpo))
    info["lacuna"] = len(re.findall(r"\[—\]", corpo))
    if info["V"] == 0:
        falhas.append("nenhum marcador [V] — rastreabilidade não aplicada")
    elif info["V"] < 20:
        avisos.append(f"apenas {info['V']} marcadores [V] (os dossiês do acervo têm 29–197)")
    if info["W"] == 0:
        avisos.append("nenhum marcador [W]")

    # ---- camadas -----------------------------------------------------------
    def corpo_secao(numero: str) -> str:
        for i, (n, t, ini, _f) in enumerate(titulos):
            if n == 2 and re.match(rf"{numero}\.\s", t):
                limite = len(corpo)
                for n2, _t2, ini2, _f2 in titulos[i + 1 :]:
                    if n2 == 2:
                        limite = ini2
                        break
                return corpo[ini:limite]
        return ""

    for num, rot in (("9", "Mitologia"), ("10", "Filosofia"), ("11", "Teologia"), ("12", "Ciência")):
        bloco = corpo_secao(num)
        nomes = set(re.findall(r"\*\*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w'’-]{2,})", bloco))
        nomes |= set(re.findall(r"\(([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w'’-]{2,}),?\s+\d{4}", bloco))
        info[f"autores_{num}"] = len(nomes)
        if len(nomes) < 3:
            avisos.append(f"seção {num} ({rot}) com {len(nomes)} autores nomeados")
        if len(re.sub(r"<[^>]+>", " ", bloco).split()) < 120:
            avisos.append(f"seção {num} ({rot}) com corpo curto (menos de 120 palavras)")

    if not re.search(r"não (tem|têm) competência|limite da ciência|onde a ciência", corpo):
        avisos.append("seção 12 sem declaração explícita de onde a ciência não tem competência")

    if "11.1" in corpo:
        esferas = ["judaic", "católic", "ortodox", "protestante", "evangélic"]
        faltando = [e for e in esferas if e not in corpo.lower()]
        if faltando:
            avisos.append(f"11.1 sem as esferas: {faltando}")
        info["selos"] = len(re.findall(r'<SeloAcesso\s+tipo="(\w+)"', corpo))
    else:
        avisos.append("falta a subseção 11.1 (comentaristas por esfera confessional)")

    # ---- espanhol ----------------------------------------------------------
    for padrao, rotulo in ESPANHOL:
        for m3 in re.finditer(padrao, corpo):
            trecho = corpo[max(0, m3.start() - 45) : m3.end() + 45].replace("\n", " ")
            falhas.append(f"espanhol: '{rotulo}' -> ...{trecho}...")

    # ---- MDX ---------------------------------------------------------------
    for m4 in re.finditer(r"<(https?://)", corpo):
        falhas.append(f"URL nua entre <> perto de: {corpo[m4.start():m4.start()+50]!r}")
    for m5 in re.finditer(r"\{[^}\n]{0,40}\}", corpo):
        falhas.append(f"'{'{'}' solto no texto: {m5.group(0)!r}")

    return falhas, avisos, info


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--todos" in sys.argv:
        alvos = sorted(BIBLIOTECA.glob("*.mdx"))
    elif args:
        alvos = [BIBLIOTECA / f"{s}.mdx" for s in args]
    else:
        print(__doc__)
        return 2

    total_f = total_a = 0
    for caminho in alvos:
        print("=" * 72)
        if not caminho.exists():
            print(f"  AUSENTE: {caminho.name}")
            total_f += 1
            continue
        falhas, avisos, info = validar(caminho)
        if info.get("pulado"):
            print(f"  {caminho.name:20s} [PULADO]  {info['pulado']}")
            continue
        marca = "OK" if not falhas else f"{len(falhas)} FALHA(S)"
        if not falhas and avisos:
            marca += f" + {len(avisos)} aviso(s)"
        print(f"  {caminho.name:20s} [{marca}]  forma: {info.get('geracao','?')}")
        if info:
            print(
                f"    {info.get('palavras','?')} palavras · [V]={info.get('V',0)} · "
                f"[W]={info.get('W',0)} · [—]={info.get('lacuna',0)} · "
                f"descr={info.get('descricao_chars','?')} · selos={info.get('selos','?')} · "
                f"autores 9/10/11/12 = {info.get('autores_9',0)}/{info.get('autores_10',0)}/"
                f"{info.get('autores_11',0)}/{info.get('autores_12',0)}"
            )
        for f in falhas:
            print(f"    ✗ {f}")
        for a in avisos:
            print(f"    · {a}")
        total_f += len(falhas)
        total_a += len(avisos)

    print("=" * 72)
    print(f"{len(alvos)} arquivo(s) · {total_f} falha(s) · {total_a} aviso(s)")
    return 1 if total_f else 0


if __name__ == "__main__":
    raise SystemExit(main())

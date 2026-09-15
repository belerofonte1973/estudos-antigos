#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Declara a esfera Evangélica nos 4 dossiês de 1ª geração (higiene 14/set/2026).

O aviso do validador ("11.1 sem as esferas: ['evangélic']") tem causa única:
Gênesis, Êxodo, Deuteronômio e Samuel nasceram com a esfera evangélica DILUÍDA
dentro da protestante. Aqui ela entra declarada, com o critério escrito (séries
críticas de editoras/linhas evangélicas), as obras CONFERIDAS nesta sessão no
Open Library e nos catálogos de editora/livraria, e a contagem corrigida — cada
nome contado uma única vez, na esfera a que pertence.

Mesmo desenho do `inserir_confessional.py`: âncora por cabeçalho, backup por
dossiê, simulação antes de aplicar, idempotente (não insere duas vezes).

Uso:
    python _higiene_evangelica.py --seco
    python _higiene_evangelica.py
"""
from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DOSSIES = RAIZ / "src" / "content" / "biblioteca" / "biblia"
BACKUP = RAIZ / "_camadas" / "_backup" / ("higiene-" + datetime.now().strftime("%Y%m%d-%H%M"))

# ---------------------------------------------------------------- blocos novos
GENESIS = """\
**5. Evangélica (séries críticas modernas).** A fronteira com a esfera protestante acima é de **catálogo, não de valor**: aqui ficam as séries críticas e expositivas de editoras e linhas evangélicas — WBC, NICOT, NAC, TOTC, EBC —, com aparato filológico e bibliografia de primeira mão, no lugar da exposição da Reforma e do devocional clássico. Conferido nesta sessão no Open Library, com editora e ano no registro:

- **Gordon J. Wenham**, *Genesis 1–15* (Word Biblical Commentary 1; Word Books, 1987) e *Genesis 16–50* (WBC 2; Word Books, 1994) [V — OL 9780849902000 e 9780849902017]: o comentário de referência da série, atento à estrutura literária e ao Antigo Oriente Próximo.
- **Victor P. Hamilton**, *The Book of Genesis: Chapters 1–17* (NICOT; Eerdmans, 1990) [V — catálogo OL]; o vol. 18–50 (1995) [W].
- **Kenneth A. Mathews**, *Genesis 11:27–50:26* (New American Commentary 1B; B&H, 2005) [V — catálogo OL]; o vol. 1A, *Genesis 1–11:26* (1996) [W].
- **Bruce K. Waltke** (com Cathi J. Fredricks), *Genesis: A Commentary* (Zondervan, 2001) [V — catálogo OL]: a leitura teológico-canônica de maior circulação entre evangélicos na última geração.
- **Derek Kidner**, *Genesis: An Introduction and Commentary* (TOTC; Tyndale, 1967) [V — catálogo OL]; em português, *Gênesis: introdução e comentário* (Série Cultura Bíblica; Vida Nova) [V — catálogo da série na editora e em livrarias BR].
- **Allen P. Ross**, *Creation and Blessing: A Guide to the Study and Exposition of Genesis* (Baker, 1988; 1ª ed. 1987) [V — catálogo OL].
- **John H. Sailhamer**, *The Pentateuch as Narrative* (Zondervan, 1992) [V — catálogo OL]: leitura que trata a composição final do Pentateuco como unidade literária com estratégia própria.

Dois pontos que a esfera exige declarar. (a) **Wenham e Waltke**, que a esfera protestante registrava acima, contam **uma única vez** — aqui. (b) O comentário evangélico de Gênesis **não é monolítico**: os títulos acima divergem entre si sobre composição, datação e uso da hipótese documentária, e essa divergência interna não se resolve por rótulo — é o que §11 já mostra no debate.
"""

EXODO = """\
**Evangélica (séries críticas modernas).** Mesmo critério declarado da esfera protestante acima, e por onde a fronteira fica visível: são as séries críticas e expositivas de editoras e linhas evangélicas, com aparato filológico e bibliografia de primeira mão. Conferido nesta sessão no Open Library, com editora e ano no registro:

- **John I. Durham**, *Exodus* (Word Biblical Commentary 3; Word Books, 1987) [V — OL 9780849902024] — já registrado no parágrafo protestante acima, por série; conta uma única vez, aqui.
- **Douglas K. Stuart**, *Exodus* (New American Commentary 2; B&H, 2006) [V — OL 9780805401028]: exposição técnica com tradução própria e nota textual.
- **Peter Enns**, *Exodus* (NIV Application Commentary; Zondervan, 2000) [V — OL 9780310520740]: a ponte explícita entre exegese e aplicação, que é o formato da série.
- **R. Alan Cole**, *Exodus: An Introduction and Commentary* (TOTC; Inter-Varsity Press, 1973) [V — catálogo OL]; em português, *Êxodo: introdução e comentário* (Série Cultura Bíblica; Vida Nova, ISBN 9788527500494) [V — catálogo da editora e livrarias BR]: o comentário evangélico de Êxodo que circulou em português antes de qualquer outro.
- **Walter C. Kaiser Jr.**, *Exodus* (Expositor's Bible Commentary; Zondervan; reedição 2008) [V — catálogo OL].
- **Philip Graham Ryken**, *Exodus* (Reformed Expository Commentary; Crossway, 2005) [V — OL 9781433500190]: o comentário reformado contemporâneo de uso congregacional.
- **Cornelis Houtman**, *Exodus* (Historical Commentary on the Old Testament; Kok Pharos, 1993–2000) [V — catálogo OL, volume de 1996]: a leitura reformada holandesa, de fôlego histórico-filológico.
- **David Prior**, *The Message of Exodus: The Days of Our Pilgrimage* (The Bible Speaks Today; Inter-Varsity Press, 2003) — já registrado acima como exposição confessional protestante; conta uma única vez, aqui [W para a data].

Fronteira declarada: **Brevard Childs** (Old Testament Library) e **Terence E. Fretheim** (Interpretation) permanecem na esfera protestante acima — são leitura crítica confessional de linha *mainline*, não séries evangélicas — e a distinção é de catálogo editorial, não de qualidade exegética.
"""

DEUTERONOMIO = """\
**Evangélica (séries críticas modernas).** Critério declarado: as séries críticas e expositivas de editoras e linhas evangélicas — NICOT, TOTC, NAC, NIVAC, NIBC, WBC, Apollos —, com aparato filológico e bibliografia de primeira mão. Conferido nesta sessão no Open Library, com editora e ano no registro:

- **Peter C. Craigie**, *The Book of Deuteronomy* (NICOT; Eerdmans, 1976) [V — OL 9780802823557] — já citado no parágrafo protestante acima, por série; conta uma única vez, aqui.
- **J. A. Thompson**, *Deuteronomy: An Introduction and Commentary* (TOTC; Inter-Varsity Press, 1974) [V — catálogo OL]; em português, *Deuteronômio: introdução e comentário* (Série Cultura Bíblica; Vida Nova, ISBN 9788527500517) [V — catálogo da editora e livrarias BR].
- **Eugene H. Merrill**, *Deuteronomy* (New American Commentary 4; Broadman & Holman, 1994) [V — OL 9780805401042].
- **Daniel I. Block**, *Deuteronomy* (NIV Application Commentary; Zondervan, 2012) [V — OL 9780310492016]: leitura que trata o livro como **catequese de Israel** e sermão de aliança.
- **Christopher J. H. Wright**, *Deuteronomy* (New International Biblical Commentary; Hendrickson/Paternoster, 1996) [V — OL 9780801048142]: o comentário que fixou a leitura missional-ética do Dt em língua inglesa.
- **J. Gordon McConville**, *Deuteronomy* (Apollos Old Testament Commentary, 2002) [V — OL 9780830825059] — já citado acima; conta uma única vez, aqui.
- **Duane L. Christensen**, *Deuteronomy 1–11* (WBC 6A, 1991) e *Deuteronomy 21:10–34:12* (WBC 6B, 2002) — já citado acima; conta uma única vez, aqui [W para a reconferência do catálogo neste passo].
"""

SAMUEL = """\
#### 5. Evangélica
Critério declarado: as **séries críticas e expositivas de editoras e linhas evangélicas** (NAC, TOTC, NICOT, NIVAC, EBC), com aparato filológico e bibliografia de primeira mão. Conferido nesta sessão no Open Library, com editora e ano no registro:

- **Robert D. Bergen**, *1, 2 Samuel* (New American Commentary 7; Broadman & Holman, 1996) [V — OL 9780805401073] — já listado na esfera protestante acima, por série; conta uma única vez, aqui.
- **Joyce G. Baldwin**, *1 and 2 Samuel: An Introduction and Commentary* (TOTC; Inter-Varsity Press, 1988) [V — catálogo OL]; em português, *1 e 2 Samuel: introdução e comentário* (Série Cultura Bíblica; Vida Nova, 1997, ISBN 9788527501910) [V — catálogo da editora e livrarias BR].
- **Bill T. Arnold**, *1 & 2 Samuel* (NIV Application Commentary; Zondervan, 2003) [V — OL 9780310210863].
- **David Toshio Tsumura**, *The First Book of Samuel* (NICOT; Eerdmans, 2007) [V — catálogo OL]: a leitura filológico-discursiva de 1 Samuel, atenta ao discurso direto.
- **Dale Ralph Davis**, *1 Samuel: Looking on the Heart* (Focus on the Bible; Christian Focus, 2003) [V — catálogo OL]: exposição pastoral, no formato da série.
- **Ronald F. Youngblood**, *1, 2 Samuel* (Expositor's Bible Commentary 3; Zondervan, 1992) [W — o registro no Open Library é a edição revisada de 2017, com Longman e Garland como editores de série, não a original].

Fronteira declarada: **P. Kyle McCarter Jr.** (Anchor Bible) permanece na esfera protestante acima — é crítica textual de linha acadêmica geral, não série evangélica.
"""

# ------------------------------------------------------- contagens atualizadas
CONTAGEM_GENESIS = """\
**Contagem e equilíbrio.** Nomes por esfera: católico ocidental **7** (Agostinho, Ambrósio, Jerônimo, Beda, Ruperto, Lira, a Lapide) · grego/oriental **6** (Orígenes, Crisóstomo, Basílio, Gregório de Nissa, Efrém, Teodoreto) · ortodoxo **3** (catena do Octateuco, Lopukhin, Orthodox Study Bible; Florovsky e Lossky apenas como teólogos, com ressalva) · protestante histórica **5** (Lutero, Calvino, Bíblia de Genebra, Henry, Keil–Delitzsch) · evangélica **7** (Wenham, Hamilton, Mathews, Waltke, Kidner, Ross, Sailhamer) · judaico **3** (Rashi, Bereshit Rabbah, Ramban [—]) · não confessional **3** (Wellhausen, Thompson, Finkelstein–Silberman). **Wenham e Waltke migraram** da contagem protestante para a evangélica nesta revisão, e contam uma única vez. O desequilíbrio é de **acesso, não de mérito**: o católico ocidental e o protestante dispõem de séries contínuas; o Oriente vive em catenae e homilias; o ortodoxo, em compilações. Ele é declarado aqui justamente para não ficar silencioso.
"""

CONTAGEM_EXODO = """\
**Contagem e desequilíbrio (declarado).** Por esfera: católico ocidental, 4 nomes (Agostinho, Beda, Nicolau de Lira, Cornélio a Lapide); grego patrístico, 5 (Gregório de Nissa, Orígenes, Teodoreto, Crisóstomo, Efrém); ortodoxo, 2 nomes mais 1 compilação (Lopukhin; Orthodox Study Bible; catena do Octateuco); protestante histórica, 5 (Lutero, Calvino, Matthew Henry, Childs, Fretheim); evangélica, 8 (Durham, Prior, Stuart, Enns, Cole, Kaiser, Ryken, Houtman); judaica, 2 (Rashi, Cassuto); não confessional, 3 (Finkelstein–Silberman, Dever, Assmann). **Durham e Prior** aparecem também no parágrafo protestante, por série; contam uma única vez, na evangélica. O terreno é assimétrico de fato: o Oriente e o ortodoxo vivem de catena e Padres, não de séries modernas, e o silêncio daqui sobre um comentário ortodoxo grego moderno ao Êxodo é **lacuna registrada**, não equilíbrio fingido.
"""

CONTAGEM_DEUTERONOMIO = """\
**Contagem e equilíbrio.** Esferas: católico ocidental (Beda, a *Glossa*, Nicolau de Lira, Cornélio a Lapide — 4); católico oriental / grego patrístico (Orígenes, Teodoreto, Crisóstomo [uso homilético], Efrém [atribuição recusada] — 4); ortodoxo (a catena, Lopukhin, *Orthodox Study Bible* — 3); protestante histórica (Lutero, Calvino, Matthew Henry, Keil–Delitzsch — 4); evangélica (Craigie, Thompson, Merrill, Block, Wright, McConville, Christensen — 7); judaico (Rashi, Ramban, Tigay, Weinfeld — 4); islâmico (remissão a §11.6); não confessional / de método secular (Wellhausen, Niditch, Assmann, Levinson — 4). **Craigie, McConville e Christensen** já apareciam no parágrafo protestante, por série; contam uma única vez, na evangélica. **Desequilíbrio declarado:** a esfera protestante e a evangélica juntas têm mais nomes porque são as que mais produzem séries de comentários a um livro do AT — é assimetria de mercado editorial, não de mérito; e a esfera ortodoxa quase não tem comentário moderno a Dt, o que é **fato estrutural da tradição**, não lacuna de pesquisa. O Oriente entra por fonte primária (Orígenes, Teodoreto, a catena), como o método exige.
"""

# -------------------------------------------------- protestante/evangélica (samuel)
SAMUEL_BULLETS_O = """\
- Protestante: **6** — Calvino, Matthew Henry, Keil–Delitzsch, McCarter, Bergen,
  Baldwin (+ as séries NICOT/NAC/TOTC)."""
SAMUEL_BULLETS_N = """\
- Protestante histórica: **4** — Calvino, Matthew Henry, Keil–Delitzsch, McCarter.
- Evangélica: **6** — Bergen, Baldwin, Arnold, Tsumura, Davis, Youngblood (+ as
  séries NICOT/NAC/TOTC/EBC)."""
SAMUEL_FRASE_O = "A esfera protestante moderna domina a\nbibliografia por **mercado anglófono**"
SAMUEL_FRASE_N = "A esfera protestante-evangélica moderna domina a\nbibliografia por **mercado anglófono**"

# --------------------------------------------------------------- plano de edição
PLANO = {
    "genesis": {
        "marcador": "Evangélica (séries críticas modernas)",
        "novo": GENESIS,
        "ancora": r"^\*\*5\. Ateu, agnóstico e não confessional\.\*\*",
        "renomear": [(r"^\*\*5\. Ateu, agnóstico e não confessional\.\*\*",
                      "**6. Ateu, agnóstico e não confessional.**")],
        "contagem_re": r"\*\*Contagem e equilíbrio\.\*\*.*$",
        "contagem_nova": CONTAGEM_GENESIS,
    },
    "exodo": {
        "marcador": "Evangélica (séries críticas modernas)",
        "novo": EXODO,
        "ancora": r"^\*\*Judaica \(complemento\)\.\*\*",
        "renomear": [],
        "contagem_re": r"\*\*Contagem e desequilíbrio \(declarado\)\.\*\*.*$",
        "contagem_nova": CONTAGEM_EXODO,
    },
    "deuteronomio": {
        "marcador": "Evangélica (séries críticas modernas)",
        "novo": DEUTERONOMIO,
        "ancora": r"^\*\*Vozes judaica e islâmica",
        "renomear": [],
        "contagem_re": r"\*\*Contagem e equilíbrio\.\*\*.*$",
        "contagem_nova": CONTAGEM_DEUTERONOMIO,
    },
    "samuel": {
        "marcador": "#### 5. Evangélica",
        "novo": SAMUEL,
        "ancora": r"^####\s*5\.\s*Ateu",
        "renomear": [
            (r"^####\s*5\.\s*Ateu", "#### 6. Ateu"),
            (r"^####\s*6\.\s*Judaico", "#### 7. Judaico"),
        ],
        "trocas": [(SAMUEL_BULLETS_O, SAMUEL_BULLETS_N), (SAMUEL_FRASE_O, SAMUEL_FRASE_N)],
    },
}


def aplicar(slug: str, cfg: dict, seco: bool) -> dict:
    p = DOSSIES / f"{slug}.mdx"
    texto = p.open(encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in texto else "\n"
    rel = {"slug": slug, "inseriu": False, "renomeou": 0, "contagem": False, "trocas": 0}

    if cfg["marcador"] in texto:
        rel["motivo"] = "já contém a esfera evangélica — nada a fazer"
        return rel

    # --- recorta o bloco §11.x (o aviso do validador é sobre ele) ------------
    cab = re.search(r"^###\s*11\.\d+\..*Comentaristas.*$", texto, re.M)
    if not cab:
        rel["motivo"] = "BLOCO §11.1 NÃO ENCONTRADO"
        return rel
    fim = re.search(r"^##\s*12\.", texto[cab.end():], re.M)
    if not fim:
        rel["motivo"] = "FIM DO BLOCO (§12) NÃO ENCONTRADO"
        return rel
    ini_b, fim_b = cab.start(), cab.end() + fim.start()
    bloco = texto[ini_b:fim_b]

    novo = cfg["novo"].replace("\n", nl)
    m = re.search(cfg["ancora"], bloco, re.M)
    if not m:
        rel["motivo"] = "ÂNCORA NÃO ENCONTRADA"
        return rel
    bloco = bloco[: m.start()] + novo + nl + nl + bloco[m.start():]
    rel["inseriu"] = True

    for pad, rep in cfg.get("renomear", []):
        bloco, n = re.subn(pad, rep, bloco, count=1, flags=re.M)
        rel["renomeou"] += n

    if cfg.get("contagem_re"):
        # o bloco termina nas quebras de linha que antecedem o "## 12." — a
        # substituição não pode comê-las (senão o cabeçalho cola no parágrafo)
        cauda = re.search("[\r\n]+$", bloco)
        cauda = cauda.group(0) if cauda else nl
        padrao = cfg["contagem_re"].replace("$", r"\s*$")
        bloco, n = re.subn(padrao, cfg["contagem_nova"].replace("\n", nl).rstrip(nl),
                           bloco, count=1, flags=re.M | re.S)
        rel["contagem"] = bool(n)
        bloco = bloco.rstrip("\r\n") + cauda

    for velho, novo_t in cfg.get("trocas", []):
        novo_t = novo_t.replace("\n", nl)
        velho = velho.replace("\n", nl)
        if velho in bloco:
            bloco = bloco.replace(velho, novo_t, 1)
            rel["trocas"] += 1
        else:
            rel.setdefault("trocas_falhas", []).append(velho[:60])

    corpo = texto[:ini_b] + bloco + texto[fim_b:]
    rel["chars_antes"], rel["chars_depois"] = len(texto), len(corpo)
    rel["bloco_antes"], rel["bloco_depois"] = fim_b - ini_b, len(bloco)
    if not seco:
        BACKUP.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, BACKUP / f"{slug}.mdx")
        p.write_text(corpo, encoding="utf-8", newline="")
    return rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()
    for slug, cfg in PLANO.items():
        r = aplicar(slug, cfg, args.seco)
        print(f"{slug:14s} inseriu={r['inseriu']} renomeou={r['renomeou']} "
              f"contagem={r['contagem']} trocas={r['trocas']} "
              f"chars {r.get('chars_antes')}->{r.get('chars_depois')} "
              f"{r.get('motivo','')} {r.get('trocas_falhas','')}")
    print("BACKUP:", BACKUP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

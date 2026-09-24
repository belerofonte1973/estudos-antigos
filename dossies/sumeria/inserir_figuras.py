#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
inserir_figuras.py — insere no MASTER.md as figuras aprovadas do manifesto.

Regras (idênticas às do acervo do site, `scripts/imagens_inserir.py`):
  * a figura entra no FIM da seção indicada (`secao` = número do cabeçalho `## N.`),
    imediatamente antes do próximo `## `;
  * a seção é achada pelo NÚMERO, que é estável entre reescritas do texto;
  * rodar duas vezes não duplica (figura cujo arquivo já está no .md é ignorada);
  * backup por arquivo antes de gravar; `--reverter` volta o backup;
  * a seção "18. Figuras com Licença" é reescrita com as figuras REALMENTE
    usadas (obra, acervo, autor, licença, link) — a tabela antiga listava
    origens externas com licenças que vedam reuso e não correspondia ao que o
    dossiê mostrava.

    python dossies/sumeria/inserir_figuras.py --seco
    python dossies/sumeria/inserir_figuras.py
    python dossies/sumeria/inserir_figuras.py --reverter
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from datetime import date

AQUI = pathlib.Path(__file__).resolve().parent
MASTER = AQUI / "00_sumeria_MASTER.md"
MANIFESTO = AQUI / "figuras.json"
BACKUP = AQUI / "00_sumeria_MASTER.md.bak-figuras"


RE_DATA_UPLOAD = re.compile(
    r"\d{2}:\d{2}:\d{2}|according to Exif|^\d{4}-\d{2}-\d{2}$|^Photo released|^Taken on",
    re.I)
AUTOR_VAZIO = ("unknown", "anônimo", "anonymous", "n/a", "sem autor")


def limpar_data(data: str) -> str:
    """Descarta a data quando ela é carimbo do upload, não datação da obra."""
    d = (data or "").strip()
    if not d or RE_DATA_UPLOAD.search(d):
        return ""
    return re.sub(r"(\d)\s+(nd|rd|th|st)\b", r"\1\2", d).strip(" ,;")


def limpar_autor(autor: str) -> str:
    a = re.sub(r"\s*\(\s*talk\s*\)", "", (autor or "").split(" FRCP")[0])
    a = a.split(" from ")[0].strip(" ,")
    metade = len(a) // 2
    if metade > 3 and a[:metade].strip() == a[metade:].strip():
        a = a[:metade].strip()          # "Unknown artist Unknown artist"
    return "" if a.lower().startswith(AUTOR_VAZIO) else a


def bloco(fig: dict) -> str:
    """Bloco de figura: imagem numa linha, legenda no parágrafo seguinte."""
    acervo = fig.get("acervo") or ""
    autor = limpar_autor(fig.get("artista") or "")
    if autor and autor.split()[-1].lower() in acervo.lower():
        autor = ""                      # o crédito já está no acervo
    data = limpar_data(fig.get("data") or "")

    partes = [p for p in (fig.get("tecnica"), data, autor, acervo) if p]
    ficha = "Ficha: " + ", ".join(partes) + "." if partes else ""
    credito = (f"Licença: {fig['licenca']}; fonte: "
               f"[Wikimedia Commons]({fig['fonte']}).")
    return (
        f"![{fig['alt']}]({fig['src']})\n\n"
        f"**Fig. {fig['ordem']} — {fig['titulo']}.** {fig['legenda']} "
        f"*{ficha} {credito}*\n"
    )


def secao_18(figuras: list[dict]) -> str:
    linhas = [
        "## 18. Figuras com Licença",
        "",
        "Todas as figuras deste dossiê têm **obra, acervo e licença conferidos na "
        "API do Wikimedia Commons no momento do download** (ver "
        "`dossies/sumeria/figuras.json` e `dossies/sumeria/baixar_figuras.py`). "
        "Nada entra por atribuição de memória. Só entram licenças que permitem "
        "reuso — domínio público/CC0 (LIVRE) e CC BY/CC BY-SA (ATRIBUICAO, com "
        "crédito ao autor).",
        "",
        "| Fig. | Obra | Acervo | Autor / data | Licença | Origem |",
        "|---|---|---|---|---|---|",
    ]
    for f in sorted(figuras, key=lambda x: x["ordem"]):
        autor = limpar_autor(f.get("artista") or "") or "—"
        data_ = limpar_data(f.get("data") or "") or "—"
        acervo = (f.get("acervo") or "—").replace("|", "/")
        linhas.append(
            f"| {f['ordem']} | {f['titulo']} | {acervo} | {autor} / {data_} | "
            f"{f['licenca']} | [Commons]({f['fonte']}) |")
    livres = sum(1 for f in figuras if f["grupo_licenca"] == "LIVRE")
    atr = sum(1 for f in figuras if f["grupo_licenca"] == "ATRIBUICAO")
    linhas += [
        "",
        f"**Total: {len(figuras)} figuras — {livres} em domínio público/CC0 "
        f"(sem obrigação de crédito) e {atr} em Creative Commons com atribuição "
        f"(crédito ao autor indicado na ficha de cada figura).**",
        "",
        f"Figuras conferidas e baixadas em {date.today().isoformat()}, em "
        f"`dossies/sumeria/imagens/` (JPEG, largura máxima 1100 px).",
        "",
    ]
    return "\n".join(linhas)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--reverter", action="store_true")
    args = ap.parse_args()

    if args.reverter:
        if not BACKUP.exists():
            sys.exit(f"sem backup em {BACKUP}")
        shutil.copy2(BACKUP, MASTER)
        print(f"revertido de {BACKUP}")
        return

    if not MANIFESTO.exists():
        sys.exit(f"sem manifesto em {MANIFESTO} — rode baixar_figuras.py")
    if not BACKUP.exists() and not args.seco:
        shutil.copy2(MASTER, BACKUP)

    figuras = json.loads(MANIFESTO.read_text(encoding="utf-8"))["figuras"]
    texto = MASTER.read_text(encoding="utf-8")
    linhas = texto.splitlines()

    # limites das seções de topo (`## N. ...`), em ordem
    cabec = [(i, int(m.group(1))) for i, l in enumerate(linhas)
             if (m := re.match(r"^##\s+(\d+)\.", l))]
    if not cabec:
        sys.exit("não achei cabeçalhos `## N.` no MASTER.md")

    inseridas, puladas = [], []
    # de trás para frente: inserir não invalida os índices anteriores
    for pos, num in reversed(cabec):
        fim = cabec[cabec.index((pos, num)) + 1][0] if cabec.index((pos, num)) + 1 < len(cabec) else len(linhas)
        if num == 18:
            continue                      # seção 18 é reescrita inteira ao final
        alvo = [f for f in figuras if str(f["secao"]) == str(num)]
        if not alvo:
            continue
        novos = []
        for f in sorted(alvo, key=lambda x: x["ordem"]):
            if f["src"] in texto:
                puladas.append(f)
                continue
            novos.append(f)
        if not novos:
            continue
        corpo = linhas[pos + 1:fim]
        while corpo and not corpo[-1].strip():
            corpo.pop()
        bloco_txt = "".join("\n" + bloco(f) for f in novos)
        linhas[pos + 1:fim] = corpo + bloco_txt.splitlines()
        inseridas += novos

    texto = "\n".join(linhas)

    # reescreve a seção 18 com as figuras realmente usadas
    m18 = re.search(r"^##\s+18\..*?(?=^##\s+19\.)", texto, re.S | re.M)
    if m18:
        texto = texto[:m18.start()] + secao_18(figuras) + texto[m18.end():]
    else:
        print("AVISO: seção 18 não encontrada — não reescrevi a tabela de licenças",
              file=sys.stderr)

    if not args.seco:
        MASTER.write_text(texto, encoding="utf-8")

    print(f"figuras no manifesto: {len(figuras)}")
    print(f"inseridas agora:      {len(inseridas)}")
    print(f"já estavam:           {len(puladas)}")
    por_secao: dict[str, int] = {}
    for f in figuras:
        por_secao[f["secao"]] = por_secao.get(f["secao"], 0) + 1
    print("por seção:            " + ", ".join(
        f"{k}: {v}" for k, v in sorted(por_secao.items(), key=lambda x: int(x[0]))))
    print(f"seção 18 reescrita com {len(figuras)} figuras "
          f"({sum(1 for f in figuras if f['grupo_licenca'] == 'LIVRE')} LIVRE / "
          f"{sum(1 for f in figuras if f['grupo_licenca'] == 'ATRIBUICAO')} ATRIBUICAO)")
    if args.seco:
        print("\n-- secO: nada gravado --")
    else:
        print(f"backup: {BACKUP}")


if __name__ == "__main__":
    main()

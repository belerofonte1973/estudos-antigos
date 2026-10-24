#!/usr/bin/env python3
"""Normaliza a formatacao dos JSONs de imagem do WIP do Josue.

Dois regressos de formato que o script do WIP introduziu:

1. Quebra de linha: os dois arquivos eram LF puro e foram reescritos como CRLF,
   o que faz o diff inteiro do arquivo aparecer como alterado.
2. Indentacao em _imagens/espec_josue.json: as tres entradas acrescentadas
   (Merneptah, Poussin, Loggia) ficaram com 4 espacos nas chaves, quando a
   convencao do arquivo e 3; e o ']' final saiu do indent de 1 espaco.

Nada de conteudo muda: o JSON resultante e igual ao atual.
"""
from __future__ import annotations

import json
import os
import sys
import time

ALVOS = ["_imagens/josue.json", "_imagens/espec_josue.json"]


def abre(caminho: str) -> bytes:
    """Le com retry: o diretorio do repo fica temporariamente indisponivel
    por instantes nesta maquina (ENOENT intermitente em caminho absoluto)."""
    atraso = 0.5
    for tentativa in range(30):
        try:
            with open(caminho, "rb") as f:
                return f.read()
        except FileNotFoundError:
            if tentativa == 29:
                raise
            time.sleep(atraso)
            atraso = min(atraso * 1.5, 4.0)
    raise RuntimeError("sem retorno")


def normaliza_espec(texto: str) -> str:
    """Dedenta as entradas novas (4 -> 3 espacos) e repoe o ']' em 1 espaco."""
    linhas = texto.split("\n")
    # entradas: linhas 61..96 no arquivo com 98 linhas (1-indexado)
    assert linhas[59].strip() == "{", linhas[59]
    assert linhas[96].strip() == "]", linhas[96]
    novas = []
    for i, linha in enumerate(linhas, start=1):
        if 60 <= i <= 96 and linha.startswith("    "):
            linha = linha[1:]
        if i == 97 and linha.strip() == "]":
            linha = " " + linha.strip()
        novas.append(linha)
    return "\n".join(novas)


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    for rel in ALVOS:
        caminho = os.path.join(base, rel.replace("/", os.sep))
        bruto = abre(caminho)
        crlf = bruto.count(b"\r\n")
        lf = bruto.count(b"\n") - crlf
        texto = bruto.decode("utf-8").replace("\r\n", "\n")
        antes = json.loads(texto)
        if rel.endswith("espec_josue.json"):
            texto = normaliza_espec(texto)
        depois = json.loads(texto)
        assert antes == depois, f"conteudo mudou em {rel}"
        with open(caminho, "wb") as f:
            f.write(texto.encode("utf-8"))
        n = len(depois["figuras"]) if "figuras" in depois else len(depois)
        print(f"{rel}: CRLF {crlf} -> 0 | LF {lf} -> {texto.count(chr(10))} | "
              f"conteudo identico ({n} figuras)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

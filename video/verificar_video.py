#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica se as legendas realmente foram renderizadas no vídeo.

Por que isso existe: o arquivo .ass pode estar perfeito e o filtro `ass` do
ffmpeg pode falhar em silêncio (libass sem a fonte, caminho relativo errado,
filtro não aplicado). O vídeo sai bonito, com áudio, e sem uma única palavra
na tela. Ninguém percebe olhando o log — só olhando o vídeo.

Como não há inspeção visual automatizada aqui, a checagem é por contagem de
pixels: extrai quadros dentro de blocos de legenda e compara a densidade de
pixels escuros na faixa da legenda contra a mesma faixa no fundo puro (que
não tem texto). Se a diferença for desprezível, a legenda não foi desenhada.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

ALTERADOS = []
LIMIAR_ESCURO = 140   # abaixo disso o pixel conta como "tinta"


def extrair_quadro(mp4: Path, t: float, destino: Path) -> bool:
    r = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{t:.3f}", "-i", str(mp4),
            "-frames:v", "1", str(destino),
        ],
        capture_output=True,
        text=True,
    )
    return r.returncode == 0 and destino.exists()


def contar_tinta(img: Image.Image, faixa: tuple[int, int]) -> int:
    """Conta pixels escuros numa faixa horizontal (y0, y1)."""
    y0, y1 = faixa
    y1 = min(y1, img.height)
    recorte = img.crop((0, max(0, y0), img.width, y1)).convert("L")
    return sum(1 for p in recorte.getdata() if p < LIMIAR_ESCURO)


def conferir(
    mp4: Path,
    fundo: Path,
    legendas: list[tuple[float, float, str]],
    altura: int,
    margem_vertical: int,
    trabalho: Path,
) -> dict:
    """
    `legendas` é uma lista de (inicio, fim, texto). Retorna um dicionário com
    o laudo. Não levanta exceção — quem chama decide o que fazer.
    """
    laudo: dict = {"quadros": [], "ok": False, "motivo": ""}

    if not fundo.exists():
        laudo["motivo"] = "fundo de referência ausente"
        return laudo

    ref = Image.open(fundo)
    # A legenda é ancorada a `margem_vertical` px do fundo (Alignment=2).
    # A faixa cobre a altura provável das linhas acima e abaixo da âncora.
    faixa = (altura - margem_vertical - 260, altura - margem_vertical + 70)
    tinta_fundo = contar_tinta(ref, faixa)
    laudo["tinta_fundo"] = tinta_fundo

    # escolhe blocos com duração suficiente para o quadro não cair na transição
    candidatos = [l for l in legendas if (l[1] - l[0]) >= 0.6]
    candidatos.sort(key=lambda l: (l[1] - l[0]), reverse=True)
    amostras = candidatos[:3] if len(candidatos) >= 3 else candidatos

    for i, (ini, fim, texto) in enumerate(amostras):
        t = ini + (fim - ini) * 0.45   # meio do bloco, longe do fade
        quadro = trabalho / f"_verif_{i}.png"
        if not extrair_quadro(mp4, t, quadro):
            laudo["quadros"].append(
                {"t": round(t, 2), "texto": texto, "erro": "falha ao extrair quadro"}
            )
            continue
        img = Image.open(quadro)
        tinta = contar_tinta(img, faixa)
        laudo["quadros"].append(
            {
                "t": round(t, 2),
                "texto": texto,
                "tinta": tinta,
                "delta": tinta - tinta_fundo,
            }
        )
        quadro.unlink(missing_ok=True)

    if not laudo["quadros"]:
        laudo["motivo"] = "nenhum bloco de legenda com duração suficiente"
        return laudo

    deltas = [q["delta"] for q in laudo["quadros"] if "delta" in q]
    if not deltas:
        laudo["motivo"] = "não foi possível medir"
        return laudo

    # Com texto desenhado, a diferença é de milhares de pixels de tinta.
    # Um limiar baixo evita falso negativo por antialiasing.
    laudo["delta_minimo"] = min(deltas)
    laudo["ok"] = min(deltas) > 800
    if not laudo["ok"]:
        laudo["motivo"] = (
            "a faixa da legenda tem a mesma densidade de tinta do fundo — "
            "o filtro `ass` provavelmente não desenhou nada"
        )
    return laudo


def relatar(laudo: dict) -> str:
    linhas = ["  verificação visual das legendas:"]
    if "tinta_fundo" in laudo:
        linhas.append(f"    referência (fundo sem texto): {laudo['tinta_fundo']} px de tinta")
    for q in laudo["quadros"]:
        if "erro" in q:
            linhas.append(f"    t={q['t']}s  ERRO: {q['erro']}")
        else:
            linhas.append(
                f"    t={q['t']:>5}s  +{q['delta']:>6} px de tinta  «{q['texto'][:44]}»"
            )
    if laudo.get("motivo"):
        linhas.append(f"    motivo: {laudo['motivo']}")
    linhas.append(f"    resultado: {'OK' if laudo['ok'] else 'FALHOU'}")
    return "\n".join(linhas)


if __name__ == "__main__":
    print("Módulo de verificação. Use a partir de gerar.py.", file=sys.stderr)
    sys.exit(2)

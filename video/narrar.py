#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Narração com edge-tts, preservando o tempo de cada palavra.

O ponto crítico deste módulo é a sincronia. O edge-tts emite eventos
`WordBoundary` com o deslocamento e a duração de cada palavra falada — é isso
que permite a legenda acompanhar a voz em vez de aparecer por conta própria.

Estratégia: uma única chamada para toda a narração. Sintetizar fala por fala
daria mapeamento exato, mas quebraria a prosódia (cada trecho perderia a
curva de entonação do anterior). Uma chamada só soa natural; o mapeamento de
volta para cada trecho do roteiro é feito por contagem de palavras.

O descompasso entre a contagem de palavras do texto e os eventos do TTS é
verificado explicitamente — quando ocorre, o módulo cai para distribuição
proporcional e avisa, em vez de produzir legenda fora de sincronia em silêncio.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import edge_tts

VOZ_PADRAO = "pt-BR-AntonioNeural"

# Unidades de 100 nanossegundos — a unidade que o edge-tts usa nos eventos.
UNIDADE = 10_000_000


@dataclass
class Narracao:
    mp3: Path
    duracao: float
    palavras: list[dict]          # [{texto, inicio, fim}]
    descompasso: bool = False     # True se caiu para distribuição proporcional


async def _sintetizar(texto: str, voz: str, destino: Path, taxa: str) -> list[dict]:
    # `boundary` é obrigatório: o padrão do edge-tts 7.x é 'SentenceBoundary',
    # que emite uma fronteira por frase. Sem pedir 'WordBoundary' não há
    # granularidade nenhuma e a legenda cai para distribuição proporcional.
    communicate = edge_tts.Communicate(
        texto, voz, rate=taxa, boundary="WordBoundary"
    )
    eventos: list[dict] = []

    with open(destino, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                inicio = chunk["offset"] / UNIDADE
                eventos.append(
                    {
                        "texto": chunk["text"],
                        "inicio": inicio,
                        "fim": inicio + chunk["duration"] / UNIDADE,
                    }
                )

    return eventos


def _duracao(caminho: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(caminho),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def _normalizar_para_contagem(texto: str) -> list[str]:
    return texto.split()


def distribuir_por_tempo(
    falas: list[tuple[str, str]], duracao: float
) -> list[tuple[str, str, float, float]]:
    """
    Plano B: reparte o tempo total proporcionalmente ao número de palavras de
    cada fala. Menos preciso que os eventos do TTS, mas nunca fica fora do ar.
    """
    total = sum(len(t.split()) for _, t in falas) or 1
    resultado = []
    cursor = 0.0
    for papel, texto in falas:
        fatia = duracao * (len(texto.split()) / total)
        resultado.append((papel, texto, cursor, cursor + fatia))
        cursor += fatia
    return resultado


def mapear_falas(
    falas: list[tuple[str, str]],
    palavras: list[dict],
    duracao: float,
) -> tuple[list[dict], bool]:
    """
    Associa cada trecho do roteiro ao intervalo de tempo em que é falado,
    guardando também as palavras daquele trecho (é delas que saem as
    legendas que acompanham a voz).

    Devolve (trechos, houve_descompasso). Cada trecho é um dict com
    papel, texto, inicio, fim e palavras.
    """
    esperado = sum(len(t.split()) for _, t in falas)

    if not palavras or abs(len(palavras) - esperado) > max(2, esperado * 0.08):
        proporcional = distribuir_por_tempo(falas, duracao)
        return (
            [
                {"papel": p, "texto": t, "inicio": i, "fim": f, "palavras": []}
                for p, t, i, f in proporcional
            ],
            True,
        )

    resultado: list[dict] = []
    cursor = 0
    for papel, texto in falas:
        n = len(texto.split())
        fatia = palavras[cursor : cursor + n]
        cursor += n
        if not fatia:
            continue
        resultado.append(
            {
                "papel": papel,
                "texto": texto,
                "inicio": fatia[0]["inicio"],
                "fim": fatia[-1]["fim"],
                "palavras": fatia,
            }
        )

    # garante que o último trecho não seja cortado antes do áudio terminar
    if resultado:
        resultado[-1]["fim"] = max(duracao, resultado[-1]["fim"])

    return resultado, False


def gerar(
    texto: str,
    falas: list[tuple[str, str]],
    destino: Path,
    voz: str = VOZ_PADRAO,
    taxa: str = "+0%",
) -> Narracao:
    """
    Sintetiza a narração e devolve o mapeamento temporal de cada trecho.

    `taxa` aceita o formato do edge-tts: '+10%' mais rápido, '-5%' mais lento.
    Para conteúdo explicativo, um pouco mais lento costuma ajudar a retenção.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)

    palavras = asyncio.run(_sintetizar(texto, voz, destino, taxa))
    duracao = _duracao(destino)

    # palavras sem `fim` útil no último evento: estende até o fim do áudio
    if palavras:
        palavras[-1]["fim"] = max(palavras[-1]["fim"], duracao)

    return Narracao(mp3=destino, duracao=duracao, palavras=palavras)


def relatar(narracao: Narracao, temporizado: list[dict]) -> str:
    linhas = [
        f"Narração: {narracao.duracao:.1f}s · {len(narracao.palavras)} eventos de palavra",
    ]
    if narracao.descompasso:
        linhas.append(
            "  AVISO: contagem de palavras divergiu do TTS — "
            "usei distribuição proporcional (legenda pode estar levemente adiantada)"
        )
    linhas.append("")
    for t in temporizado:
        linhas.append(
            f"  {t['inicio']:6.2f}s → {t['fim']:6.2f}s  [{t['papel']:>6}]  "
            f"{t['texto'][:66]}"
        )
    return "\n".join(linhas)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Estilo visual dos vídeos verticais.

Espelha os tokens de `src/styles/global.css` para que o vídeo seja
reconhecivelmente o mesmo produto que o site — mesma paleta, mesma dupla
tipográfica (Inter/Arial para interface, serif para autoridade).

Gera dois artefatos consumidos pelo ffmpeg:
  - um PNG de fundo 1080x1920 (moldura fixa, marca, rodapé)
  - um arquivo .ass com as legendas temporizadas

Por que ASS e não drawtext: o filtro `ass` do libass resolve posicionamento,
quebra de linha e fade sem eu ter de montar cadeias gigantes de filtros, e a
renderização de texto é a mesma que o ffmpeg usa para subtítulos em geral.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------- tokens
LARGURA, ALTURA = 1080, 1920

FUNDO = "#F6F5F4"          # --bg-warm
FUNDO_CARTAO = "#FFFFFF"   # --bg-raised
TINTA = "#1A1A1A"          # --ink
TINTA2 = "#615D59"         # --ink-2
TINTA3 = "#A39E98"         # --ink-3
ACENTO = "#6B4423"         # --accent (siena)
ACENTO_SUAVE = "#F5EBE0"   # --accent-soft
HAIRLINE = "#E4E1DE"

# Fontes do Windows, com alternativas caso alguma falte
FONTES_SERIF = ["georgiab.ttf", "georgia.ttf", "timesbd.ttf", "arialbd.ttf"]
FONTES_SANS = ["arialbd.ttf", "segoeuib.ttf", "arial.ttf"]
FONTES_SANS_REG = ["arial.ttf", "segoeui.ttf"]

DIR_FONTES = Path("C:/Windows/Fonts")


def _fonte(candidatos: list[str], tamanho: int) -> ImageFont.FreeTypeFont:
    for nome in candidatos:
        caminho = DIR_FONTES / nome
        if caminho.exists():
            return ImageFont.truetype(str(caminho), tamanho)
    return ImageFont.load_default(size=tamanho)


def _fonte_para_libass(candidatos: list[str]) -> str:
    """Nome da família que o fontconfig vai resolver (libass usa nomes, não caminhos)."""
    for nome in candidatos:
        if (DIR_FONTES / nome).exists():
            mapa = {
                "georgiab.ttf": "Georgia",
                "georgia.ttf": "Georgia",
                "timesbd.ttf": "Times New Roman",
                "arialbd.ttf": "Arial",
                "arial.ttf": "Arial",
                "segoeuib.ttf": "Segoe UI",
                "segoeui.ttf": "Segoe UI",
            }
            return mapa.get(nome, "Arial")
    return "Arial"


FONTE_SERIF = _fonte_para_libass(FONTES_SERIF)
FONTE_SANS = _fonte_para_libass(FONTES_SANS)

# Âncora vertical das legendas: distância em px da base do quadro.
# 700 põe o texto a ~63% da altura — acima das sobreposições de interface do
# Instagram/TikTok, e ainda na metade inferior, que é onde o olho procura.
MARGEM_VERTICAL = 700


# ------------------------------------------------------------- utilitários
def _hex_para_bgr(hexcor: str) -> str:
    """ASS usa &HAABBGGRR& — alpha invertido (00 = opaco)."""
    h = hexcor.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def _texto_espacado(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    texto: str,
    fonte: ImageFont.FreeTypeFont,
    preenchimento: str,
    espaco: int = 0,
    anchor: str | None = None,
) -> int:
    """
    PIL não tem letter-spacing. Desenha caractere a caractere.
    Devolve a largura total, para permitir centralizar.
    """
    if espaco == 0:
        draw.text(xy, texto, font=fonte, fill=preenchimento, anchor=anchor)
        return int(draw.textlength(texto, font=fonte))

    largura_total = sum(
        draw.textlength(c, font=fonte) + (espaco if i < len(texto) - 1 else 0)
        for i, c in enumerate(texto)
    )
    x, y = xy
    if anchor and anchor.startswith("m"):
        x -= largura_total / 2
    for i, c in enumerate(texto):
        draw.text((x, y), c, font=fonte, fill=preenchimento, anchor="l" + (anchor[1:] if anchor else "a"))
        x += draw.textlength(c, font=fonte) + espaco
    return int(largura_total)


def _quebra_texto(
    draw: ImageDraw.ImageDraw,
    texto: str,
    fonte: ImageFont.FreeTypeFont,
    largura_max: int,
) -> list[str]:
    """Quebra em linhas cabendo em largura_max."""
    palavras = texto.split()
    linhas: list[str] = []
    atual = ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        if draw.textlength(teste, font=fonte) <= largura_max or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


# ------------------------------------------------------------------ fundo
@dataclass
class DadosFundo:
    area: str
    handle: str = "estudosantigos"
    marca: str = "ESTUDOS ANTIGOS"


def gerar_fundo(dados: DadosFundo, destino: Path) -> Path:
    """
    Moldura fixa do vídeo: fundo quente, barra de acento à esquerda, marca no
    topo e rodapé. O texto falado NÃO entra aqui — ele vem no .ass, para mudar
    ao longo do tempo sem recompor o fundo.
    """
    img = Image.new("RGB", (LARGURA, ALTURA), FUNDO)
    d = ImageDraw.Draw(img)

    # Barra de acento à esquerda — âncora visual da identidade
    d.rectangle([0, 0, 16, ALTURA], fill=ACENTO)

    # Marca d'água: marca do livro, grande e muito discreta, no centro
    marca = _fonte(FONTES_SANS, 520)
    d.text(
        (LARGURA // 2 + 30, ALTURA // 2 - 40),
        "❧",
        font=marca,
        fill="#EDEAE7",
        anchor="mm",
    )

    # --- topo: marca
    f_marca = _fonte(FONTES_SANS, 30)
    y = 118
    largura_marca = _texto_espacado(
        d, (92, y), dados.marca, f_marca, TINTA2, espaco=6
    )
    d.rectangle([92, y + 52, 92 + largura_marca, y + 55], fill=ACENTO)

    # --- área de estudo
    f_area = _fonte(FONTES_SANS, 26)
    _texto_espacado(d, (92, y + 82), dados.area.upper(), f_area, ACENTO, espaco=3)

    # --- rodapé: linha + handle + legenda dos marcadores
    y_rod = ALTURA - 250
    d.rectangle([92, y_rod, LARGURA - 92, y_rod + 1], fill=HAIRLINE)

    f_rod = _fonte(FONTES_SANS_REG, 26)
    d.text((92, y_rod + 40), dados.handle, font=f_rod, fill=TINTA3)

    f_rod2 = _fonte(FONTES_SANS_REG, 22)
    d.text(
        (LARGURA - 92, y_rod + 42),
        "cada afirmação com fonte",
        font=f_rod2,
        fill=TINTA3,
        anchor="ra",
    )

    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, "PNG", optimize=True)
    return destino


# --------------------------------------------------------------- legendas
@dataclass
class Fala:
    texto: str
    inicio: float
    fim: float
    papel: str = "fala"   # gancho | fala | virada | cta


def _ts(segundos: float) -> str:
    """0:00:00.00 — formato de tempo do ASS."""
    if segundos < 0:
        segundos = 0.0
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = segundos % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def agrupar_em_frases(
    palavras: list[dict],
    max_palavras: int = 4,
    max_duracao: float = 2.0,
) -> list[list[dict]]:
    """
    Agrupa palavras em blocos curtos — o formato que se lê de relance no
    celular. Quebra antes de ficar longo demais, e também em fim de frase,
    para a legenda não atravessar a pausa.
    """
    frases: list[list[dict]] = []
    atual: list[dict] = []
    for p in palavras:
        atual.append(p)
        duracao = atual[-1]["fim"] - atual[0]["inicio"]
        fim_de_frase = bool(re.search(r"[.!?…]$", p["texto"].strip()))
        if len(atual) >= max_palavras or duracao >= max_duracao or fim_de_frase:
            frases.append(atual)
            atual = []
    if atual:
        frases.append(atual)
    return frases


def gerar_ass(
    falas: list[Fala],
    destino: Path,
    margem_vertical: int = MARGEM_VERTICAL,
) -> Path:
    """
    Escreve as legendas em ASS.

    Um Dialogue por bloco de fala. O texto é o mesmo da narração, então a
    legenda nunca diverge do áudio por construção.
    """
    cabecalho = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {LARGURA}
PlayResY: {ALTURA}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Gancho,{FONTE_SERIF},86,{_hex_para_bgr(TINTA)},{_hex_para_bgr(TINTA)},{_hex_para_bgr(FUNDO)},&H00000000,-1,0,0,0,100,100,0,0,1,10,0,2,110,110,{margem_vertical},1
Style: Fala,{FONTE_SANS},74,{_hex_para_bgr(TINTA)},{_hex_para_bgr(TINTA)},{_hex_para_bgr(FUNDO)},&H00000000,-1,0,0,0,100,100,0,0,1,10,0,2,110,110,{margem_vertical},1
Style: Virada,{FONTE_SERIF},76,{_hex_para_bgr(ACENTO)},{_hex_para_bgr(ACENTO)},{_hex_para_bgr(FUNDO)},&H00000000,-1,0,0,0,100,100,0,0,1,10,0,2,110,110,{margem_vertical},1
Style: Cta,{FONTE_SANS},64,{_hex_para_bgr(ACENTO)},{_hex_para_bgr(ACENTO)},{_hex_para_bgr(FUNDO)},&H00000000,-1,0,0,0,100,100,0,0,1,10,0,2,110,110,{margem_vertical - 60},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ESTILO = {"gancho": "Gancho", "fala": "Fala", "virada": "Virada", "cta": "Cta"}

    linhas: list[str] = []
    for f in falas:
        estilo = ESTILO.get(f.papel, "Fala")
        # fade curto: entrada legível sem parecer travado
        efeito = r"{\fad(90,110)}" if f.papel != "cta" else r"{\fad(200,300)}"
        texto = f.texto.replace("\n", r"\N")
        linhas.append(
            f"Dialogue: 0,{_ts(f.inicio)},{_ts(f.fim)},{estilo},,0,0,0,,{efeito}{texto}"
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(cabecalho + "\n".join(linhas) + "\n", encoding="utf-8")
    return destino

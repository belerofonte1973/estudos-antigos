#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gera um vídeo curto vertical (1080x1920) a partir de um artigo da revista.

    python video/gerar.py quem-escreveu-o-genesis
    python video/gerar.py --todos
    python video/gerar.py quem-escreveu-o-genesis --voz pt-BR-FranciscaNeural --taxa -5%

O vídeo reaproveita o texto já verificado do artigo: não há redação nova, e
portanto não há risco de o vídeo afirmar algo que o artigo não sustenta.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import estilo  # noqa: E402
import narrar  # noqa: E402
import roteiro as mod_roteiro  # noqa: E402
import verificar_video  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ARTIGOS = RAIZ / "src" / "content" / "artigos"
SAIDA = Path(__file__).resolve().parent / "saida"

# Áreas -> rótulo exibido no topo do vídeo
ROTULOS_AREA = {
    "biblia": "Antiguidade Bíblica",
    "classica": "Antiguidade Clássica",
    "idade-media": "Idade Média",
    "pre-historia": "Pré-História",
    "oriente": "Oriente Próximo Antigo",
}


# Abreviações que não devem quebrar a legenda, mesmo terminando em ponto
_NAO_QUEBRA = {
    "séc", "sécs", "cap", "caps", "cf", "c", "ed", "eds", "trad", "org",
    "p", "pp", "aprox", "vol", "no", "etc", "ex", "fig", "a.c", "d.c",
    "j", "e", "l", "dr", "dra", "prof",
}


def _grupos_de_palavras(palavras: list[str], max_palavras: int = 4) -> list[list[str]]:
    """
    Agrupa as palavras DO TEXTO do artigo em blocos de legenda.

    Usa o texto original (com pontuação) e não os tokens do TTS — o edge-tts
    devolve as palavras sem vírgulas, e legenda sem pontuação fica ilegível
    ("vocabulários distintos o modelo clássico").
    """
    grupos: list[list[str]] = []
    atual: list[str] = []

    for p in palavras:
        atual.append(p)
        limpa = p.strip(".,;:!?…\"'“”").lower()
        fecha = p.rstrip()[-1:] in ".,;:!?…"
        # não quebra em abreviação conhecida ("séc.", "a.C.")
        if limpa in _NAO_QUEBRA:
            fecha = False
        if len(atual) >= max_palavras or fecha:
            grupos.append(atual)
            atual = []
    if atual:
        grupos.append(atual)
    return grupos


def _tempos_exatos(
    grupos: list[list[str]], palavras_tts: list[dict]
) -> list[tuple[float, float]]:
    """Casa cada grupo com o tempo real das suas palavras no áudio."""
    tempos = []
    cursor = 0
    for grupo in grupos:
        n = len(grupo)
        fatia = palavras_tts[cursor : cursor + n]
        cursor += n
        if fatia:
            tempos.append((fatia[0]["inicio"], fatia[-1]["fim"]))
        else:
            tempos.append((tempos[-1][1], tempos[-1][1]) if tempos else (0.0, 0.0))
    return tempos


def _tempos_proporcionais(
    grupos: list[list[str]], inicio: float, fim: float
) -> list[tuple[float, float]]:
    """
    Plano B por trecho: o TTS não devolveu o mesmo número de palavras que o
    texto (siglas, números romanos). Reparte o tempo pela contagem de palavras.
    """
    total = sum(len(g) for g in grupos) or 1
    tempos = []
    cursor = inicio
    for grupo in grupos:
        fatia = (fim - inicio) * (len(grupo) / total)
        tempos.append((cursor, cursor + fatia))
        cursor += fatia
    return tempos


def _montar_legendas(temporizado: list[dict]) -> list[estilo.Fala]:
    """
    Converte os trechos narrados em legendas de tela.

    O texto exibido vem do artigo (com pontuação); o tempo vem dos eventos de
    palavra do TTS. Quando as duas contagens divergem, o trecho cai para
    distribuição proporcional — o texto continua correto, só o sincronismo
    fica aproximado.
    """
    legendas: list[estilo.Fala] = []

    for t in temporizado:
        papel = t["papel"]
        palavras_tts = t["palavras"]
        palavras_txt = t["texto"].split()

        # pergunta e chamada final aparecem inteiras: são curtas e precisam
        # ser lidas de uma vez
        if papel in ("gancho", "cta") or len(palavras_txt) <= 4:
            legendas.append(
                estilo.Fala(
                    texto=t["texto"],
                    inicio=t["inicio"],
                    fim=t["fim"],
                    papel=papel,
                )
            )
            continue

        grupos = _grupos_de_palavras(palavras_txt)

        if palavras_tts and len(palavras_tts) == len(palavras_txt):
            tempos = _tempos_exatos(grupos, palavras_tts)
        else:
            tempos = _tempos_proporcionais(grupos, t["inicio"], t["fim"])

        for grupo, (ini, fim) in zip(grupos, tempos):
            legendas.append(
                estilo.Fala(
                    texto=" ".join(grupo),
                    inicio=ini,
                    fim=fim + 0.12,
                    papel=papel,
                )
            )

    # Sem sobreposição: o libass desenharia duas legendas ao mesmo tempo.
    # O corte é feito para trás e, se o bloco ficar curto demais, o início do
    # seguinte é empurrado — nunca os dois ao mesmo tempo na tela.
    for i in range(len(legendas) - 1):
        atual, seguinte = legendas[i], legendas[i + 1]
        if atual.fim >= seguinte.inicio:
            novo_fim = seguinte.inicio - 0.02
            if novo_fim - atual.inicio >= 0.40:
                atual.fim = novo_fim
            else:
                seguinte.inicio = atual.fim + 0.02

    return legendas


def _ffprobe(caminho: Path) -> dict:
    r = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(caminho),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(r.stdout)


def montar_video(
    slug: str,
    voz: str = narrar.VOZ_PADRAO,
    taxa: str = "+0%",
    orcamento: int = 150,
) -> Path:
    origem = ARTIGOS / f"{slug}.md"
    if not origem.exists():
        raise SystemExit(f"artigo não encontrado: {origem}")

    trabalho = SAIDA / slug
    trabalho.mkdir(parents=True, exist_ok=True)

    # 1. roteiro
    rot = mod_roteiro.montar_roteiro(origem, orcamento_palavras=orcamento)
    (trabalho / "roteiro.txt").write_text(
        mod_roteiro.relatar(rot), encoding="utf-8"
    )

    # 2. narração
    mp3 = trabalho / "narracao.mp3"
    narracao = narrar.gerar(rot.narracao, rot.falas, mp3, voz=voz, taxa=taxa)

    # 3. sincronia
    temporizado, descompasso = narrar.mapear_falas(
        rot.falas, narracao.palavras, narracao.duracao
    )
    narracao.descompasso = descompasso

    duracao = narracao.duracao

    # 4. legendas + fundo
    legendas = _montar_legendas(temporizado)
    sobreposicoes = sum(
        1
        for i in range(len(legendas) - 1)
        if legendas[i].fim > legendas[i + 1].inicio + 0.001
    )
    ass = estilo.gerar_ass(legendas, trabalho / "legendas.ass")
    fundo = estilo.gerar_fundo(
        estilo.DadosFundo(area=ROTULOS_AREA.get(rot.area, rot.area)),
        trabalho / "fundo.png",
    )

    # 5. composição
    saida = trabalho / f"{slug}.mp4"
    fade_out = max(0.0, duracao - 0.7)
    afade_out = max(0.0, duracao - 0.8)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "30", "-i", fundo.name,
        "-i", mp3.name,
        "-vf", f"ass={ass.name},fade=t=in:st=0:d=0.5,fade=t=out:st={fade_out:.2f}:d=0.7",
        "-af", f"afade=t=in:st=0:d=0.3,afade=t=out:st={afade_out:.2f}:d=0.8",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", f"{duracao:.3f}",
        "-movflags", "+faststart",
        "-metadata", f"title={rot.titulo}",
        saida.name,
    ]
    r = subprocess.run(cmd, cwd=trabalho, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        raise SystemExit("ffmpeg falhou")

    # 6. verificação do artefato
    info = _ffprobe(saida)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur_real = float(info["format"]["duration"])
    tamanho_mb = saida.stat().st_size / 1_048_576

    problemas = []
    if (video["width"], video["height"]) != (estilo.LARGURA, estilo.ALTURA):
        problemas.append(f"resolução {video['width']}x{video['height']}")
    if abs(dur_real - duracao) > 0.5:
        problemas.append(f"duração {dur_real:.2f}s vs narração {duracao:.1f}s")
    if not audio:
        problemas.append("sem faixa de áudio")
    if video["pix_fmt"] != "yuv420p":
        problemas.append(f"pix_fmt {video['pix_fmt']} (incompatível com celular)")
    if sobreposicoes:
        problemas.append(f"{sobreposicoes} sobreposição(ões) de legenda")

    # 7. verificação visual: a legenda chegou mesmo à imagem?
    laudo = verificar_video.conferir(
        saida,
        fundo,
        [(l.inicio, l.fim, l.texto) for l in legendas],
        estilo.ALTURA,
        estilo.MARGEM_VERTICAL,
        trabalho,
    )
    if not laudo["ok"]:
        problemas.append(f"legendas não renderizaram ({laudo.get('motivo', '?')})")

    print(f"\n== {slug} ==")
    print(narrar.relatar(narracao, temporizado))
    print(
        f"\n  vídeo: {video['width']}x{video['height']} · {video['codec_name']}"
        f" · {dur_real:.1f}s · {tamanho_mb:.1f} MB"
    )
    print(f"  áudio: {audio['codec_name'] if audio else '—'}"
          f" · {audio.get('sample_rate', '?') if audio else '?'} Hz")
    print(f"  legendas: {len(legendas)} blocos")
    print(verificar_video.relatar(laudo))
    print(f"  saída: {saida}")

    if problemas:
        raise SystemExit("PROBLEMAS: " + "; ".join(problemas))

    (trabalho / "verificacao.json").write_text(
        json.dumps(
            {
                "slug": slug,
                "duracao": dur_real,
                "resolucao": f"{video['width']}x{video['height']}",
                "blocos_legenda": len(legendas),
                "descompasso_tts": descompasso,
                "voz": voz,
                "taxa": taxa,
                "palavras": rot.palavras,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return saida


def listar_artigos() -> list[str]:
    return sorted(p.stem for p in ARTIGOS.glob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Gera vídeo curto vertical a partir de um artigo da revista."
    )
    ap.add_argument("slug", nargs="?", help="slug do artigo (sem .md)")
    ap.add_argument("--todos", action="store_true", help="gera para todos os artigos")
    ap.add_argument("--listar", action="store_true", help="lista os artigos disponíveis")
    ap.add_argument("--voz", default=narrar.VOZ_PADRAO)
    ap.add_argument("--taxa", default="+0%", help="ex.: -5%% mais lento, +10%% mais rápido")
    ap.add_argument("--orcamento", type=int, default=150, help="máximo de palavras na fala")
    args = ap.parse_args()

    if args.listar:
        for s in listar_artigos():
            print(f"  {s}")
        return 0

    if args.todos:
        slugs = listar_artigos()
        if not slugs:
            raise SystemExit("nenhum artigo encontrado")
        falhas = []
        for s in slugs:
            try:
                montar_video(s, args.voz, args.taxa, args.orcamento)
            except SystemExit as e:
                falhas.append(f"{s}: {e}")
        print("\n" + "=" * 54)
        print(f"{len(slugs) - len(falhas)}/{len(slugs)} vídeos gerados")
        for f in falhas:
            print(f"  ✗ {f}")
        return 1 if falhas else 0

    if not args.slug:
        ap.print_help()
        return 2

    slug = args.slug.replace(".md", "")
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise SystemExit(f"slug inválido: {slug}")
    montar_video(slug, args.voz, args.taxa, args.orcamento)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gerar_html_avulso.py — converte TODO o build do Astro (dist/) em um conjunto
de arquivos HTML AUTÔNOMOS, num só diretório, com a navegação interna
funcionando de verdade (sem servidor e sem internet).

O que faz:
  1. mapeia cada rota do build para um nome de arquivo plano:
       /biblioteca/biblia/<slug>/   -> <slug>.html      (os dossiês, nome curto)
       /biblioteca/biblia/          -> index.html       (índice do conjunto)
       /                            -> inicio.html      (capa do site)
       as demais                    -> caminho-com-hifens.html
  2. inline do CSS do site (os <link rel="stylesheet" href="/_astro/..."> viram <style>)
  3. baixa UMA vez as fontes web (Inter + Source Serif 4, subconjuntos latinos)
     para <destino>/fonts/ e troca o @import do Google Fonts por @font-face
     locais — o conjunto abre sem internet, com a tipografia do site
  4. reaponta TODO link interno para o arquivo local correspondente; só perde
     o href o que não tem par local (ex.: rota inexistente) — nada de link morto
  5. copia favicon.svg, og-default.png, rss.xml e os sitemaps
  6. o tema claro/escuro continua funcionando: o script de alternância já é
     inline na página e usa localStorage ('ea-theme')

Saída: <destino>/*.html + favicon.svg + og-default.png + rss.xml + fonts/*.woff2

Uso:
    python scripts/gerar_html_avulso.py                 # gera em html-avulso/
    python scripts/gerar_html_avulso.py --limpar        # apaga o destino antes
    python scripts/gerar_html_avulso.py --destino outra_pasta
"""
import argparse
import pathlib
import re
import shutil
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / "dist"
DESTINO_PADRAO = RAIZ / "html-avulso"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

IMPORT_RE = re.compile(r'@import\s+"([^"]+)"\s*;')
FONTFACE_RE = re.compile(r"@font-face\s*\{[^}]*\}")
FONTURL_RE = re.compile(r"url\((https://fonts\.gstatic\.com/[^)]+)\)")

# arquivos que o build publica na raiz e que são referenciados por links
EXTRAS = ["favicon.svg", "og-default.png", "rss.xml", "sitemap-index.xml", "sitemap-0.xml"]


# ----------------------------------------------------------------- mapa de rotas
def rota_de(caminho_html):
    """dist/biblioteca/biblia/juizes/index.html -> /biblioteca/biblia/juizes/"""
    rel = caminho_html.relative_to(BUILD).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return "/" + rel


def mapa_de_rotas():
    """rota -> nome do arquivo de saída (plano, sem colisão)."""
    mapa = {}
    for p in sorted(BUILD.rglob("*.html")):
        rota = rota_de(p)
        m = re.fullmatch(r"/biblioteca/biblia/([a-z0-9\-]+)/", rota)
        if m:
            nome = f"{m.group(1)}.html"
        elif rota == "/biblioteca/biblia/":
            nome = "index.html"
        elif rota == "/":
            nome = "inicio.html"
        elif rota == "/404.html":
            nome = "404.html"
        else:
            nome = rota.strip("/").replace("/", "-") + ".html"
        mapa[rota] = nome
    for extra in EXTRAS:
        if (BUILD / extra).exists():
            mapa[f"/{extra}"] = extra

    # colisão seria dois arquivos com o mesmo nome: aborta antes de escrever
    vistos = {}
    for rota, nome in mapa.items():
        if nome in vistos:
            sys.exit(f"COLISÃO de nomes: {vistos[nome]} e {rota} -> {nome}")
        vistos[nome] = rota
    return mapa


def href_local(href, mapa):
    """Link interno do site -> arquivo local (ou None se não houver par)."""
    if href.startswith("/"):
        for variante in (href, href.rstrip("/") + "/", href.rstrip("/")):
            if variante in mapa:
                return f"./{mapa[variante]}"
    return None


# ----------------------------------------------------------------- fontes web
def preparar_fontes(css_texto, destino):
    """Devolve (import_original, bloco_fontes_local, mensagem).

    'bloco_fontes_local' é o conjunto de @font-face com url(./fonts/*.woff2),
    pronto para substituir o @import do Google Fonts em cada cópia do CSS.
    Sem rede devolve (None, None, msg) e o @import fica como está — as páginas
    seguem funcionando com as fontes de reserva do sistema.
    """
    m = IMPORT_RE.search(css_texto)
    if not m:
        return None, None, "sem @import de fonte no CSS"
    try:
        req = urllib.request.Request(m.group(1), headers={"User-Agent": UA})
        css_fontes = urllib.request.urlopen(req, timeout=25).read().decode("utf-8")
    except Exception as e:  # noqa: BLE001
        return None, None, f"falhou ao buscar o CSS das fontes ({e}) — mantido o @import"

    pasta = destino / "fonts"
    pasta.mkdir(parents=True, exist_ok=True)
    blocos, baixados = [], 0
    for bloco in FONTFACE_RE.findall(css_fontes):
        ur = re.search(r"unicode-range:\s*([^;]+);", bloco)
        if ur and not re.search(r"U\+0000-00FF|U\+0100-02", ur.group(1)):
            continue  # cirílico, grego, vietnamita: não usado pelo conteúdo
        mu = FONTURL_RE.search(bloco)
        if not mu:
            continue
        nome = mu.group(1).rsplit("/", 1)[-1]
        alvo = pasta / nome
        if not alvo.exists():
            try:
                req = urllib.request.Request(mu.group(1), headers={"User-Agent": UA})
                alvo.write_bytes(urllib.request.urlopen(req, timeout=25).read())
                baixados += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ! fonte não baixada ({nome}): {e}")
                continue
        blocos.append(bloco.replace(mu.group(1), f"./fonts/{nome}"))
    if not blocos:
        return None, None, "nenhum @font-face latino encontrado"
    return m.group(0), "\n".join(blocos), f"{len(blocos)} @font-face locais ({baixados} baixadas agora)"


# ----------------------------------------------------------------- transformação
def transformar(html, mapa, import_original=None, fontes_bloco=None):
    # 1. CSS inline (o @import do Google Fonts já vem trocado por @font-face locais)
    for href in re.findall(r'<link rel="stylesheet" href="([^"]+)">', html):
        caminho = BUILD / href.lstrip("/")
        css = caminho.read_text(encoding="utf-8") if caminho.exists() else ""
        if import_original and fontes_bloco:
            css = css.replace(import_original, fontes_bloco, 1)
        html = html.replace(f'<link rel="stylesheet" href="{href}">', f"<style>{css}</style>", 1)

    # 2. imagens e demais recursos servidos pelo site (/imagens/...) -> ./imagens/...
    html = re.sub(r'(src|href)="/(imagens/[^"]+)"', r'\1="./\2"', html)
    html = html.replace("srcset=\"/imagens/", "srcset=\"./imagens/")
    html = html.replace('href="/favicon.svg"', 'href="./favicon.svg"')
    html = html.replace('src="/og-default.png"', 'src="./og-default.png"')
    html = html.replace('src="/favicon.svg"', 'src="./favicon.svg"')

    # 2. links <a ...>
    def tratar_a(match):
        tag = match.group(0)
        m = re.search(r'href="([^"]*)"', tag)
        if not m:
            return tag
        href = m.group(1)
        if href.startswith(("#", "http://", "https://", "mailto:", "./")):
            return tag
        novo = href_local(href, mapa)
        if novo:
            return tag.replace(f'href="{href}"', f'href="{novo}"', 1)
        tag = re.sub(r'\shref="[^"]*"', "", tag, count=1)  # sem par local: vira texto
        return tag.replace("<a ", '<a data-remoto="1" ', 1)

    html = re.sub(r"<a\s[^>]*>", tratar_a, html)

    # 3. aviso de conjunto autônomo
    aviso = (
        '<div style="font:13px/1.5 system-ui,sans-serif;text-align:center;'
        'padding:10px 12px;border-top:1px solid rgba(128,128,128,.35);'
        'opacity:.75">Cópia autônoma do site Estudos Antigos — gerada do build. '
        'Abre sem servidor e sem internet; o tema claro/escuro alterna no botão '
        'do topo.</div>'
    )
    return html.replace("</body>", aviso + "</body>", 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", default=str(DESTINO_PADRAO))
    ap.add_argument("--limpar", action="store_true")
    args = ap.parse_args()

    destino = pathlib.Path(args.destino).resolve()
    if not (BUILD / "index.html").exists():
        sys.exit(f"Build não encontrado em {BUILD}\nRode 'npm run build' antes.")

    mapa = mapa_de_rotas()
    if args.limpar and destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True, exist_ok=True)

    css_base = next((BUILD / "_astro").glob("BaseLayout.*.css")).read_text(encoding="utf-8")
    import_original, fontes_bloco, rel_fontes = preparar_fontes(css_base, destino)
    print(f"fontes: {rel_fontes}")
    print(f"rotas mapeadas: {len(mapa)}")
    print(f"destino: {destino}\n")

    escritos, problemas = [], []
    for p in sorted(BUILD.rglob("*.html")):
        rota = rota_de(p)
        nome = mapa[rota]
        saida = transformar(p.read_text(encoding="utf-8"), mapa, import_original, fontes_bloco)
        if "/_astro/" in saida:
            problemas.append(f"{nome}: ainda referencia /_astro/")
        if "<style>" not in saida:
            problemas.append(f"{nome}: sem CSS inlined")
        (destino / nome).write_text(saida, encoding="utf-8")
        escritos.append((nome, (destino / nome).stat().st_size))

    for extra in EXTRAS:
        origem = BUILD / extra
        if origem.exists():
            shutil.copy2(origem, destino / extra)

    # imagens do site (public/imagens) entram na cópia autônoma
    origem_img = RAIZ / "public" / "imagens"
    n_img = 0
    if origem_img.exists():
        shutil.copytree(origem_img, destino / "imagens", dirs_exist_ok=True)
        n_img = sum(1 for p in (destino / "imagens").rglob("*") if p.is_file())
        peso_img = sum(p.stat().st_size for p in (destino / "imagens").rglob("*") if p.is_file())
        print(f"imagens copiadas: {n_img} ({peso_img / 1024 / 1024:.1f} MB)")

    escritos.sort(key=lambda x: x[1])
    print(f"páginas escritas: {len(escritos)}")
    print(f"menor: {escritos[0][0]} ({escritos[0][1] // 1024} KB) · "
          f"maior: {escritos[-1][0]} ({escritos[-1][1] // 1024} KB)")
    print(f"total html: {sum(b for _, b in escritos) / 1024 / 1024:.1f} MB")

    faltando, inertes = set(), 0
    for nome, _ in escritos:
        txt = (destino / nome).read_text(encoding="utf-8")
        inertes += txt.count("data-remoto")
        for alvo in re.findall(r'href="\./([^"#]+)', txt):
            if not (destino / alvo).exists():
                faltando.add(f"{nome} -> {alvo}")
    print(f"links locais quebrados: {len(faltando)}")
    for f in sorted(faltando)[:10]:
        print("   ", f)
    print(f"links internos sem par local (nestas páginas): {inertes}")
    if problemas:
        print("PROBLEMAS:")
        for p in problemas:
            print("   ", p)
    else:
        print("sanidade: OK (nenhum /_astro/ remanescente, CSS inlined em todas)")


if __name__ == "__main__":
    main()

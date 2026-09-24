#!/usr/bin/env python3
"""
Gerador de dossiê multi-formato a partir de master .md (v4).

Melhorias: badges coloridos em TODOS os marcadores [X]; PDF com
capa+sumário+corpo separados; HTML light/dark com sidebar sticky
e variáveis CSS.
"""
from __future__ import annotations
import re, io, json, sys
from pathlib import Path
from typing import List, Tuple

import markdown
from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos
from PIL import Image
from pypdf import PdfWriter, PdfReader


INPUT = Path(r"C:/Users/music/estudos-antigos/dossies/sumeria/00_sumeria_MASTER.md")
OUTDIR = INPUT.parent
TITLE = "A Civilização Suméria: O Berço da Civilização"
FONT_R = r"C:/Windows/Fonts/arial.ttf"
FONT_B = r"C:/Windows/Fonts/arialbd.ttf"
FONT_I = r"C:/Windows/Fonts/ariali.ttf"

# Figuras embutidas no PDF: 150 mm de largura a ~150 dpi = 886 px. É o que
# basta para a mancha; o HTML fica com as figuras em tamanho cheio (1100 px).
PDF_LARGURA_PX = 900
PDF_QUALIDADE = 74

BADGE_COLORS = {
    "[V]":       ("#2e7d32", "#e8f5e9"),
    "[V-OL]":    ("#2e7d32", "#e8f5e9"),
    "[V-WP]":    ("#2e7d32", "#e8f5e9"),
    "[W]":       ("#1565c0", "#e3f2fd"),
    "[ACAD]":    ("#6a1b9a", "#f3e5f5"),
    "[BLOG]":    ("#e65100", "#fff3e0"),
    "[SITE]":    ("#37474f", "#eceff1"),
    "[YT]":      ("#c62828", "#ffebee"),
    "[CD]":       ("#00695c", "#e0f2f1"),
    "[NV]":      ("#b71c1c", "#ffebee"),
    "[HIST]":    ("#4e342e", "#efebe9"),
    "[DIGITAL]": ("#2e7d32", "#e8f5e9"),
    "[—]":        ("#757575", "#f5f5f5"),
}


def badge_html(marker: str) -> str:
    fg, bg = BADGE_COLORS.get(marker, ("#555", "#f0f0f0"))
    return (f'<span class="badge" style="background:{bg};color:{fg};'
            f'border:1px solid {fg};padding:2px 7px;border-radius:4px;'
            f'font-size:0.72rem;font-weight:700;margin-right:5px;'
            f'transform:translateY(-1px);display:inline-block">{marker}</span>')


def strip_badges(line: str) -> str:
    return re.sub(r'^\[[A-Z\-—]+\]\s*', '', line).strip()


def clean_pdf_text(s: str) -> str:
    # Arial (arial.ttf) não tem glifos devanágari/CJK: o nome de usuário do
    # Commons que aparece num crédito vira a transliteração, e o que sobrar
    # fora do repertório da fonte é removido — senão o fpdf2 avisa de glifo
    # ausente e o PDF sai com quadradinhos.
    s = s.replace("पाटलिपुत्र", "Pataliputra")
    s = re.sub(r"[\u0900-\u097F\u0980-\u09FF\u0E00-\u0E7F\u3040-\u30FF\u4E00-\u9FFF]",
               "", s)
    return (s.replace("—", "-").replace("–", "-").replace("…", "...")
            .replace("触发", "Trigger").replace("发", "a"))


def extract_toc(html_body: str) -> List[Tuple[int, str, str]]:
    """Extrai (level, title, anchor) do HTML gerado pelo markdown."""
    out = []
    for m in re.finditer(r'<h([1-6])\s+id="([^"]+)">(.*?)</h\1>', html_body, re.S):
        lvl = int(m.group(1))
        anchor = m.group(2)
        title = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        out.append((lvl, title, anchor))
    return out


def apply_badges(html: str) -> str:
    """Substitui [X] dentro de <li> por badge colorido.

    O markdown gera 4 variantes:
      <li><strong>[X]</strong>          (ul com bold)
      <li>[X]                          (ul sem bold)
      <li><p><strong>[X]</strong>      (ol com bold)
      <li><p>[X]                      (ol sem bold)
    Uma única regex com 2 grupos captura todas."""
    pat = re.compile(
        r'(<li[^>]*>(?:\s*<p[^>]*>)?)\s*(?:<strong>)?(\[[A-Z\-—]+\])(?:</strong>)?'
    )
    return pat.sub(lambda m: m.group(1) + badge_html(m.group(2)), html)


# --- figuras ---------------------------------------------------------------
# Convenção no MASTER.md (markdown puro, legível no arquivo e nas duas saídas):
#
#   ![descrição da imagem](imagens/07-warka-vase.jpg)
#
#   **Fig. 7 — Vaso de Warka.** Legenda em duas ou três frases. *Ficha: ...*
#
# O parágrafo de imagem e o de legenda viram um <figure> com <figcaption> no
# HTML; o PDF desenha a imagem e escreve a legenda em corpo pequeno.

FIG_HTML = re.compile(
    r'<p>\s*<img([^>]*?)src="(imagens/[^"]+)"([^>]*?)>\s*</p>'
    r'(?:\s*<p>(.*?)</p>)?', re.S)
FIG_MD = re.compile(r'^!\[(.*?)\]\((imagens/[^)]+)\)\s*$')
LINK_MD = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def sem_marcacao(texto: str) -> str:
    """Tira marcação markdown e entidades do texto da legenda (para o PDF)."""
    t = LINK_MD.sub(r'\1 (\2)', texto)
    t = t.replace("**", "").replace("__", "").replace("*", "").replace("`", "")
    t = re.sub(r'<[^>]+>', '', t)
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&nbsp;", " ").replace("&quot;", '"'))
    return re.sub(r'\s+', ' ', t).strip()


def envolver_figuras(html: str) -> str:
    def sub(m: re.Match) -> str:
        alt = re.search(r'alt="([^"]*)"', m.group(1) + m.group(3))
        alt = alt.group(1) if alt else ""
        legenda = m.group(4) or ""
        return ('<figure class="figura">'
                f'<img src="{m.group(2)}" alt="{alt}" loading="lazy" decoding="async">'
                f'<figcaption>{legenda}</figcaption></figure>')
    return FIG_HTML.sub(sub, html)


class DossierPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_font("Arial", "", FONT_R)
        self.add_font("Arial", "B", FONT_B)
        self.add_font("Arial", "I", FONT_I)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Arial", "I", 7)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, TITLE, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(200, 200, 200)
            self.line(10, 18, 200, 18)
            self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}", align=Align.C)

    def cover(self):
        self.add_page()
        self.ln(65)
        self.set_font("Arial", "B", 26)
        self.set_text_color(60, 30, 10)
        self.multi_cell(190, 13, TITLE, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)
        self.set_font("Arial", "", 11)
        self.set_text_color(100, 100, 100)
        self.multi_cell(190, 7, "Dossie academico em 4 formatos", align=Align.C,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.multi_cell(190, 7, "Elaborado em 15 set 2026", align=Align.C,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def toc_page(self, sections, figuras=None):
        self.add_page()
        self.set_font("Arial", "B", 15)
        self.set_text_color(60, 30, 10)
        self.multi_cell(190, 9, "Sumario", align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_font("Arial", "", 9)
        for lvl, title, anchor in sections:
            self.multi_cell(190, 4.5, "    " * (lvl - 1) + title,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if figuras:
            self.ln(4)
            self.set_font("Arial", "B", 11)
            self.set_text_color(60, 30, 10)
            self.multi_cell(190, 6, "Figuras", align=Align.L,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Arial", "", 8)
            self.set_text_color(80, 80, 80)
            for f in figuras:
                self.multi_cell(190, 4, f"Fig. {f['ordem']} — {clean_pdf_text(f['titulo'])}",
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def desenhar_figura(self, caminho: Path, legenda: str) -> None:
        """Imagem centralizada na largura da mancha + legenda em corpo pequeno.

        A imagem é reduzida para caber em 150 mm de largura e 105 mm de altura,
        e quebra de página antes de começar quando não houver espaço para imagem
        e legenda juntas — nunca fica órfã no rodapé.

        O binário embutido é reduzido a `PDF_LARGURA_PX` de largura antes de
        entrar no PDF: as figuras do HTML (1100 px) são maiores do que o PDF
        precisa e, sem esta redução, 37 imagens levariam o arquivo a ~10 MB.
        A compactação posterior via pypdf não serve para isso: no pypdf 6.x,
        `set_data` recusa streams com filtro diferente de FlateDecode, e todo
        JPEG embutido (DCTDecode) passa em silêncio sem redução.
        """
        try:
            with Image.open(caminho) as im:
                lw, lh = im.size
                im = im.convert("RGB")
                if im.width > PDF_LARGURA_PX:
                    im = im.resize((PDF_LARGURA_PX,
                                    round(im.height * PDF_LARGURA_PX / im.width)),
                                   Image.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, format="JPEG", quality=PDF_QUALIDADE,
                        optimize=True, progressive=True)
                buf.seek(0)
        except Exception as e:  # noqa: BLE001
            self.set_font("Arial", "I", 8)
            self.set_text_color(150, 80, 80)
            self.multi_cell(190, 4, f"[figura indisponivel: {caminho.name} — {e}]",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return

        larg = 150.0
        alt = larg * lh / lw
        if alt > 105:
            alt = 105.0
            larg = alt * lw / lh
        texto = clean_pdf_text(sem_marcacao(legenda))
        # estimativa do corpo da legenda: ~95 caracteres por linha de 190 mm a 7,5 pt
        linhas_legenda = max(2, (len(texto) // 95) + 1)
        precisa = alt + linhas_legenda * 3.6 + 6
        if self.get_y() + precisa > self.h - 22:
            self.add_page()

        x = (210 - larg) / 2
        self.image(buf, x=x, y=self.get_y(), w=larg, h=alt)
        self.set_y(self.get_y() + alt + 2.5)
        self.set_font("Arial", "", 7.5)
        self.set_text_color(95, 95, 95)
        self.multi_cell(190, 3.6, texto, align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

    def render_body(self, md_lines):
        in_code = False
        i = 0
        while i < len(md_lines):
            line = md_lines[i]
            s = clean_pdf_text(line).rstrip()
            # --- figura: linha de imagem + parágrafo de legenda seguinte ---
            mfig = FIG_MD.match(line.strip())
            if mfig:
                legenda = ""
                j = i + 1
                while j < len(md_lines) and not md_lines[j].strip():
                    j += 1
                if j < len(md_lines) and not md_lines[j].startswith(("#", "|", "!")):
                    legenda = md_lines[j].strip()
                    i = j
                self.desenhar_figura(INPUT.parent / mfig.group(2).strip(), legenda)
                i += 1
                continue
            if s.strip().startswith("```"):
                in_code = not in_code
                i += 1
                continue
            if in_code:
                self.set_font("Arial", "", 7)
                self.set_text_color(80, 80, 80)
                self.multi_cell(190, 4, s[:280], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                i += 1
                continue
            m = re.match(r'^(#{1,6})\s+(.*)', s)
            if m:
                lvl = len(m.group(1))
                t = strip_badges(m.group(2))
                fmt = {1: ("B", 14, 60, 30, 10, 7), 2: ("B", 11, 60, 30, 10, 6),
                       3: ("B", 9, 40, 40, 40, 5), 4: ("B", 8, 40, 40, 40, 4)}
                st = fmt.get(lvl, fmt[4])
                self.set_font("Arial", st[0], st[1])
                self.set_text_color(st[2], st[3], st[4])
                self.multi_cell(190, st[5] + 1, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.ln(0.5)
                i += 1
                continue
            if s.startswith("|") and "---" not in s:
                self.set_font("Arial", "", 7)
                self.multi_cell(190, 4, " | ".join(c.strip() for c in s.split("|") if c.strip())[:210],
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                i += 1
                continue
            if s.strip() == "---":
                self.set_draw_color(200, 200, 200)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(1.5)
                i += 1
                continue
            self.set_font("Arial", "", 9)
            self.set_text_color(60, 60, 60)
            if s.startswith(("- ", "* ")):
                t = re.sub(r'\[([A-Z\-—]+)\]', r'[\1]', s.lstrip("- *").strip())[:480]
                self.multi_cell(190, 5, "  - " + t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif s:
                self.multi_cell(190, 5, re.sub(r'\[([A-Z\-—]+)\]', r'[\1]', s)[:480],
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            i += 1

    def build(self, md_lines, toc, figuras=None):
        self.cover()
        self.toc_page(toc, figuras)
        self.add_page()
        self.render_body(md_lines)



CSS = """
:root {
  --bg:#fff; --fg:#1a1a1a; --muted:#555; --link:#1565c0;
  --accent:#6b4423; --border:#ddd; --sidebar-bg:#fafafa;
}
*{box-sizing:border-box}
body{font-family:Georgia,'Times New Roman',serif;margin:0;padding:0;
     background:var(--bg);color:var(--fg);line-height:1.65}
.container{display:flex;min-height:100vh}
.sidebar{width:280px;min-width:280px;background:var(--sidebar-bg);
         border-right:1px solid var(--border);padding:1.2rem .8rem;
         position:sticky;top:0;height:100vh;overflow-y:auto}
.sidebar h2{font-size:.9rem;margin:0 0 .5rem;color:var(--accent)}
.sidebar ul{list-style:none;padding:0;margin:0}
.sidebar li{margin:.12rem 0}
.sidebar li.level-3{margin-left:12px;font-size:.86rem}
.sidebar li.level-4{margin-left:22px;font-size:.8rem}
.sidebar a{color:var(--link);text-decoration:none;font-size:.86rem}
.sidebar a:hover{text-decoration:underline}
.main{flex:1;padding:2rem 2.5rem;max-width:960px}
.main h1{color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:.4rem}
.main h2{color:var(--accent);margin-top:2rem;border-bottom:1px solid var(--border);padding-bottom:.3rem}
.main h3{color:#333;margin-top:1.5rem}
.main a{color:var(--link)}
.main code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:.9em}
.main pre{background:#f4f4f4;padding:1rem;overflow-x:auto;border-radius:6px}
.main blockquote{border-left:4px solid var(--accent);padding-left:1rem;color:#555;font-style:italic}
table{border-collapse:collapse;width:100%;margin:1rem 0}
th,td{border:1px solid var(--border);padding:6px 10px;text-align:left}
th{background:var(--sidebar-bg)}
.badge{display:inline-block;padding:2px 7px;border-radius:4px;font-size:.72rem;
       font-weight:700;border:1px solid;margin-right:5px;vertical-align:middle}
figure.figura{margin:1.7rem 0;padding:0;break-inside:avoid;page-break-inside:avoid}
figure.figura img{display:block;width:100%;max-width:520px;height:auto;margin:0 auto;
                  border:1px solid var(--border);border-radius:6px}
figure.figura figcaption{margin:.6rem auto 0;max-width:520px;font-size:.86rem;
                         color:var(--muted);line-height:1.55;text-align:left}
figure.figura figcaption strong{color:var(--fg)}
figure.figura figcaption em{display:block;margin-top:.25rem;font-size:.78rem;
                            color:var(--muted)}
figure.figura figcaption a{color:var(--link)}
[data-theme="dark"] figure.figura img{border-color:#444}
[data-theme="dark"] {
  --bg:#1a1a2e; --fg:#e0e0e0; --muted:#aaa; --link:#64b5f6;
  --accent:#d4a574; --border:#333; --sidebar-bg:#16213e;
}
[data-theme="dark"] .main h3{color:#ccc}
[data-theme="dark"] code{background:#2a2a3e}
[data-theme="dark"] pre{background:#2a2a3e}
[data-theme="dark"] th{background:#0f3460}
[data-theme="dark"] blockquote{color:#aaa;border-left-color:var(--accent)}

@media(max-width:1000px){
.container{flex-direction:column}
.sidebar{width:100%;min-width:100%;height:auto;position:static;border-right:none;
         border-bottom:1px solid var(--border);padding:.8rem 1rem}
.sidebar ul{display:flex;flex-wrap:wrap;gap:.3rem .8rem}
.sidebar li.level-3,.sidebar li.level-4{margin-left:0}
.main{max-width:100%;padding:1rem 1.2rem;text-align:justify}
.main h1{font-size:1.5rem}
}
@media(max-width:600px){
.sidebar ul{flex-direction:column}
.main{padding:.8rem}
.main h1{font-size:1.2rem}
.main h2{font-size:1.05rem}
}
"""

JS = """<script>
(function(){var t=localStorage.getItem('dossier-theme');if(t)document.documentElement.setAttribute('data-theme',t);
var b=document.getElementById('theme-toggle');
if(b)b.addEventListener('click',function(){var c=document.documentElement.getAttribute('data-theme');
var n=c==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);
localStorage.setItem('dossier-theme',n);});})();
</script>"""

BTN = ('<button id="theme-toggle" style="position:fixed;top:10px;right:10px;z-index:999;'
       'padding:6px 14px;border-radius:6px;border:1px solid var(--border);'
       'background:var(--sidebar-bg);color:var(--fg);cursor:pointer;font-size:.82rem">'
       'Alterar tema</button>')


def compact_pdf(p: Path):
    """Reduz imagens em FlateDecode já embutidas no PDF.

    ATENÇÃO: no pypdf 6.x `set_data` recusa qualquer stream com filtro diferente
    de FlateDecode ("Streams encoded with a filter different from FlateDecode are
    not supported"). Como o fpdf2 embute JPEG como DCTDecode, este passo NÃO
    reduz as figuras — quem controla o tamanho do PDF é a redução feita antes de
    embutir (PDF_LARGURA_PX/PDF_QUALIDADE, em `desenhar_figura`). O relatório
    abaixo diz quantas imagens ficaram de fora, para o passo não voltar a
    "funcionar" em silêncio sem fazer nada.
    """
    try:
        r = PdfReader(str(p))
        w = PdfWriter(clone_from=r)
        reduzidas = ignoradas = 0
        for pg in w.pages:
            if "/Resources" not in pg or "/XObject" not in pg["/Resources"]:
                continue
            xo = pg["/Resources"]["/XObject"]
            if hasattr(xo, "get_object"):
                xo = xo.get_object()
            for n in list(xo.keys()):
                x = xo[n]
                if x.get("/Subtype") != "/Image":
                    continue
                filtro = x.get("/Filter")
                if filtro not in (None, "/FlateDecode"):
                    ignoradas += 1
                    continue
                try:
                    dw, dh = int(x["/Width"]), int(x["/Height"])
                    if dw > 250 and dh > 250:
                        img = Image.open(io.BytesIO(x.get_data()))
                        img.thumbnail((1000, 1000), Image.LANCZOS)
                        b = io.BytesIO()
                        img.save(b, format="JPEG", quality=70, optimize=True)
                        if len(b.getvalue()) < len(x.get_data()):
                            x.set_data(b.getvalue())
                            x["/Width"], x["/Height"] = img.width, img.height
                            reduzidas += 1
                except Exception:  # noqa: BLE001
                    ignoradas += 1
        tmp = p.with_suffix(".tmp.pdf")
        with open(tmp, "wb") as f:
            w.write(f)
        tmp.replace(p)
        if ignoradas:
            print(f"  (compactacao: {reduzidas} reduzidas, {ignoradas} ignoradas "
                  f"— JPEG/DCTDecode nao e compactavel pelo pypdf 6.x; o tamanho "
                  f"ja vem controlado da reducao antes de embutir)", file=sys.stderr)
    except Exception as e:
        print(f"Aviso: compactacao de imagens: {e}", file=sys.stderr)


def carregar_figuras() -> list[dict]:
    """Manifesto de figuras (dossies/sumeria/figuras.json), se já houver."""
    p = OUTDIR / "figuras.json"
    if not p.exists():
        return []
    dados = json.loads(p.read_text(encoding="utf-8"))
    return sorted(dados.get("figuras", []), key=lambda f: f["ordem"])


def main():
    md_text = INPUT.read_text(encoding="utf-8")
    md_lines = md_text.splitlines()
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])
    html_body = apply_badges(html_body)
    html_body = envolver_figuras(html_body)
    toc = extract_toc(html_body)
    figuras = carregar_figuras()

    # TOC sidebar
    toc_html = "<ul>"
    for lvl, title, anchor in toc:
        cls = f' class="level-{lvl}"' if lvl > 2 else ''
        toc_html += f'<li{cls}><a href="#{anchor}">{title}</a></li>'
    toc_html += "</ul>"

    page = f"""<!DOCTYPE html>
<html lang="pt-BR"{{theme}}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{TITLE}</title>
<style>{CSS}</style>
</head>
<body>
{BTN}
<div class="container">
<nav class="sidebar"><h2>Sumário</h2>{toc_html}</nav>
<main class="main">
{html_body}
</main>
</div>
{JS}
</body>
</html>"""

    (OUTDIR / "00_sumeria.html").write_text(page.replace("{theme}", ""), encoding="utf-8")
    (OUTDIR / "00_sumeria_dark.html").write_text(page.replace("{theme}", ' data-theme="dark"'), encoding="utf-8")

    pdf = DossierPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.build(md_lines, toc, figuras)
    pdf_path = OUTDIR / "00_sumeria.pdf"
    pdf.output(str(pdf_path))
    compact_pdf(pdf_path)

    print(f"PDF:  {pdf_path} ({pdf_path.stat().st_size/1024:.1f} KB, {len(PdfReader(str(pdf_path)).pages)} pag.)")
    print(f"HTML: {OUTDIR/'00_sumeria.html'} (light) + _dark.html")
    print(f"Figuras: {len(figuras)} no manifesto; "
          f"{len(re.findall(r'<figure class=.figura.>', page))} desenhadas no HTML")

    # Stats
    badges_found = re.findall(r'class="badge"[^>]*>(\[[A-Z\-—]+\])</span>', page)
    print(f"Badges: {len(badges_found)} aplicados ({len(set(badges_found))} tipos)")


if __name__ == "__main__":
    main()

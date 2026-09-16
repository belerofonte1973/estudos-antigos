#!/usr/bin/env python3
"""
Gerador de dossiê multi-formato a partir de master .md (v4).

Melhorias: badges coloridos em TODOS os marcadores [X]; PDF com
capa+sumário+corpo separados; HTML light/dark com sidebar sticky
e variáveis CSS.
"""
from __future__ import annotations
import re, io, sys
from pathlib import Path
from typing import List, Tuple

import markdown
from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos
from PIL import Image
from pypdf import PdfWriter, PdfReader


INPUT = Path(r"C:/Users/music/estudos-antigos/dossies/antigo-egito/00_antigo_egito_MASTER.md")
OUTDIR = INPUT.parent
TITLE = "Antigo Egito — Dossiê"
FONT_R = r"C:/Windows/Fonts/arial.ttf"
FONT_B = r"C:/Windows/Fonts/arialbd.ttf"
FONT_I = r"C:/Windows/Fonts/ariali.ttf"

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

    def toc_page(self, sections):
        self.add_page()
        self.set_font("Arial", "B", 15)
        self.set_text_color(60, 30, 10)
        self.multi_cell(190, 9, "Sumario", align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_font("Arial", "", 9)
        for lvl, title, anchor in sections:
            self.multi_cell(190, 4.5, "    " * (lvl - 1) + title,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def render_body(self, md_lines):
        in_code = False
        for line in md_lines:
            s = clean_pdf_text(line).rstrip()
            if s.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                self.set_font("Arial", "", 7)
                self.set_text_color(80, 80, 80)
                self.multi_cell(190, 4, s[:280], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
                continue
            if s.startswith("|") and "---" not in s:
                self.set_font("Arial", "", 7)
                self.multi_cell(190, 4, " | ".join(c.strip() for c in s.split("|") if c.strip())[:210],
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                continue
            if s.strip() == "---":
                self.set_draw_color(200, 200, 200)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(1.5)
                continue
            self.set_font("Arial", "", 9)
            self.set_text_color(60, 60, 60)
            if s.startswith(("- ", "* ")):
                t = re.sub(r'\[([A-Z\-—]+)\]', r'[\1]', s.lstrip("- *").strip())[:480]
                self.multi_cell(190, 5, "  - " + t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif s:
                self.multi_cell(190, 5, re.sub(r'\[([A-Z\-—]+)\]', r'[\1]', s)[:480],
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def build(self, md_lines, toc):
        self.cover()
        self.toc_page(toc)
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
.main{flex:1;padding:2rem 2.5rem;max-width:960px;text-align:justify}
.main h1{color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:.4rem}
.main h2{color:var(--accent);margin-top:2rem;border-bottom:1px solid var(--border);padding-bottom:.3rem}
.main h3{color:#333;margin-top:1.5rem}
.main a{color:var(--link)}
.main p{text-align:justify}
.main code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:.9em}
.main pre{background:#f4f4f4;padding:1rem;overflow-x:auto;border-radius:6px}
.main blockquote{border-left:4px solid var(--accent);padding-left:1rem;color:#555;font-style:italic}
table{border-collapse:collapse;width:100%;margin:1rem 0}
th,td{border:1px solid var(--border);padding:6px 10px;text-align:left}
th{background:var(--sidebar-bg)}
.badge{display:inline-block;padding:2px 7px;border-radius:4px;font-size:.72rem;
       font-weight:700;border:1px solid;margin-right:5px;vertical-align:middle}
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
    try:
        r = PdfReader(str(p))
        w = PdfWriter(clone_from=r)
        for pg in w.pages:
            if "/Resources" in pg and "/XObject" in pg["/Resources"]:
                xo = pg["/Resources"]["/XObject"]
                if hasattr(xo, "get_object"):
                    xo = xo.get_object()
                for n in list(xo.keys()):
                    x = xo[n]
                    if x.get("/Subtype") == "/Image":
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
                        except Exception:
                            pass
        tmp = p.with_suffix(".tmp.pdf")
        with open(tmp, "wb") as f:
            w.write(f)
        tmp.replace(p)
    except Exception as e:
        print(f"Aviso: compactacao de imagens: {e}", file=sys.stderr)


def main():
    md_text = INPUT.read_text(encoding="utf-8")
    md_lines = md_text.splitlines()
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])
    html_body = apply_badges(html_body)
    toc = extract_toc(html_body)

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

    (OUTDIR / "00_antigo_egito.html").write_text(page.replace("{theme}", ""), encoding="utf-8")
    (OUTDIR / "00_antigo_egito_dark.html").write_text(page.replace("{theme}", ' data-theme="dark"'), encoding="utf-8")

    pdf = DossierPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.build(md_lines, toc)
    pdf_path = OUTDIR / "00_antigo_egito.pdf"
    pdf.output(str(pdf_path))
    compact_pdf(pdf_path)

    print(f"PDF:  {pdf_path} ({pdf_path.stat().st_size/1024:.1f} KB, {len(PdfReader(str(pdf_path)).pages)} pag.)")
    print(f"HTML: {OUTDIR/'00_antigo_egito.html'} (light) + _dark.html")

    # Stats
    badges_found = re.findall(r'class="badge"[^>]*>(\[[A-Z\-—]+\])</span>', page)
    print(f"Badges: {len(badges_found)} aplicados ({len(set(badges_found))} tipos)")


if __name__ == "__main__":
    main()

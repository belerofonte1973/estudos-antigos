import re
from pathlib import Path

html = Path(r"C:/Users/music/estudos-antigos/dossies/antigo-egito/antigo-egito-completo.html").read_text(encoding='utf-8')

# Extract the dossier section (PARTE I onwards)
match = re.search(r'<h2 id="parte-i-bibliografia-academica">.*', html, re.DOTALL)
if not match:
    print("No dossier section found")
    exit(1)

dossier_html = match.group(0)
dossier_html = re.sub(r'</main>\s*</div>\s*</body>\s*</html>', '', dossier_html)
dossier_html = re.sub(r'<nav.*?</nav>', '', dossier_html, flags=re.DOTALL)

# Convert headers
dossier_html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', dossier_html)
dossier_html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', dossier_html)
dossier_html = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', dossier_html)

# Convert paragraphs
dossier_html = re.sub(r'<p>(.*?)</p>', r'\1\n', dossier_html, flags=re.DOTALL)

# Convert lists
dossier_html = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', dossier_html, flags=re.DOTALL)
dossier_html = re.sub(r'<ol[^>]*>', '', dossier_html)
dossier_html = re.sub(r'</ol>', '', dossier_html)
dossier_html = re.sub(r'<ul[^>]*>', '', dossier_html)
dossier_html = re.sub(r'</ul>', '', dossier_html)

# Convert links
dossier_html = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', dossier_html)

# Convert formatting
dossier_html = re.sub(r'<strong>(.*?)</strong>', r'**\1**', dossier_html)
dossier_html = re.sub(r'<em>(.*?)</em>', r'*\1*', dossier_html)
dossier_html = re.sub(r'<code>(.*?)</code>', r'`\1`', dossier_html)

# Convert blockquotes
dossier_html = re.sub(r'<blockquote>(.*?)</blockquote>', r'> \1', dossier_html, flags=re.DOTALL)

# Convert tables
dossier_html = re.sub(r'<table[^>]*>', '\n', dossier_html)
dossier_html = re.sub(r'</table>', '\n', dossier_html)
dossier_html = re.sub(r'<thead[^>]*>', '', dossier_html)
dossier_html = re.sub(r'</thead>', '', dossier_html)
dossier_html = re.sub(r'<tbody[^>]*>', '', dossier_html)
dossier_html = re.sub(r'</tbody>', '', dossier_html)
dossier_html = re.sub(r'<tr[^>]*>', '| ', dossier_html)
dossier_html = re.sub(r'</tr>', ' |', dossier_html)
dossier_html = re.sub(r'<th[^>]*>(.*?)</th>', r' **\1** |', dossier_html)
dossier_html = re.sub(r'<td[^>]*>(.*?)</td>', r' \1 |', dossier_html)

# Remove remaining HTML tags
dossier_html = re.sub(r'<[^>]+>', '', dossier_html)

# Clean up whitespace
dossier_html = re.sub(r'\n{3,}', '\n\n', dossier_html)
dossier_html = dossier_html.strip()

# Write to file
Path(r"C:/Users/music/estudos-antigos/dossies/antigo-egito/dossie_content.md").write_text(dossier_html, encoding='utf-8')
print(f"Done. Total chars: {len(dossier_html)}")
print("First 500 chars:")
print(dossier_html[:500])

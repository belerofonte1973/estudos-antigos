import re
from pathlib import Path

html = Path(r"C:/Users/music/estudos-antigos/dossies/antigo-egito/antigo-egito-completo.html").read_text(encoding='utf-8')

# Find the article section (from "Artigo Enciclopédico" to "Referências do Dossiê")
# The HTML has the structure: ... <h2 id="artigo-enciclopédico">Artigo Enciclopédico</h2> ... <h2 id="referências-do-dossiê">Referências do Dossiê</h2>

# Extract article content (between artigo-enciclopédico and referências-do-dossiê)
art_match = re.search(r'<h2[^>]*id="artigo-enciclopédico"[^>]*>.*?<h2[^>]*id="referências-do-dossiê"[^>]*>', html, re.DOTALL)
if not art_match:
    print("Could not find article section")
    exit(1)

article_html = art_match.group(0)
# Remove the last <h2> tag
article_html = re.sub(r'<h2[^>]*id="referências-do-dossiê"[^>]*>.*$', '', article_html)

# Extract references section (from referências-do-dossiê onwards, before sidebar end)
ref_match = re.search(r'<h2[^>]*id="referências-do-dossiê"[^>]*>.*?</article>', html, re.DOTALL)
if not ref_match:
    print("Could not find references section")
    exit(1)

ref_html = ref_match.group(0)
# Remove </article> at the end
ref_html = re.sub(r'</article>\s*$', '', ref_html)

def html_to_md(text):
    """Simple HTML to markdown conversion."""
    # Headers
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', text, flags=re.DOTALL)
    
    # Paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', text, flags=re.DOTALL)
    
    # Lists
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
    text = re.sub(r'<[ou]l[^>]*>', '', text)
    text = re.sub(r'</[ou]l>', '', text)
    
    # Links
    text = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)
    
    # Formatting
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)
    
    # Blockquotes
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', text, flags=re.DOTALL)
    
    # Line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)
    
    # Tables - simplified
    text = re.sub(r'<table[^>]*>', '\n', text)
    text = re.sub(r'</table>', '\n', text)
    text = re.sub(r'<thead[^>]*>', '', text)
    text = re.sub(r'</thead>', '', text)
    text = re.sub(r'<tbody[^>]*>', '', text)
    text = re.sub(r'</tbody>', '', text)
    text = re.sub(r'<tr[^>]*>', '| ', text)
    text = re.sub(r'</tr>', ' |\n', text)
    text = re.sub(r'<th[^>]*>(.*?)</th>', r'**\1** |', text)
    text = re.sub(r'<td[^>]*>(.*?)</td>', r'\1 |', text)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'  +', ' ', text)
    text = text.strip()
    
    return text

article_md = html_to_md(article_html)
ref_md = html_to_md(ref_html)

# Save for inspection
Path(r"C:/Users/music/estudos-antigos/dossies/antigo-egito/article_part.md").write_text(article_md, encoding='utf-8')
Path(r"C:/Users/music/estudos-antigos/dossies/antigo-egito/ref_part.md").write_text(ref_md, encoding='utf-8')

print(f"Article part: {len(article_md)} chars")
print(f"References part: {len(ref_md)} chars")
print("\n=== Article first 800 chars ===")
print(article_md[:800])
print("\n=== References first 800 chars ===")
print(ref_md[:800])

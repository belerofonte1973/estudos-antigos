import pathlib, re
p = pathlib.Path(r'C:\Users\music\AppData\Local\hermes\skills\research\pesquisador-bibliografico\SKILL.md')
text = p.read_text(encoding='utf-8')
# inserir linha após a linha que contém templates-civilizacao-e-prehistoria
old = '| artigo de **civilização** ou **pré-história humana** | `templates-civilizacao-e-prehistoria.md` |'
new = '| artigo de **civilização** ou **pré-história humana** | `templates-civilizacao-e-prehistoria.md` |\n| pesquisadores (ranking, identidade, produção) | `prehistory-researchers.md` |'
if old in text:
    text = text.replace(old, new, 1)
    p.write_text(text, encoding='utf-8')
    print('PATCH OK')
else:
    print('OLD NOT FOUND')
    for i, l in enumerate(text.splitlines()[34:42], start=35):
        print(f'{i}: {l}')

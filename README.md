# Estudos Antigos

Portal de divulgação sobre Antiguidade Bíblica, Clássica e Medieval.
Cada afirmação factual carrega citação rastreável a fonte primária.

## Duas superfícies, um build

| Superfície | Rota | Natureza |
|---|---|---|
| **Revista** | `/artigos/<pergunta>/` | artigos curtos, **uma pergunta por endereço**. Motor de alcance. |
| **Biblioteca** | `/biblioteca/<área>/<slug>/` | dossiês longos com aparato acadêmico. Destino. |

A revista existe para ser encontrada; a biblioteca, para ser conferida. Elas se
ligam por links mútuos.

## Por que não há Starlight

O Starlight foi removido de propósito. Ele é um tema de **documentação** —
sidebar primeiro, pressupõe que o leitor já sabe o que procura. A face pública
precisa do oposto: `<head>` livre para SEO, schema.org e imagem social.

Os componentes do Starlight usados pelo conteúdo foram substituídos por
equivalentes próprios em `src/components/` (`Card`, `CardGrid`, `Aside`,
`LinkButton`, `Icon`). Os nomes de ícone do conteúdo (`open-book`, `pencil`,
`document`, `star`) continuam funcionando.

## Comandos

```bash
npm install
npm run dev                # servidor local — http://localhost:4321
npm run build              # build de produção em dist/

python verificar_site.py   # verificação pós-build — SEMPRE após build
node scripts/gerar_og.mjs  # regenera public/og-default.png
```

### O que a verificação confere

`verificar_site.py` roda contra `dist/` e cobre os sintomas que já quebraram
este projeto:

1. conteúdo que não renderizou (termo presente no MDX, ausente no HTML)
2. tokens de corrupção de PT-BR (vazamento de espanhol, normalização cega)
3. diretivas MDX (`:::`) vazando como texto literal
4. canonical, Open Graph, JSON-LD e `lang="pt-BR"`
5. JSON-LD sintaticamente válido, com os tipos esperados
6. links internos que não resolvem
7. feed RSS

Falha com **exit 1** quando encontra problema. É o portão de qualidade.

## Estrutura

```
src/
├── content.config.ts          # coleções: biblioteca + artigos (schemas Zod)
├── content/
│   ├── biblioteca/            # dossiês profundos (MDX)
│   └── artigos/               # revista (MD)
├── components/                # Card, CardGrid, Aside, LinkButton, Icon,
│   │                          # Header, Footer, Breadcrumbs, TableOfContents,
│   │                          # ArticleCard, Seo
├── layouts/
│   ├── BaseLayout.astro       # head, tema, scripts globais
│   ├── ArtigoLayout.astro     # artigo (resposta rápida + fontes + sumário)
│   ├── BibliotecaLayout.astro # dossiê (sidebar + sumário)
│   └── PaginaLayout.astro     # páginas institucionais
├── pages/
│   ├── index.astro            # capa da revista
│   ├── artigos/               # índice + [...slug]
│   ├── biblioteca/            # índice + [area] + [...slug]
│   ├── sobre/                 # projeto, contribua, contato
│   ├── rss.xml.ts
│   └── 404.astro
├── plugins/
│   └── remark-linguas-antigas.mjs   # hebraico/grego: bidi + lang
└── styles/global.css          # design system (Notion Warm Minimalism)
```

## Como escrever um artigo da revista

Um artigo responde **uma** pergunta. O schema exige os campos que fazem o
trabalho de alcance — não são decoração:

```yaml
---
titulo: 'Quem escreveu o Gênesis?'      # manchete para humanos
pergunta: 'Quem escreveu o Gênesis?'    # a consulta literal, como se digita
descricao: '...'                        # MÁX 160 caracteres (o schema rejeita mais)
respostaRapida: '...'                   # 2-4 frases: alimenta FAQPage e trecho em destaque
area: biblia                            # biblia | classica | idade-media | pre-historia | oriente
tags: [Pentateuco, autoria]
data: 2026-09-11
destaque: 1                             # menor aparece primeiro na capa
dossie: biblia/genesis                  # id do dossiê correspondente (link "Aprofundar")
fontes:                                 # viram o bloco Fontes e o schema.org citation
  - texto: 'Baden, Joel S. ... Yale, 2012. ISBN 9780300152647.'
---
```

**Descrição acima de 160 caracteres quebra o build.** É intencional: o Google
trunca além disso, então o excesso é desperdício.

## Armadilhas conhecidas

- **Linha em branco depois dos imports MDX.** Sem ela, o parser interpreta o
  primeiro `<Componente>` como JavaScript e falha com *"Unexpected statement in
  code: only import/exports are supported"*. `corrigir_imports_mdx.py` conserta.
- **Subagentes entregam espanhol reportando "PT-BR limpo".** Nunca confie no
  relatório — verifique o arquivo. A verificação caça `hebreo`, `pueblo`,
  `también`, `Antiguo`, `siglos`. Cuidado com o falso positivo: **"Siglo XXI"** é
  editora legítima.
- **Nunca normalize texto com dicionário de replace cego.** `"no "→"não "` vira
  "não deserto"; `"del"→"do"` vira "modelo"→"modoo".
- **Hebraico e grego não precisam de marcação no MDX.** O plugin
  `remark-linguas-antigas` envolve automaticamente em
  `<span class="he" dir="rtl" lang="he">` e `<span class="grc" lang="grc">`.
  Escreva o texto puro.

## Identidade visual

Notion Warm Minimalism sobre base editorial: **Inter** para interface, **Source
Serif 4** para corpo de leitura longa. Acento siena `#6b4423` (claro) / `#d4a574`
(escuro). Tokens em `src/styles/global.css` — nenhum valor de cor solto nos
componentes.

## SEO

Centralizado em `src/components/Seo.astro`. Cada artigo emite três blocos
JSON-LD: `Article`, `FAQPage` (com `pergunta` + `respostaRapida`) e
`BreadcrumbList`. Os dossiês emitem `ScholarlyArticle`.

## Scripts utilitários

| Arquivo | Função |
|---|---|
| `migrar_conteudo.py` | migração histórica de `docs/` (Starlight) → `biblioteca/`. Já executado. |
| `corrigir_imports_mdx.py` | insere a linha em branco após imports MDX |
| `encurtar_descricoes.py` | ajusta meta descrições ao limite de 160 |
| `verificar_site.py` | verificação pós-build |

## Pendências conhecidas

- **Domínio próprio.** Hoje `estudos-antigos.netlify.app`. Trocar exige editar
  `SITE` e `site:` em `astro.config.mjs`.
- **O site está privado no Netlify** (proteção de acesso ativa) — logo, não é
  indexável. Publicar é o passo que destrava todo o alcance.
- **Imagem social única** (`og-default.png`) para todo o site. Imagem por artigo
  exigiria geração em build (satori) — avaliar depois.
- **Busca interna.** O Starlight trazia Pagefind; alternativa é rodá-lo como
  passo pós-build.

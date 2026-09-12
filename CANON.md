# Plano canônico — os 58 livros e a ordem de produção

Documento de trabalho. Diz **o que falta**, **em que ordem** e **com que regras**.
Foi escrito para que a produção sobreviva à sessão que a começou.

## Estado

A taxonomia (`src/taxonomia.ts`) declara **58 livros** em **4 cânones**. Deles,
**11 entradas já têm dossiê** (9 dossiês cobrem 11 hubs, porque Samuel e Reis são
unidades canônicas: um dossiê cada, dois livros cada).

| Superfície | Hoje |
|---|---|
| Biblioteca — dossiês bíblicos | 9 (Gênesis … Reis) |
| Biblioteca — contexto | Suméria, Pré-História |
| Revista — artigos | 13, todos do núcleo bíblico |
| Passagens | 1 (Gênesis 6–9) |
| Páginas | 59 (hub do núcleo, 4 hubs de cânon, hubs de livro, revista, biblioteca) |

Portões: `python verificar_site.py` (integridade, exit 1) e
`python verificar_eixos.py` (modelo, exit 1). Ambos verdes — 67 verificações.

## Os cânones, e por que estão no site

| Cânon | Livros | O que acrescenta |
|---|---|---|
| Hebraico / protestante | 39 | o denominador comum |
| Católico | 46 | deuterocanônicos (Trento, 1546) |
| Ortodoxo | 52 | 1–2 Esdras, 3–4 Macabeus, Salmo 151, Oração de Manassés |
| Etíope (Tewahedo) | 58 | 1 Enoque, Jubileus, 1–3 Meqabyan, 4 Baruque |

A página `/[cânon]/` de cada tradição lista os seus livros e o que ela recebe a
mais que o hebraico. O cartão de livro fora do cânon hebraico declara a tradição
que o recebe — na grade, não em nota de rodapé.

## Os lotes

Ordem por densidade de material acadêmico disponível e por utilidade para quem
estuda o cânon inteiro. Cada lote é uma leva de dossiês na forma consagrada.

### Lote 1 — Profetas Maiores (5)
`isaias` · `jeremias` · `lamentacoes` · `ezequiel` · `daniel`

### Lote 2 — Os Doze (12)
`oseias` · `joel` · `amos` · `obadias` · `jonas` · `miqueias` · `naum` ·
`habacuque` · `sofonias` · `ageu` · `zacarias` · `malaquias`
*(Decisão: 12 dossiês, um por livro — não um dossiê dos Doze. O cânon hebraico
trata os Doze como um livro, mas cada profeta tem bibliografia própria e é
buscado pelo nome, que é o que a revista explora.)*

### Lote 3 — Históricos restantes (3)
`rute` · `cronicas-1`+`cronicas-2` (um dossiê, `livros: [cronicas-1, cronicas-2]`) ·
`esdras`+`neemias` (um dossiê, `livros: [esdras, neemias]`)

### Lote 4 — Sapienciais (5)
`jo` · `salmos` · `proverbios` · `coelet` · `cantico`

### Lote 5 — Deuterocanônicos (8)
`tobias` · `judite` · `sabedoria` · `eclesiastico` · `baruque` · `macabeus-1` ·
`macabeus-2` · `ester` (adições gregas, tratadas dentro do dossiê de Ester)
*(Baruque inclui a Carta de Jeremias; o dossiê trata as duas.)*

### Lote 6 — Ortodoxos (5 + Oração)
`esdras-1` · `esdras-2` · `macabeus-3` · `macabeus-4` · `oracao-manasses` ·
`salmo-151`

### Lote 7 — Etíopes (6)
`enoque-1` · `jubileus` · `meqabyan-1` · `meqabyan-2` · `meqabyan-3` · `baruque-4`

## Forma do dossiê (obrigatória)

Treze seções, na ordem, mais a bibliografia. Copiar a forma de um dossiê recente
(`biblia/juizes.mdx` é o modelo mais completo):

```
1. Lead e Ficha            8. Audiovisual e Games
2. Contexto e Autoria      9. Mitologia e Literatura Comparada
3. Estrutura (N capítulos) 10. Filosofia — as perguntas que o texto levanta
4. Conteúdos-chave com     11. Teologia — os debates
   Debate (### 4.1 …)         (inclui 11.1 Comentaristas por esfera confessional)
5. Temas                   12. Ciência — o que as ciências dizem, e onde não têm
6. Recepção                13. Lacunas e Correções de Atribuição
7. Traduções PT e          ## Bibliografia-âncora verificada
   Comentários PT            ### Como conseguir estas obras
```

Frontmatter:

```yaml
---
title: '<Livro> (<incipit>) — Artigo Enciclopédico'
description: '...'   # até 160 caracteres
area: biblia
ordem: <n>          # de LIVROS
eixo: nucleo
livro: <slug>       # ou livros: [a, b] para unidade canônica
---
```

## Regras de conteúdo (skill `pesquisador-bibliografico` v5.8)

1. **Regra Zero.** Nunca inventar autor, título, ano, DOI, página. Não achou,
   escreve "não encontrei fonte verificada para X".
2. **Marcadores literais**, sem abreviar: `[V]` ISBN validado em Open Library ·
   `[V-OL]` work record · `[W]` citado em Wikipedia PT refs · `[V-WP]` · `[ACAD]`
   paper com DOI · `[NV]` ISBN testado e não achado · `[HIST]` pré-1980 sem ISBN ·
   `[DIGITAL]` domínio público · `[—]` lacuna.
3. **Citação inline** em cada afirmação factual: `(Autor, Ano, p.X)` ou
   `(Autor, Ano, cap.X)`; 2–3 fontes nas afirmações contestadas.
4. **Quatro camadas obrigatórias** com autores extra-bíblicos nomeados:
   mitologia/literatura comparada (paralelos do ANE), filosofia
   (Espinosa/Kant/Mackie/Rowe/Girard/Douglas), teologia-*debates*
   (von Rad/Noth/Cross/Levenson/Gutiérrez/Rashi), ciência
   (Finkelstein/Dever/Whitcomb/Patterson/Skorecki/Thiele). A seção de ciência
   **precisa declarar onde a ciência não tem competência**.
5. **Comentaristas por esfera confessional** (11.1): judaica, católica,
   ortodoxa, protestante histórica, evangélica — com alvo mensurável.
6. **Bibliografia com selos de acesso** `[livre]`/`[empréstimo]`/`[compra]`/
   `[biblioteca]`/`[esgotado]` e link clicável por obra. Selo é passada de
   conteúdo obra por obra, não decoração.
7. **PT-BR sempre.** Nenhum vazamento de espanhol (`hebreo`, `pueblo`,
   `también`, `siglos`, `Antiguo` fora de "Antiguo Oriente"). Editora "Siglo XXI"
   é legítima.
8. **Hebraico/grego/ge'ez em texto puro** — o plugin remark envolve
   automaticamente. Não marcar à mão.

## Modelo de pesquisa

`deepseek/deepseek-v4.1-flash` (Nous Portal) — 1M de contexto, visão, raciocínio.
Configurado em `delegation.model` para os redatores.

## Fluxo de um lote

1. Redator escreve o dossiê **completo** no caminho final
   (`src/content/biblioteca/biblia/<slug>.mdx`), seguindo a forma e as regras.
2. Pai **verifica o artefato**, não o relatório: frontmatter, treze seções,
   contagem de palavras, marcadores, quatro camadas com nomes, selos, ausência
   de espanhol, ausência de `<` ou `{` solto (MDX).
3. `npm run build` + `python verificar_site.py` + `python verificar_eixos.py`.
4. Commit por lote.

## Pendências que não são dossiê

- Domínio próprio (hoje `estudos-antigos.netlify.app`).
- Site **privado no Netlify** — não indexável. O usuário decidiu: sem pressa;
  primeiro o conteúdo.
- Imagem social por artigo (hoje uma só).
- Busca interna (Pagefind como passo pós-build).
- Artigos-porta para os dossiês que ainda não têm (Suméria e Pré-História não
  têm; os 9 bíblicos têm 7 no total).

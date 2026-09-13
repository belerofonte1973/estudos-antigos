# Plano canônico — os 58 livros e a ordem de produção

Documento de trabalho. Diz **o que falta**, **em que ordem** e **com que regras**.
Foi escrito para que a produção sobreviva à sessão que a começou.

## Estado

A taxonomia (`src/taxonomia.ts`) declara **58 livros** em **4 cânones**. Deles,
**58 entradas — TODAS** (54 dossiês cobrem os 58 livros, porque Samuel, Reis,
Crônicas e Esdras+Neemias são unidades canônicas: um dossiê cada, dois livros
cada). **Faltam 0 — os 58 livros dos 4 cânones estão cobertos.**

| Superfície | Hoje |
|---|---|
| Biblioteca — dossiês bíblicos | **54** = **58 dos 58 livros — COMPLETO** |
| Biblioteca — contexto | Suméria, Pré-História |
| Revista — artigos | 13, todos do núcleo bíblico |
| Passagens | 1 (Gênesis 6–9) |
| Páginas | **151** (hub do núcleo, 4 hubs de cânon, hubs de livro, revista, biblioteca) |

Portões, todos verdes:
`python validar_dossie.py --todos` (forma, ANTES do build) ·
`python verificar_site.py` (integridade, exit 1) ·
`python verificar_eixos.py` (modelo, 67 checagens, exit 1).

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

### Lote 1 — Profetas Maiores (5) — FEITO
`isaias` (8.441 palavras) · `jeremias` (8.384) · `lamentacoes` (8.330) ·
`ezequiel` (8.384) · `daniel` (8.285). Commit `40ce611`. Os cinco passaram com
0 falhas e 0 avisos no validador.

### Lote 2 — Os Doze (12) — FEITO
Primeira metade: `oseias` (8.499 palavras) · `joel` (8.459) · `amos` (8.497) ·
`obadias` (8.243) · `jonas` (8.480) · `miqueias` (8.493).
Segunda metade: `naum` (8.493) · `habacuque` (8.400) · `sofonias` (8.334) ·
`ageu` (8.498) · `zacarias` (8.499) · `malaquias` (8.500).
Os doze passaram o validador com 0 falhas e 0 avisos; build em 93 páginas.
*(Decisão: 12 dossiês, um por livro — não um dossiê dos Doze. O cânon hebraico
trata os Doze como um livro, mas cada profeta tem bibliografia própria e é
buscado pelo nome, que é o que a revista explora.)*

### Lote 3 — Históricos restantes (3) — FEITO
`rute` (8.323 palavras) · `cronicas` (8.282 — um dossiê, `livros: [cronicas-1,
cronicas-2]`) · `esdras-neemias` (8.490 — um dossiê, `livros: [esdras, neemias]`).
Os três passaram o validador com 0 falhas e 0 avisos; build em 101 páginas.
*(Os Históricos estão completos: Gênesis a Ester do bloco histórico, mais Rute.)*

### Lote 4 — Sapienciais (5) — FEITO
`jo` (8.417 palavras) · `salmos` (8.489) · `proverbios` (8.493) · `coelet` (8.490) ·
`cantico` (8.499). Os cinco passaram o validador com 0 falhas e 0 avisos; build em
111 páginas. *(O dossiê dos Salmos declara na §1 o recorte: trata o Saltério como
obra, com salmos individuais analisados como exemplo — não 150 fichas.)*

### Lote 5 — Deuterocanônicos (8) — FEITO
`tobias` (8.495 palavras) · `judite` (8.843) · `ester` (8.474, adições gregas
tratadas dentro) · `macabeus-1` (8.501) · `macabeus-2` (8.498) ·
`sabedoria` (compressão própria posterior: 10.162 → 8.228, com a remoção de
~860 palavras de 4 blocos DUPLICADOS que a re-edição tinha deixado, e correção
de 6 H2 colados no parágrafo anterior) ·
`eclesiastico` (8.480) · `baruque` (8.486, com a Carta de Jeremias). Os oito
passaram com 0 falhas e 0 avisos; build em 127 páginas.
*(O dossiê da Sabedoria chegou com 4 subseções em H2 e 4 títulos duplicados por
reedição — resíduo corrigido à mão e o validador ganhou a checagem de hierarquia:
só as 13 seções + bibliografia podem ser H2, e título duplicado é aviso.)*

### Lote 6 — Ortodoxos (5 + Oração) — FEITO
`esdras-1` (7.794 palavras) · `esdras-2` (8.367) · `oracao-manasses` (7.982) ·
`salmo-151` (7.798) · `macabeus-3` (7.796) · `macabeus-4` (7.792). Os seis
passaram com 0 falhas e 0 avisos; build em 139 páginas. Primeiro lote no Nous
Portal (flash-0731, reasoning high): os briefings de economia seguraram ~7,8k
em uma passada — exceto o 2 Esdras (8.367, apocalipse de 16 capítulos com tabela
tripartida e 7 visões) e a Oração de Manassés (7.982), ambos justificados.

### Lote 7 — Etíopes (6) — FEITO
`enoque-1` (7.790 palavras) · `jubileus` (7.786) · `meqabyan-1` (7.800) ·
`meqabyan-2` (7.309) · `meqabyan-3` (7.596) · `baruque-4` (8.441). Os seis
passaram com 0 falhas e 0 avisos; build em 151 páginas.
*(Os três Meqabyan são os livros menos documentados da série: os dossiês
declaram as lacunas com honestidade — [—]=51/34/28 — em vez de fabricar.
Foi a instrução explícita do briefing e o melhor resultado possível.)*
**OS 58 LIVROS DOS 4 CÂNONES TÊM DOSSIÊ — série fechada em 12/set/2026.**

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

`deepseek/deepseek-v4.1-flash`, com **o provedor escolhido pelo dia e hora** —
mesmo modelo, dois canais de cobrança:

| Quando | Provedor | Comando |
|---|---|---|
| **Fim de semana** (sáb/dom, qualquer hora) | **OpenRouter** (base $0,15/$0,60) | `hermes config set delegation.provider openrouter` |
| Dia útil 13:40–21:00 e madrugada 03:40–07:00 BRT | **OpenRouter** | idem |
| Dia útil no pico 22:40–03:40 e 07:00–13:40 BRT | **Nous Portal** (fixo $0,12/$0,96) | `hermes config set delegation.provider nous` |

O OpenRouter dobra o preço na janela de pico dos dias úteis; o Portal é fixo.
Conferir antes de um lote grande: `https://openrouter.ai/api/v1/models` →
`pricing.prompt`. Trocar no meio da produção é seguro — subagente já iniciado
mantém o provedor com que nasceu.

Configurado em `delegation.model` / `delegation.provider`.

### Economia de tokens na delegação — decidido 12/set/2026

Config de produção atual: `delegation.model` = `deepseek/deepseek-v4-flash-0731` ·
`delegation.provider` = `nous` · `delegation.reasoning_effort` = `high` (alinhado ao
`reasoning_overrides` do agente principal para este modelo; xhigh queimou tokens de
raciocínio sem ganho proporcional).

Por que trocou o provedor: os créditos do OpenRouter esgotaram com 8 subagentes em
voo — HTTP 402, a reserva de requisições simultâneas estoura o saldo. Saldo medido
na API (`/api/v1/credits`): 0,65 USD de 140 USD comprados. O Nous Portal roda a
sessão principal há tempo e tem preço fixo.

**A maior perda de tokens NÃO é o modelo: é o estouro do teto de palavras.** Medido
na produção: Oséias 10.660 → 8.499 (duas reescritas), Jó 13.665 → 8.417, Cântico
13.095 → 8.499. Cada passada de compressão re-envia o arquivo inteiro pelo wire.
Regras de briefing desde o Lote 6:
1. Alvo de palavras **7.200–7.800** — folga para nunca cruzar 8.500 (o teto real).
2. Uma passada de escrita; quem passar de 9.000 comprime POR SEÇÃO com `patch`,
   nunca reescreve o arquivo todo com `write_file`.
3. UMA validação no fim (`python validar_dossie.py <slug>`); aviso de estilo não
   exige correção.
4. Pesquisa sem redundância: a forma e as fontes-âncora já estão no acervo.

Métrica de controle do Lote 6 (flash/high no Portal) contra o padrão v4.1:
`validar_dossie.py` + densidade das quatro camadas + custo em USD por lote.

## Fluxo de um lote

1. Redator escreve o dossiê **completo** no caminho final
   (`src/content/biblioteca/biblia/<slug>.mdx`), seguindo a forma e as regras.
2. Pai **verifica o artefato**, não o relatório:
   `python validar_dossie.py <slug>` — frontmatter, treze seções, imports e a
   linha em branco do MDX, tamanho, marcadores, quatro camadas com autores
   nomeados, esferas confessionais, selos, ausência de espanhol, `<` ou `{`
   soltos. **Falha = não buildar.** Os avisos são para revisão, não bloqueiam.
3. `npm run build` + `python verificar_site.py` + `python verificar_eixos.py`.
4. Commit por lote.

### O que o validador aprendeu (não repetir)

O acervo tem **duas gerações** de dossiês: os do Pentateuco usam títulos em
caixa alta (`2. CONTEXTO E AUTORIA`, `4. NARRATIVAS-CHAVE E DEBATE ACADÊMICO`) e
os de Josué a Reis a forma consagrada (`2. Contexto e Autoria`). A primeira
versão do validador só conhecia a segunda e reprovou dossiê íntegro — o defeito
era do extrator. Corolários que valem para qualquer verificador novo:

- A bibliografia tem **quatro** grafias legítimas: `Bibliografia-âncora
  verificada`, `Referências-âncora verificadas` (Levítico), `Autores-âncora`
  (Êxodo), `ANEXO — OBRAS-ÂNCORA E VERIFICAÇÃO` (Gênesis). Aceitar todas.
- O `max(160)` da descrição vale para `artigos` (meta de SERP), não para a
  biblioteca: ali é aviso.
- **Recortar seção por posição do cabeçalho, nunca por `texto.find(título)`** —
  o sumário lateral repete os títulos e o `find` ancora nele, devolvendo corpo
  truncado. Foi o que produziu "autores 0/0/0/0" em dossiê que os tem.
- Dossiê de contexto (`area: oriente`, `pre-historia`) e página de área têm
  forma própria: o validador os pula em vez de reprová-los.
- **O validador não checava o VALOR do selo, e isso quebrou o build** (12/set/2026,
  dossiê de Coélet): o redator escreveu `<SeloAcesso tipo="empréstimo" />` com
  acento, quando a chave em `SELOS` é `emprestimo`. `\w+` em Python casa com
  acento, o selo foi contado certinho e o arquivo passou com 0 falhas — o
  componente só lança (`SeloAcesso: tipo desconhecido`) quando o Astro o
  renderiza, com o `dist` já apagado. Corrigido: o validador agora lê a lista de
  tipos válidos de `src/taxonomia.ts` (fonte única) e reprova qualquer valor
  fora dela. **Lição geral: quem valida forma não valida vocabulário.** Todo
  campo que alimenta um `throw` no componente precisa da sua lista de valores
  legítimos no portão pré-build.

### Armadilha de arquivo parcial

Redator que escreve em partes deixa `_<slug>_parte2.mdx` no diretório de
conteúdo — e o glob `**/*.mdx` do Astro o lê, falhando o build por frontmatter
ausente. Conferir antes de buildar: `ls src/content/biblioteca/biblia/_*.mdx`.

## Pendências que não são dossiê

- Domínio próprio (hoje `estudos-antigos.netlify.app`).
- Site **privado no Netlify** — não indexável (confirmado: todas as rotas respondem 401).
  O usuário decidiu: sem pressa; primeiro o conteúdo.
- Imagem social por artigo (hoje uma só).
- Busca interna (Pagefind como passo pós-build).
- Artigos-porta para os dossiês que ainda não têm (Suméria e Pré-História não
  têm; os 9 bíblicos têm 7 no total).

## Entregas fora do site (13/set/2026)

Duas pastas geradas do build, ambas no `.gitignore` (artefato, não fonte):

- `html-avulso/` — **cópia autônoma do site inteiro**: 151 páginas HTML num só
  diretório, com CSS inline, fontes locais (`fonts/`, 4 `.woff2`), tema
  claro/escuro funcional e **toda a navegação interna reapontada** para os
  próprios arquivos (0 links quebrados, 0 links inertes). Os dossiês ficam com
  nome curto (`juizes.html`); o índice do conjunto é `index.html`; a capa do
  site é `inicio.html`. Abre por duplo clique, sem servidor e sem internet.
- `html-avulso/pdf/` — **os 54 dossiês em PDF** (1.273 páginas, 63,5 MB), impressos
  do HTML pelo Chrome headless (A4, tema claro, chrome de navegação oculto,
  metadados de título por artigo). Preserva a tipografia e o layout do site.

Scripts (versionados):

    python scripts/gerar_html_avulso.py --limpar     # gera html-avulso/ do build
    python scripts/conferir_html_avulso.py           # texto idêntico ao build, links, fontes, tema
    python scripts/conferir_pdfs.py                  # páginas, seções, navegação, brancas, metadados

Dois aprendizados que o verificador precisa respeitar (já implementados):
1. **Duas gerações de dossiê coexistem** — a §13 varia ("Lacunas e Correções de
   Atribuição", "LACUNAS", "LACUNAS DECLARADAS", "LACUNAS E INCERTEZAS",
   "LACUNAS (estado da arte)") e a bibliografia tem quatro grafias. Verificador
   que exige uma só reprova dossiê íntegro.
2. No PDF, **a última página com poucas linhas é a nota final da bibliografia**
   ("Selo [esgotado] não aparece aqui…"), não uma página vazia — em 4 dos 54
   dossiês ela fica sozinha. Só página curta no MEIO do documento é defeito.


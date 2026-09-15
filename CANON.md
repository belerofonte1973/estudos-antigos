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

## Regras de conteúdo (skill `pesquisador-bibliografico` v5.9)

Desde 14/set/2026 a skill se divide em **núcleo** (SKILL.md, 31 kB: disciplina,
workflow, modelo, calibração, verificação) e **references por tópico**, abertas
sob demanda (era um único arquivo de 142 kB, carregado inteiro em todo uso). Para
os dossiês deste acervo, o briefing do redator é
`_briefings/nucleo-dossie.md` via `scripts/briefing.py <slug>` — as oito regras
abaixo são o que ele precisa, e a skill só é aberta além disso quando a tarefa
pedir (ex.: `references/book-verification-recipes.md` para conferir ISBN).

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

### Economia de tokens — medido no `state.db` em 14/set/2026

Medição real (`session_model_usage`) das quatro sessões que produziram o acervo:

    chamadas   entrada    cache_read   saída   raciocínio   US$ estimado
      870       4,31M      181,0M      965k      491k          0,87
                                              (sem cache seria US$ 7,56 — 9x)

Leituras que mudaram o processo:
- **98% do prompt vem do cache** (`cache_read` a US$ 0,01/M contra US$ 0,04/M de
  entrada fresca). O custo é baixo porque o cache está vivo; quebrá-lo custa 9x.
- O maior VOLUME não é o modelo, é o **prefixo reenviado a cada chamada**:
  média de **117k a 255k tokens por chamada** nas sessões longas.
- A skill `pesquisador-bibliografico` tem **142 kB ≈ 36 mil tokens** e era
  carregada por cada subagente, em todos os turnos dele.

Regras adicionais desde 14/set/2026 (somam-se às quatro de briefing acima):

5. **Briefing aponta para `_briefings/nucleo-dossie.md` (~4,4 kB), não para a
   skill.** O núcleo tem as 8 regras de conteúdo, o contrato de saída exato
   (frontmatter, 13 seções, faixa de palavras) e o fecho. Só abrir uma
   referência da skill quando a tarefa pedir além disso — e só a específica
   (ex.: `book-verification-recipes.md` para conferir ISBN).
6. **Sessão nova por lote.** Histórico acumulado é o que engorda o prefixo:
   sessão de 588 mensagens reenviava ~250 kB em cada uma das 300 chamadas.
   Commitar o lote e abrir sessão nova derruba o prefixo para dezenas de kB.
7. **Blindar o cache:** não editar skill nem system prompt no meio do lote; não
   trocar modelo/provider com subagente em voo; manter o estável (regras,
   briefing) no início do contexto e o volátil no fim.
8. **Saída de terminal no contexto também é prefixo.** `python scripts/status.py`
   imprime o estado em ~10 linhas (o validador cru imprime 56 blocos) — use-o em
   lugar de ler a saída inteira.
9. Medir antes de opinar: `python ~/hermes-tools/relatorio_tokens.py --sessoes 5`
   (relatório por sessão/modelo/tarefa, com % de cache e o custo "se sem cache").
   `python scripts/status.py` = estado do acervo; `relatorio_tokens.py` = o que
   custou.

## Ferramentas de operação (14/set/2026)

O que consultar antes de agir, em ordem de frequência:

    python scripts/status.py                 # estado do acervo em ~10 linhas (o validador
                                             #   roda junto; --rapido pula, --sem-rede não testa o site)
    python scripts/briefing.py <slug>        # briefing de UM dossiê, pronto para o context da
                                             #   delegação (núcleo + específico do livro) — não
                                             #   compor briefing à mão nem carregar a skill inteira
    python scripts/briefing.py --proximo     # livros da taxonomia ainda sem dossiê
    python ~/hermes-tools/relatorio_tokens.py --sessoes 5
                                             # tokens/custo por sessão, % de cache e custo
                                             #   "se 100% sem cache" (lê o state.db do Hermes)

Cadeia de figuras (só quando mexer em imagem): `baixar_pendentes.py --seco` →
`baixar_pendentes.py` → `aplicar_figuras.py` → `npm run build` →
`gerar_html_avulso.py --limpar` → `conferir_html_avulso.py` → reimprimir os PDFs
afetados (Chrome headless) → `comprimir_pdf.py html-avulso/pdf` →
`conferir_pdfs.py`.

## Fluxo de um lote

1. **Briefing** do redator = `_briefings/nucleo-dossie.md` (lido do disco, ~4,4 kB)
   + o que é específico do livro. **Não** mandar carregar a skill inteira
   (`skill_view('pesquisador-bibliografico')` = ~36 mil tokens por subagente, em
   cada turno dele). Referência da skill só quando a tarefa exigir algo além do
   núcleo — e só a específica.
2. Redator escreve o dossiê **completo** no caminho final
   (`src/content/biblioteca/biblia/<slug>.mdx`), seguindo a forma e as regras.
3. Pai **verifica o artefato**, não o relatório:
   `python validar_dossie.py <slug>` — frontmatter, treze seções, imports e a
   linha em branco do MDX, tamanho, marcadores, quatro camadas com autores
   nomeados, esferas confessionais, selos, ausência de espanhol, `<` ou `{`
   soltos. **Falha = não buildar.** Os avisos são para revisão, não bloqueiam.
4. `npm run build` + `python verificar_site.py` + `python verificar_eixos.py`.
5. Commit por lote — e **sessão nova para o lote seguinte** (o histórico
   acumulado é o que engorda o prefixo reenviado em cada chamada).

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

## Figuras nos dossiês (13/set/2026)

Cada dossiê recebe **4 a 6 obras** — pinturas, gravuras, esculturas, estátuas,
iluminuras e objetos arqueológicos — das personagens, figuras, animais e temas
do livro, com **ficha completa e fonte verificável**.

Fonte: **Wikimedia Commons** (que reúne também as doações de acesso aberto do
MET, Rijksmuseum, NGA). Nada entra sem passar pelo portão de licença:

    LIVRE       domínio público / PDM / CC0        preferir sempre
    ATRIBUICAO  CC BY / CC BY-SA                   aceitável, creditando o autor da foto
    NAO-USAR    qualquer outra                     recusada e registrada no manifesto

Ferramentas (versionadas):

    python scripts/imagens_buscar.py "termo"        # busca com licença/autor/data/px já classificados
    python scripts/imagens_baixar.py --spec _imagens/espec_<slug>.json
    python scripts/imagens_inserir.py --slug <slug> [--seco|--reverter]
    python scripts/comprimir_pdf.py html-avulso/pdf/*.pdf

- `scripts/commons_api.py` centraliza o acesso à API: throttle de 1,1 s, backoff
  para 429/5xx e **cache em disco** (`_imagens/cache/`, no `.gitignore`). A API
  limita com força as chamadas de busca; um 429 tratado como "não achei" viraria
  lacuna de imagem fabricada.
- `public/imagens/<slug>/` — as imagens do site (WebP, largura máxima 950 px,
  qualidade 75, ~210 KB de média). `_imagens/<slug>.json` — o manifesto: ficha de
  cada figura, sha256, licença e as recusas. `_imagens/espec_<slug>.json` — a
  especificação editorial de cada dossiê.
- O componente é `src/components/Figura.astro`; a legenda descreve a cena e cita
  a passagem, e a ficha (autor · data · técnica · acervo) mais a linha
  `Fonte: <link> · Licença:` são obrigatórias.

**Dois aprendizados que valem para qualquer PDF com imagens:**
1. O Chrome (`Page.printToPDF`) **embute as figuras sem compressão com perdas** —
   um dossiê de 9 figuras saiu com 20 MB. `scripts/comprimir_pdf.py` recomprime
   cada imagem embutida (pypdf `ImageFile.replace`, que só funciona em página de
   `PdfWriter`) e faz uma segunda passada para normalizar o `/Size` do trailer:
   20,1 MB → **3,3 MB**, mesmas páginas, mesmo texto.
2. `loading="lazy"` no HTML **não** impede o Chrome de incluir as figuras na
   impressão (verificado contando os XObjects do PDF) — mas isso é observação,
   não garantia: conte-os sempre.

**Resolvido (14/set/2026):** as **315 figuras especificadas estão todas
gravadas** (315 de 315, 0 recusadas, 0 recusadas de rede). O 429 do
`upload.wikimedia.org` é limite por IP e derruba **thumb e original juntos**
(medido: os dois devolvem 429 no mesmo minuto) — mas o cluster da wiki serve o
**mesmo arquivo** por outro ponto de entrada, e foi isso que destravou:
`https://commons.wikimedia.org/w/thumb.php?f=<arquivo>&w=<largura>` e
`https://commons.wikimedia.org/wiki/Special:FilePath/<arquivo>?width=<largura>`
(ambos medidos com HTTP 200 enquanto o CDN de mídia devolvia 429).

`scripts/imagens_baixar.py` agora tem `urls_da_figura()` — a URL normal primeiro,
as duas do cluster da wiki como plano B da mesma obra (licença continua sendo a
que a API confirmou, nada muda no manifesto) — e `baixar_arquivo()` tenta cada
candidata, respeitando `Retry-After`. Efeito medido: a segunda passada fechou
24 especificações **sem uma única recusa** e em ~1/3 do tempo da primeira (que
gastou o tempo em backoff contra o CDN limitado). Lição: 429 do Wikimedia é
limite do host de mídia, não da obra — trocar de ponto de entrada resolve antes
de esperar a cota abrir.

## Pendências que não são dossiê

- Domínio próprio (hoje `estudos-antigos.netlify.app`).
- Site **privado no Netlify** — não indexável (confirmado: todas as rotas respondem 401).
  O usuário decidiu: sem pressa; primeiro o conteúdo.
- Imagem social por artigo (hoje uma só).
- Busca interna (Pagefind como passo pós-build).
- Artigos-porta para os dossiês que ainda não têm (Suméria e Pré-História não
  têm; os 9 bíblicos têm 7 no total).

## Entregas fora do site (13/set/2026 · atualizado 14/set/2026)

Duas pastas geradas do build, ambas no `.gitignore` (artefato, não fonte):

- `html-avulso/` — **cópia autônoma do site inteiro**: 151 páginas HTML num só
  diretório, com CSS inline, fontes locais (`fonts/`, 4 `.woff2`), tema
  claro/escuro funcional e **toda a navegação interna reapontada** para os
  próprios arquivos (0 links quebrados, 0 links inertes). Os dossiês ficam com
  nome curto (`juizes.html`); o índice do conjunto é `index.html`; a capa do
  site é `inicio.html`. Abre por duplo clique, sem servidor e sem internet.
  **Páginas `_*.html` do build ficam de fora** (`paginas_do_build()`): são
  utilitárias do site vivo, não conteúdo — sem essa guarda o gerador produz
  `_tema_claro.html.html` e o verificador acusa duas faltas que não são defeito.
- `html-avulso/pdf/` — **os 54 dossiês em PDF** (1.327 páginas, 122,9 MB),
  impressos do HTML pelo Chrome headless (A4, tema claro, chrome de navegação
  oculto, metadados de título por artigo). Preserva a tipografia e o layout do
  site. A cadeia depois de mexer em figuras: reimprimir só os dossiês afetados
  (o `.pdf` antigo continua válido para os demais) →
  `python scripts/comprimir_pdf.py html-avulso/pdf` (mediu 363,2 MB → 122,9 MB)
  → `python scripts/conferir_pdfs.py` (**tudo verde**).

Página utilitária do site: `public/_tema_claro.html` grava `ea-theme=light` no
localStorage (mesmo domínio vale para todo o site) e redireciona para
`/artigos/`. Ela morava só em `dist/` — que o build apaga — e sumiu na primeira
recompilação; agora vive versionada em `public/`, então sobrevive a todo build.

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


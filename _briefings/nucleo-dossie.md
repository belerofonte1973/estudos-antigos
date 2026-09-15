# Núcleo de briefing — dossiê enciclopédico (Estudos Antigos)

**Por que este arquivo existe:** a skill `pesquisador-bibliografico` tem ~142 kB
(≈36 mil tokens) e cada subagente que a carrega reenvia esse prefixo em todos os
seus turnos. Este núcleo entrega o que um dossiê da Bíblia realmente exige em
~4 kB. **Briefing de subagente aponta para cá — não carregue a skill inteira.**
Só abra uma referência da skill quando a tarefa pedir algo além daqui, e só a
referência específica (ex.: `book-verification-recipes.md` para conferir ISBN).

## 1. Regra Zero

Nunca inventar autor, título, ano, DOI, editora ou página. Não achou a fonte:
escreve que não encontrou. Citar página só se a página foi vista.

## 2. Marcadores literais (sem abreviar, um por afirmação rastreável)

`[V]` ISBN conferido em Open Library · `[V-OL]` work record · `[W]` obra citada
nas referências da Wikipédia PT · `[V-WP]` · `[ACAD]` artigo com DOI ·
`[NV]` ISBN testado e não encontrado · `[HIST]` obra pré-1980 sem ISBN ·
`[DIGITAL]` domínio público · `[—]` lacuna assumida.

Acervo real: 29–197 marcadores `[V]` por dossiê e nenhum dossiê sem `[W]`.

## 3. Citação inline

`(Autor, Ano, p.X)` ou `(Autor, Ano, cap.X)` em **cada** afirmação factual;
2–3 fontes nas afirmações contestadas.

## 4. Quatro camadas obrigatórias, com autores extrabíblicos nomeados

- §9 mitologia/literatura comparada — paralelos do Antigo Oriente Próximo;
- §10 filosofia — Espinosa, Kant, Mackie, Rowe, Girard, Douglas…;
- §11 teologia-*debates* — von Rad, Noth, Cross, Levenson, Gutiérrez, Rashi…;
- §12 ciência — Finkelstein, Dever, Whitcomb, Patterson, Skorecki, Thiele…
  e **declarar explicitamente onde a ciência não tem competência**.

O validador avisa quando uma camada tem menos de 3 autores nomeados, ou corpo
de menos de 120 palavras.

## 5. §11.1 — comentaristas por esfera confessional

Cinco esferas: judaica, católica, ortodoxa, protestante histórica, evangélica.
Faltar a evangélica é o aviso mais comum do acervo.

A esfera **evangélica é própria, não diluída na protestante histórica**: a
protestante fica com a Reforma e o devocional clássico (Lutero, Calvino, Henry,
Keil–Delitzsch); a evangélica fica com as **séries críticas e expositivas** de
editoras e linhas evangélicas (WBC, NICOT, NAC, TOTC/BST, NIVAC, EBC, NIBC,
Apollos), com ano e editora no registro. Um autor conta **uma única vez**, na
esfera a que pertence, e a contagem no fim da subseção diz onde. Obras só entram
com ano/editora conferidos — na dúvida, `[W]`, e o texto diz que não foi
reconferido.

## 6. Bibliografia-âncora com selo de acesso por obra

`[livre]` · `[empréstimo]` (`emprestimo`, sem acento, na chave do componente) ·
`[compra]` · `[biblioteca]` · `[esgotado]`, com link clicável. Selo é passada de
conteúdo obra por obra — nunca decoração.

## 7. PT-BR sempre

Nenhum vazamento de espanhol (`hebreo`, `pueblo`, `también`, `además`, `mientras`,
`siglos`, `Antiguo` fora de "Antiguo Oriente"; `Siglo` fora de "Siglo XXI").
Editora "Siglo XXI" é legítima.

## 8. Hebraico, grego e ge'ez em texto puro

O plugin remark envolve automaticamente — não marcar à mão, não usar `<span>`.

## 9. Contrato de saída (o artefato, não o relatório)

Arquivo: `src/content/biblioteca/biblia/<slug>.mdx`.

- Frontmatter: `title`, `description` (**≤160 chars**), `area: biblia`,
  `ordem: <n>`, `eixo: nucleo`, `livro: <slug>` (ou `livros: [...]`).
- Imports depois do frontmatter, **com linha em branco** no fim do bloco:
  Card, CardGrid, Aside, SeloAcesso, LinkButton (todos de `../../../components/`).
- 13 seções H2, nesta ordem, com o padrão da geração consagrada:
  `1. Lead e Ficha` · `2. Contexto e Autoria` · `3. Estrutura` ·
  `4. Conteúdos-chave com Debate` · `5. Temas` · `6. Recepção` ·
  `7. Traduções PT e Comentários PT` · `8. Audiovisual e Games` ·
  `9. Mitologia e Literatura Comparada` · `10. Filosofia…` · `11. Teologia…`
  (com `### 11.1`) · `12. Ciência…` · `13. Lacunas e Correções de Atribuição`,
  mais a `## Bibliografia-âncora` no fim.
- Subseção é `###`. H2 extra é aviso do validador.
- Tamanho: **7.200–7.800 palavras** (piso 6.500, teto 11.000 — acima de 9.000
  comprima por seção com `patch`, nunca reescreva o arquivo com `write_file`).

## 10. Fecho (o que o subagente devolve ao pai)

Devolver: slug, contagem de palavras, `[V]`/`[W]`/`[—]`, seções ausentes, fontes
novas que precisam de conferência e — se houver — o que **não** foi possível
verificar. Não colar o texto do dossiê na resposta.

## 11. Validação (uma vez, no fim — e é o pai que confere)

- `python validar_dossie.py <slug>` — 0 falhas é obrigatório; aviso de estilo
  não exige correção.
- Uma passada de escrita. Pesquisa sem redundância: a forma e as fontes-âncora
  já estão no acervo (`_camadas/`, `_selos/`, os dossiês irmãos).

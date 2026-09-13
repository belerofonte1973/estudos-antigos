# Figuras dos dossiês — caderno de encargos

Documento de trabalho para quem for montar a especificação de figuras de um
dossiê. O objetivo: **cada dossiê passa a ter imagens de personagens, figuras,
animais e temas do livro, com ficha completa e fonte verificável** — sem
nenhuma imagem de licença duvidosa e sem nenhum dado inventado.

## O que se entrega

Um arquivo por dossiê: `_imagens/espec_<slug>.json`, no schema abaixo. Nada mais.
**Não baixe imagens, não edite os `.mdx`, não rode build.** Quem baixa, insere e
confere é a sessão principal, com os scripts do acervo.

## Regra de licença (não negociável)

Só entra o que permite reuso:

| Grupo | Licença | Uso |
|---|---|---|
| LIVRE | domínio público, PDM, CC0 | preferir sempre |
| ATRIBUICAO | CC BY 2.0/3.0/4.0, CC BY-SA 2.0/3.0/4.0 | aceitável, com crédito ao autor da foto na ficha |
| NAO-USAR | qualquer outra | fora |

`scripts/imagens_buscar.py` já classifica e filtra. **Toda obra precisa ser
confirmada pelo script** — nunca por memória. Nome de arquivo inventado ou
escrito de cabeça é o erro que este caderno existe para impedir: a busca
confirma que o arquivo existe, diz a licença, o autor, a data, o acervo e o
tamanho.

## Ferramenta

```bash
cd C:/Users/music/estudos-antigos
python scripts/imagens_buscar.py "Samson and Delilah"           # busca livre
python scripts/imagens_buscar.py --categoria "Category:Samson"  # dentro de uma categoria
python scripts/imagens_buscar.py "Gideon" --limite 10 --largura-min 900
python scripts/imagens_buscar.py "Baal Ugarit" --json _imagens/cand_baal.json
```

Saída: tabela `licença · autor · data · px · KB · arquivo` e a lista de páginas
de origem. Só os candidatos utilizáveis aparecem (descarta pequenas, formatos
estranhos e licença NAO-USAR). A API é limitada por taxa: o script espera e
repete sozinho (HTTP 429 é tratado) — **não** contorne com chamadas paralelas.

Categorias do Commons que rendem muito (busque outras com
`srnamespace=14` se precisar): `Category:Samson`, `Category:Gideon`,
`Category:Deborah`, `Category:Bible illustrations by Gustave Doré`,
`Category:Art depicting the Old Testament by Gustave Doré`,
`Category:Paintings of the Old Testament` e as categorias de cada livro.

## Critérios editoriais da figura

1. **4 a 6 figuras por dossiê.** Menos que 4 deixa o artigo seco; mais que 6
   incha o repositório (cada imagem fica ~200 KB).
2. **Variedade de mídia** — o conjunto deve ter, sempre que possível: uma
   **pintura**, uma **gravura** (Doré 1866 é o padrão-ouro, mas também Dürer,
   Pencz, Merian), uma **escultura/estátua** ou **relevo**, uma **iluminura**
   medieval ou objeto de época, e um **objeto arqueológico/inscrição** quando o
   livro tem lastro material (estela, selo, óstraco, moeda, lâmpada, figurinha).
3. **Cobertura do que o leitor quer ver**: ao menos um **personagem central**
   (Abraão, Moisés, Sansão, Rute, Ester, Judite, Davi…), uma **figura** (anjo,
   profeta, sacerdote, rei), quando houver **animal** (leão, cordeiro, jumenta,
   peixe, gafanhoto, serpente, águia) um item com o animal, e um item de
   **tema** (o sacrifício, o êxodo, o exílio, a aliança, o banquete, a
   destruição do templo).
4. **Distribuição por seção** — a figura entra no FIM da seção pedida:
   - `"4"` — Conteúdos-chave com Debate: a cena que o dossiê discute;
   - `"6"` — Recepção: arte, música, cinema (é a casa natural da pintura/gravura);
   - `"9"` — Mitologia e Literatura Comparada: objeto do Antigo Oriente Próximo
     que se compara ao texto (Baal, deuses, motivos do ANE);
   - `"12"` — Ciência: arqueologia, epigrafia, o que o material documenta.
5. **Isso é um acervo acadêmico, não uma galeria**: a obra precisa dizer algo
   sobre o livro. Se a imagem é bonita mas só decorativa, não entra.

## Legenda e ficha

- `titulo`: curto, em PT-BR — "Sansão e Dalila", "Débora louva Jael".
- `alt`: descrição para quem não vê a imagem (uma linha, o que está na cena).
- `legenda`: **2 a 3 frases em PT-BR** (norma do site: nada de espanhol) que
  digam o que se vê, **a passagem bíblica** (ex.: `Jz 16,4-22`) e por que aquilo
  interessa ao dossiê. Baseie o que se vê na descrição da fonte no Commons e no
  texto bíblico; se não for possível afirmar com segurança o que a obra mostra,
  escolha outra obra. **Não invente atribuição, data, acervo nem número de
  inventário** — o que não estiver na API fica em branco e o script preenche.
- `passagem`: referência bíblica da cena.
- `tecnica`: só se a fonte disser ("óleo sobre tela", "xilogravura",
  "estatueta de bronze", "desenho sobre papel").
- `acervo`: o que a fonte declarar (museu, cidade, inv.) — para obras com foto
  CC BY/BY-SA, cite também o **autor da fotografia** (obrigação da licença).
- `secao` / `posicao`: conforme o item 4 acima (`posicao` é "fim" no caso normal).

## Schema do arquivo

```json
{
 "slug": "<slug do dossiê, igual ao nome do .mdx>",
 "figuras": [
  {
   "arquivo": "File:Nome exato como aparece no Commons.jpg",
   "titulo": "Sansão e Dalila",
   "alt": "descrição do que se vê, em uma linha",
   "legenda": "Duas ou três frases em PT-BR, com a passagem e o interesse para o dossiê.",
   "passagem": "Jz 16,4-22",
   "tecnica": "óleo sobre tela",
   "acervo": "The Metropolitan Museum of Art, Nova York",
   "secao": "6",
   "posicao": "fim"
  }
 ]
}
```

Exemplo completo e real: `_imagens/espec_juizes.json` (9 figuras, dossiê-piloto).

## Relatório final obrigatório

Na resposta: para cada dossiê, o slug, quantas figuras entraram e as licenças
usadas (por exemplo: "rute: 5 figuras — 4 LIVRE, 1 ATRIBUICAO"). E, se algum
dossiê ficar com menos de 4 figuras, **diga qual e por quê** — um dossiê sem
material livre é uma informação, não um fracasso.

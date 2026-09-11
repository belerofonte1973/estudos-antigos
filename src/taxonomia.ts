/**
 * Taxonomia compartilhada: eixos, recortes disciplinares e livros.
 *
 * Mora fora de `src/content.config.ts` de propósito. Aquele arquivo é o
 * módulo de configuração da camada de conteúdo do Astro: ele importa
 * `astro:content`, e importá-lo de dentro de um componente cria um ciclo em
 * que as constantes chegam indefinidas em tempo de renderização (o sintoma é
 * `Cannot read properties of undefined (reading 'nome')` no build).
 *
 * Este arquivo não importa nada — pode ser usado por componentes, layouts,
 * páginas, scripts Python (via espelhamento) e pelo config das coleções.
 */

/**
 * EIXOS — a espinha do site.
 *
 * Não é uma taxonomia de menu: é a divisão real da disciplina. Um estudo
 * bíblico sério se organiza em torno do texto, do mundo em que ele surgiu e
 * do que foi feito dele depois. Modelar assim tem uma consequência prática:
 * acrescentar uma camada nova (arte, reforma, recepção moderna) é adicionar
 * um valor aqui, sem mover arquivo nem quebrar endereço.
 */
export const EIXOS = {
	nucleo: {
		nome: 'Texto',
		rotulo: 'Núcleo bíblico',
		descricao:
			'Os livros bíblicos em si: crítica textual, línguas originais, formação do cânon, exegese, passagens.',
		rota: '/biblia/',
	},
	contexto: {
		nome: 'Contexto',
		rotulo: 'Mundo antigo',
		descricao:
			'O mundo em que esses textos surgiram: Antigo Oriente Próximo, Mesopotâmia, Egito, Grécia e Roma, pré-história, arqueologia.',
		rota: '/contexto/',
	},
	recepcao: {
		nome: 'Recepção',
		rotulo: 'Depois do texto',
		descricao:
			'O que foi feito desses textos: patrística, exegese medieval, iconografia, traduções, história da interpretação.',
		rota: '/recepcao/',
	},
} as const;

export type Eixo = keyof typeof EIXOS;

/** Recorte disciplinar — o eixo diz a posição; a área diz o assunto. */
export const AREAS = {
	biblia: 'Antiguidade Bíblica',
	oriente: 'Oriente Próximo Antigo',
	classica: 'Antiguidade Clássica',
	'pre-historia': 'Pré-História',
	'idade-media': 'Idade Média',
} as const;

export type Area = keyof typeof AREAS;

/**
 * LIVROS — a coluna vertebral do núcleo.
 *
 * Cada livro tem endereço próprio (`/biblia/<slug>/`) com as passagens
 * estudadas. É por aqui que o núcleo cresce: uma passagem por vez, sem
 * engordar nenhuma página até o ponto de não poder ser editada.
 *
 * Os nomes hebraicos são os incipits — o livro toma o nome da primeira
 * palavra significativa do texto, prática da tradição judaica.
 *
 * `abrev`, `en` e `slugCat` existem para montar link a Bíblia online: cada
 * site tem o seu esquema de URL, e todos os padrões abaixo foram conferidos
 * por HTTP 200 em 11-set-2026. Não inventar slug novo sem conferir.
 */
export const LIVROS = {
	genesis: {
		nome: 'Gênesis',
		hebraico: 'בְּרֵאשִׁית',
		translit: 'Bereshit',
		ordem: 1,
		abrev: 'gn',
		en: 'Genesis',
		slugCat: 'genesis',
	},
	exodo: {
		nome: 'Êxodo',
		hebraico: 'שְׁמוֹת',
		translit: 'Shemot',
		ordem: 2,
		abrev: 'ex',
		en: 'Exodus',
		slugCat: 'exodo',
	},
	levitico: {
		nome: 'Levítico',
		hebraico: 'וַיִּקְרָא',
		translit: 'Vayikra',
		ordem: 3,
		abrev: 'lv',
		en: 'Leviticus',
		slugCat: 'levitico',
	},
	numeros: {
		nome: 'Números',
		hebraico: 'בְּמִדְבַּר',
		translit: 'Bemidbar',
		ordem: 4,
		abrev: 'nm',
		en: 'Numbers',
		slugCat: 'numeros',
	},
	deuteronomio: {
		nome: 'Deuteronômio',
		hebraico: 'דְּבָרִים',
		translit: 'Devarim',
		ordem: 5,
		abrev: 'dt',
		en: 'Deuteronomy',
		slugCat: 'deuteronomio',
	},
	josue: {
		nome: 'Josué',
		hebraico: 'יְהוֹשֻׁעַ',
		translit: 'Yehoshua',
		ordem: 6,
		abrev: 'js',
		en: 'Joshua',
		slugCat: 'josue',
	},
	juizes: {
		nome: 'Juízes',
		hebraico: 'שׁוֹפְטִים',
		translit: 'Shoftim',
		ordem: 7,
		abrev: 'jz',
		en: 'Judges',
		slugCat: 'juizes',
	},
	'samuel-1': {
		nome: '1 Samuel',
		hebraico: 'שְׁמוּאֵל',
		translit: 'Shemuel',
		ordem: 8,
		abrev: '1sm',
		en: '1 Samuel',
		slugCat: '1-samuel',
	},
	'samuel-2': {
		nome: '2 Samuel',
		hebraico: 'שְׁמוּאֵל',
		translit: 'Shemuel',
		ordem: 9,
		abrev: '2sm',
		en: '2 Samuel',
		slugCat: '2-samuel',
	},
	'reis-1': {
		nome: '1 Reis',
		hebraico: 'מְלָכִים',
		translit: 'Melakhim',
		ordem: 10,
		abrev: '1rs',
		en: '1 Kings',
		slugCat: '1-reis',
	},
	'reis-2': {
		nome: '2 Reis',
		hebraico: 'מְלָכִים',
		translit: 'Melakhim',
		ordem: 11,
		abrev: '2rs',
		en: '2 Kings',
		slugCat: '2-reis',
	},
} as const;

/** Catálogo de bíblias online em PT, com a tradição declarada. */
export const BIBLIAS = [
	{
		id: 'ara',
		nome: 'Almeida Revista e Atualizada',
		sigla: 'ARA',
		tradicao: 'protestante',
		url: (l: LivroMeta, cap: string) =>
			`https://www.bibliaonline.com.br/ara/${l.abrev}/${cap}`,
	},
	{
		id: 'nvi',
		nome: 'Nova Versão Internacional',
		sigla: 'NVI',
		tradicao: 'protestante',
		url: (l: LivroMeta, cap: string) =>
			`https://www.bibliaonline.com.br/nvi/${l.abrev}/${cap}`,
	},
	{
		id: 'ave-maria',
		nome: 'Ave-Maria',
		sigla: 'Ave-Maria',
		tradicao: 'católica',
		url: (l: LivroMeta, cap: string) =>
			`https://www.bibliacatolica.com.br/biblia-ave-maria/${l.slugCat}/${cap.split('-')[0]}/`,
	},
	{
		id: 'nvi-pt-gateway',
		nome: 'NVI (BibleGateway)',
		sigla: 'NVI',
		tradicao: 'protestante',
		url: (l: LivroMeta, cap: string) =>
			`https://www.biblegateway.com/passage/?search=${encodeURIComponent(`${l.en} ${cap}`)}&version=NVI-PT`,
	},
	{
		id: 'livre',
		nome: 'Bíblia Livre',
		sigla: 'livre',
		tradicao: 'licença aberta',
		url: () => 'https://ebible.org/find/show.php?id=porblivre',
	},
] as const;

export type LivroMeta = (typeof LIVROS)[Livro];

/** Selos de acesso — o que o leitor precisa para obter uma obra. */
export const SELOS = {
	livre: {
		rotulo: 'livre',
		descricao: 'Acesso livre e legal: domínio público, Creative Commons ou acesso aberto.',
	},
	emprestimo: {
		rotulo: 'empréstimo',
		descricao: 'Emprestável digitalmente (Internet Archive / Open Library).',
	},
	compra: {
		rotulo: 'compra',
		descricao: 'Disponível por compra, na editora ou em livraria.',
	},
	biblioteca: {
		rotulo: 'biblioteca',
		descricao: 'Buscar em acervo de biblioteca universitária (WorldCat).',
	},
	esgotado: {
		rotulo: 'esgotado',
		descricao: 'Sem via de acesso atual — a obra secundária que o resume é indicada.',
	},
} as const;

export type Selo = keyof typeof SELOS;

/**
 * PRÉ-REQUISITOS por livro — o que o dossiê supõe que o leitor já saiba.
 *
 * Só aponta para páginas que EXISTEM neste site. Pré-requisito que aponta para
 * lugar nenhum é pior que pré-requisito nenhum: ensina o leitor a desconfiar
 * dos links. O termo que o autor usa há vinte anos é o termo que o leitor
 * encontra pela primeira vez — e não há rodapé que salve.
 */
export const PRE_REQUISITOS: Record<string, Array<{ termo: string; href: string }>> = {
	genesis: [
		{ termo: 'o que é a hipótese documentária', href: '/artigos/o-que-e-a-hipotese-documentaria/' },
		{ termo: 'quem escreveu o Gênesis', href: '/artigos/quem-escreveu-o-genesis/' },
		{ termo: 'quem foram os sumérios', href: '/artigos/quem-foram-os-sumerios/' },
		{ termo: 'o dilúvio e Gilgamesh', href: '/artigos/diluvio-da-biblia-vem-de-gilgamesh/' },
	],
	exodo: [
		{ termo: 'Moisés existiu?', href: '/artigos/moises-existiu/' },
		{ termo: 'os hebreus foram escravos no Egito?', href: '/artigos/os-hebreus-foram-escravos-no-egito/' },
		{ termo: 'o que é a hipótese documentária', href: '/artigos/o-que-e-a-hipotese-documentaria/' },
	],
	levitico: [
		{ termo: 'o que é a hipótese documentária', href: '/artigos/o-que-e-a-hipotese-documentaria/' },
	],
	numeros: [
		{ termo: 'o que é a hipótese documentária', href: '/artigos/o-que-e-a-hipotese-documentaria/' },
	],
	deuteronomio: [
		{ termo: 'o que é a hipótese documentária', href: '/artigos/o-que-e-a-hipotese-documentaria/' },
	],
	josue: [{ termo: 'que fontes são estas e como se datam', href: '/como-pesquisar/' }],
	juizes: [{ termo: 'que fontes são estas e como se datam', href: '/como-pesquisar/' }],
	samuel: [{ termo: 'que fontes são estas e como se datam', href: '/como-pesquisar/' }],
	reis: [{ termo: 'que fontes são estas e como se datam', href: '/como-pesquisar/' }],
};

/**
 * ESCADA DE ESTUDO — o caminho, não o índice.
 *
 * O dossiê numerado é um mapa; quem chega sozinho não sabe por onde começar,
 * quanto leva nem o que precisa saber antes. A escada dá o percurso.
 *
 * `secoes` casa com o número das seções do dossiê: passos cujas seções não
 * existem naquele dossiê são omitidos em vez de aparecerem vazios. A ordem dos
 * passos NÃO é a ordem das seções — ler o texto vem antes de qualquer
 * comentário, e isso é o ponto.
 */
export const ESCADA_ESTUDO = [
	{
		passo: 0,
		nome: 'A porta',
		tempo: '5–10 min',
		descricao:
			'A pergunta e a resposta rápida, sem rodeio. Ao fim você tem uma resposta utilizável e o mapa do que existe.',
		origem: 'artigo',
	},
	{
		passo: 1,
		nome: 'Ler o texto',
		tempo: '15–30 min',
		descricao:
			'A passagem inteira, em duas traduções de tradições diferentes, sem comentário. Comparar as duas é o exercício que mais rende: mostra onde o original é ambíguo.',
		origem: 'biblia',
	},
	{
		passo: 2,
		nome: 'O contexto',
		tempo: '20–40 min',
		descricao: 'O mundo em que o texto surgiu: geografia, arqueologia, paralelos do Antigo Oriente Próximo.',
		secoes: ['2', '9'],
	},
	{
		passo: 3,
		nome: 'O debate',
		tempo: '30–60 min',
		descricao: 'As posições em disputa, com quem as sustenta, onde publicou e qual é a réplica.',
		secoes: ['4', '10'],
	},
	{
		passo: 4,
		nome: 'A recepção',
		tempo: '30–60 min',
		descricao: 'O que se fez do texto: Padres, medievo, tradições confessionais.',
		secoes: ['6', '11'],
	},
	{
		passo: 5,
		nome: 'As quatro camadas',
		tempo: '40–90 min',
		descricao: 'Comparação com a mitologia, as perguntas filosóficas, os debates teológicos e o que a ciência diz — e onde não tem competência.',
		secoes: ['9', '10', '11', '12'],
	},
	{
		passo: 6,
		nome: 'O dossiê integral',
		tempo: '1,5–3 h',
		descricao: 'Tudo, na ordem, mais bibliografia com selo de acesso e as lacunas assumidas.',
		origem: 'integral',
	},
] as const;

export type Livro = keyof typeof LIVROS;

/** Rótulos de área prontos para exibição, com fallback. */
export const rotuloArea = (a: string): string =>
	(AREAS as Record<string, string>)[a] ?? a;

/** Rótulo do livro, com fallback para o slug. */
export const rotuloLivro = (l: string): string =>
	(LIVROS as Record<string, { nome: string }>)[l]?.nome ?? l;

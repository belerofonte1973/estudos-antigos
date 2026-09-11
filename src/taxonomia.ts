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
 */
export const LIVROS = {
	genesis: { nome: 'Gênesis', hebraico: 'בְּרֵאשִׁית', translit: 'Bereshit', ordem: 1 },
	exodo: { nome: 'Êxodo', hebraico: 'שְׁמוֹת', translit: 'Shemot', ordem: 2 },
	levitico: { nome: 'Levítico', hebraico: 'וַיִּקְרָא', translit: 'Vayikra', ordem: 3 },
	numeros: { nome: 'Números', hebraico: 'בְּמִדְבַּר', translit: 'Bemidbar', ordem: 4 },
	deuteronomio: { nome: 'Deuteronômio', hebraico: 'דְּבָרִים', translit: 'Devarim', ordem: 5 },
	josue: { nome: 'Josué', hebraico: 'יְהוֹשֻׁעַ', translit: 'Yehoshua', ordem: 6 },
	juizes: { nome: 'Juízes', hebraico: 'שׁוֹפְטִים', translit: 'Shoftim', ordem: 7 },
	'samuel-1': { nome: '1 Samuel', hebraico: 'שְׁמוּאֵל', translit: 'Shemuel', ordem: 8 },
	'samuel-2': { nome: '2 Samuel', hebraico: 'שְׁמוּאֵל', translit: 'Shemuel', ordem: 9 },
	'reis-1': { nome: '1 Reis', hebraico: 'מְלָכִים', translit: 'Melakhim', ordem: 10 },
	'reis-2': { nome: '2 Reis', hebraico: 'מְלָכִים', translit: 'Melakhim', ordem: 11 },
} as const;

export type Livro = keyof typeof LIVROS;

/** Rótulos de área prontos para exibição, com fallback. */
export const rotuloArea = (a: string): string =>
	(AREAS as Record<string, string>)[a] ?? a;

/** Rótulo do livro, com fallback para o slug. */
export const rotuloLivro = (l: string): string =>
	(LIVROS as Record<string, { nome: string }>)[l]?.nome ?? l;

/**
 * Taxonomia compartilhada: eixos, recortes disciplinares, cânones e livros.
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
 * CANONES — as tradições que recebem os livros.
 *
 * Existe porque "o Antigo Testamento" não é um só: é um conjunto de coleções
 * com fronteiras diferentes. Os mesmos livros aparecem em quatro extensões,
 * e cada acréscimo tem uma razão histórica verificável — o cânone católico
 * inclui os deuterocanônicos definidos em Trento (1546); o ortodoxo acrescenta
 * 1 e 2 Esdras, 3 e 4 Macabeus, o Salmo 151 e a Oração de Manassés; o etíope
 * (Tewahedo) recebe ainda 1 Enoque, Jubileus, os três Meqabyan e 4 Baruque.
 *
 * O site declara isso em vez de esconder: um livro fora do cânon protestante
 * aparece marcado como tal, com a tradição que o recebe. É informação, não
 * polêmica — e é o que faz a grade de livros dizer a verdade sobre o objeto.
 */
export const CANONES = {
	hebraico: {
		nome: 'Cânon hebraico',
		rotulo: 'Hebraico / protestante',
		descricao:
			'Os 24 livros do Tanakh, correspondentes aos 39 do Antigo Testamento protestante. É o cânon das Bíblias de referência protestantes.',
	},
	catolico: {
		nome: 'Cânon católico',
		rotulo: 'Católico',
		descricao:
			'Os 39 protocanônicos mais os deuterocanônicos: Tobias, Judite, Sabedoria, Eclesiástico, Baruque, 1 e 2 Macabeus, e as adições gregas a Ester e Daniel. Fixado em Trento (1546).',
	},
	ortodoxo: {
		nome: 'Cânon ortodoxo',
		rotulo: 'Ortodoxo',
		descricao:
			'Os livros católicos mais 1 Esdras, 2 Esdras, 3 e 4 Macabeus, o Salmo 151 e a Oração de Manassés — extensão variável entre as igrejas autocéfalas.',
	},
	etiope: {
		nome: 'Cânon etíope (Tewahedo)',
		rotulo: 'Etíope (Tewahedo)',
		descricao:
			'O cânone mais extenso: recebe os livros ortodoxos e acrescenta 1 Enoque, Jubileus, 1–3 Meqabyan e 4 Baruque (Paralipômenos de Jeremias), preservados em ge’ez.',
	},
} as const;

export type Canon = keyof typeof CANONES;

/**
 * BLOCOS — a ordem de leitura dentro de uma grade.
 *
 * Não substitui o cânon: serve à exibição. Um leitor procura "os profetas"
 * antes de procurar "o que Trento acrescentou", mas precisa das duas coisas.
 */
export const BLOCOS = [
	'Pentateuco',
	'Históricos',
	'Sapienciais',
	'Profetas',
	'Deuterocanônicos',
	'Ortodoxos',
	'Etíopes',
] as const;

export type Bloco = (typeof BLOCOS)[number];

/**
 * LIVROS — a coluna vertebral do núcleo.
 *
 * Cada livro tem endereço próprio (`/biblia/<slug>/`) com as passagens
 * estudadas. É por aqui que o núcleo cresce: uma passagem por vez, sem
 * engordar nenhuma página até o ponto de não poder ser editada.
 *
 * `ordem` segue a sequência canônica católica (a mais completa entre as
 * tradições ocidentais) e continua depois com os livros ortodoxos e etíopes,
 * para que a grade nunca precise ser renumerada ao receber um livro novo.
 *
 * O nome na língua original vai em `original` + `lang` — hebraico quando há
 * (incipit massorético), grego para os livros de transmissão grega, ge’ez para
 * os exclusivos etíopes. NÃO inventar: livro sem forma original segura fica
 * sem o campo, e o hub simplesmente não o exibe.
 *
 * `abrev`, `en` e `slugCat` existem para montar link a Bíblia online: cada
 * site tem o seu esquema de URL. Quais traduções valem para um livro decorre
 * do cânon que ele segue (ver `bibliasPara`) — os catálogos protestantes só
 * trazem o cânon hebraico. Não inventar slug novo sem conferir por HTTP.
 */
export const LIVROS = {
	// ---------------------------------------------------------------- Pentateuco
	genesis: {
		nome: 'Gênesis',
		original: 'בְּרֵאשִׁית',
		lang: 'he',
		translit: 'Bereshit',
		ordem: 1,
		bloco: 'Pentateuco',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'gn',
		en: 'Genesis',
		slugCat: 'genesis',
	},
	exodo: {
		nome: 'Êxodo',
		original: 'שְׁמוֹת',
		lang: 'he',
		translit: 'Shemot',
		ordem: 2,
		bloco: 'Pentateuco',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ex',
		en: 'Exodus',
		slugCat: 'exodo',
	},
	levitico: {
		nome: 'Levítico',
		original: 'וַיִּקְרָא',
		lang: 'he',
		translit: 'Vayikra',
		ordem: 3,
		bloco: 'Pentateuco',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'lv',
		en: 'Leviticus',
		slugCat: 'levitico',
	},
	numeros: {
		nome: 'Números',
		original: 'בְּמִדְבַּר',
		lang: 'he',
		translit: 'Bemidbar',
		ordem: 4,
		bloco: 'Pentateuco',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'nm',
		en: 'Numbers',
		slugCat: 'numeros',
	},
	deuteronomio: {
		nome: 'Deuteronômio',
		original: 'דְּבָרִים',
		lang: 'he',
		translit: 'Devarim',
		ordem: 5,
		bloco: 'Pentateuco',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'dt',
		en: 'Deuteronomy',
		slugCat: 'deuteronomio',
	},

	// --------------------------------------------------------------- Históricos
	josue: {
		nome: 'Josué',
		original: 'יְהוֹשֻׁעַ',
		lang: 'he',
		translit: 'Yehoshua',
		ordem: 6,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'js',
		en: 'Joshua',
		slugCat: 'josue',
	},
	juizes: {
		nome: 'Juízes',
		original: 'שׁוֹפְטִים',
		lang: 'he',
		translit: 'Shoftim',
		ordem: 7,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'jz',
		en: 'Judges',
		slugCat: 'juizes',
	},
	rute: {
		nome: 'Rute',
		original: 'רוּת',
		lang: 'he',
		translit: 'Rut',
		ordem: 8,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'rt',
		en: 'Ruth',
		slugCat: 'rute',
	},
	'samuel-1': {
		nome: '1 Samuel',
		original: 'שְׁמוּאֵל',
		lang: 'he',
		translit: 'Shemuel',
		ordem: 9,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: '1sm',
		en: '1 Samuel',
		slugCat: '1-samuel',
	},
	'samuel-2': {
		nome: '2 Samuel',
		original: 'שְׁמוּאֵל',
		lang: 'he',
		translit: 'Shemuel',
		ordem: 10,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: '2sm',
		en: '2 Samuel',
		slugCat: '2-samuel',
	},
	'reis-1': {
		nome: '1 Reis',
		original: 'מְלָכִים',
		lang: 'he',
		translit: 'Melakhim',
		ordem: 11,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: '1rs',
		en: '1 Kings',
		slugCat: '1-reis',
	},
	'reis-2': {
		nome: '2 Reis',
		original: 'מְלָכִים',
		lang: 'he',
		translit: 'Melakhim',
		ordem: 12,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: '2rs',
		en: '2 Kings',
		slugCat: '2-reis',
	},
	'cronicas-1': {
		nome: '1 Crônicas',
		original: 'דִּבְרֵי הַיָּמִים',
		lang: 'he',
		translit: 'Divrei ha-Yamim',
		ordem: 13,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: '1cr',
		en: '1 Chronicles',
		slugCat: 'i-cronicas',
	},
	'cronicas-2': {
		nome: '2 Crônicas',
		original: 'דִּבְרֵי הַיָּמִים',
		lang: 'he',
		translit: 'Divrei ha-Yamim',
		ordem: 14,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: '2cr',
		en: '2 Chronicles',
		slugCat: 'ii-cronicas',
	},
	esdras: {
		nome: 'Esdras',
		original: 'עֶזְרָא',
		lang: 'he',
		translit: 'Ezra',
		ordem: 15,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ed',
		en: 'Ezra',
		slugCat: 'esdras',
	},
	neemias: {
		nome: 'Neemias',
		original: 'נְחֶמְיָה',
		lang: 'he',
		translit: 'Nehemyah',
		ordem: 16,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ne',
		en: 'Nehemiah',
		slugCat: 'neemias',
	},
	tobias: {
		nome: 'Tobias',
		original: 'Τωβίτ',
		lang: 'grc',
		translit: 'Tōbit',
		ordem: 17,
		bloco: 'Históricos',
		tradicoes: ['catolico', 'ortodoxo', 'etiope'],
		abrev: 'tb',
		en: 'Tobit',
		slugCat: 'tobias',
	},
	judite: {
		nome: 'Judite',
		original: 'Ἰουδίθ',
		lang: 'grc',
		translit: 'Ioudith',
		ordem: 18,
		bloco: 'Históricos',
		tradicoes: ['catolico', 'ortodoxo', 'etiope'],
		abrev: 'jt',
		en: 'Judith',
		slugCat: 'judite',
	},
	ester: {
		nome: 'Ester',
		original: 'אֶסְתֵּר',
		lang: 'he',
		translit: 'Ester',
		ordem: 19,
		bloco: 'Históricos',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'et',
		en: 'Esther',
		slugCat: 'ester',
	},
	'macabeus-1': {
		nome: '1 Macabeus',
		original: 'Μακκαβαίων Α',
		lang: 'grc',
		translit: 'Makkabaiōn A',
		ordem: 20,
		bloco: 'Históricos',
		tradicoes: ['catolico', 'ortodoxo'],
		abrev: '1mc',
		en: '1 Maccabees',
		slugCat: 'i-macabeus',
	},
	'macabeus-2': {
		nome: '2 Macabeus',
		original: 'Μακκαβαίων Β',
		lang: 'grc',
		translit: 'Makkabaiōn B',
		ordem: 21,
		bloco: 'Históricos',
		tradicoes: ['catolico', 'ortodoxo'],
		abrev: '2mc',
		en: '2 Maccabees',
		slugCat: 'ii-macabeus',
	},

	// -------------------------------------------------------------- Sapienciais
	jo: {
		nome: 'Jó',
		original: 'אִיּוֹב',
		lang: 'he',
		translit: 'Iyyov',
		ordem: 22,
		bloco: 'Sapienciais',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'job',
		en: 'Job',
		slugCat: 'jo',
	},
	salmos: {
		nome: 'Salmos',
		original: 'תְּהִלִּים',
		lang: 'he',
		translit: 'Tehillim',
		ordem: 23,
		bloco: 'Sapienciais',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'sl',
		en: 'Psalms',
		slugCat: 'salmos',
	},
	proverbios: {
		nome: 'Provérbios',
		original: 'מִשְׁלֵי',
		lang: 'he',
		translit: 'Mishlei',
		ordem: 24,
		bloco: 'Sapienciais',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'pv',
		en: 'Proverbs',
		slugCat: 'proverbios',
	},
	coelet: {
		nome: 'Eclesiastes (Coélet)',
		original: 'קֹהֶלֶת',
		lang: 'he',
		translit: 'Qohelet',
		ordem: 25,
		bloco: 'Sapienciais',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ec',
		en: 'Ecclesiastes',
		slugCat: 'eclesiastes',
	},
	cantico: {
		nome: 'Cântico dos Cânticos',
		original: 'שִׁיר הַשִּׁירִים',
		lang: 'he',
		translit: 'Shir ha-Shirim',
		ordem: 26,
		bloco: 'Sapienciais',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ct',
		en: 'Song of Solomon',
		slugCat: 'cantico-dos-canticos',
	},
	sabedoria: {
		nome: 'Sabedoria',
		original: 'Σοφία Σαλωμῶνος',
		lang: 'grc',
		translit: 'Sophia Salōmōnos',
		ordem: 27,
		bloco: 'Sapienciais',
		tradicoes: ['catolico', 'ortodoxo', 'etiope'],
		abrev: 'sb',
		en: 'Wisdom',
		slugCat: 'sabedoria',
	},
	eclesiastico: {
		nome: 'Eclesiástico (Sirácide)',
		original: 'Σοφία Σιράχ',
		lang: 'grc',
		translit: 'Sophia Sirach',
		ordem: 28,
		bloco: 'Sapienciais',
		tradicoes: ['catolico', 'ortodoxo', 'etiope'],
		abrev: 'eclo',
		en: 'Sirach',
		slugCat: 'eclesiastico',
	},

	// ---------------------------------------------------------------- Profetas
	isaias: {
		nome: 'Isaías',
		original: 'יְשַׁעְיָהוּ',
		lang: 'he',
		translit: 'Yeshayahu',
		ordem: 29,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'is',
		en: 'Isaiah',
		slugCat: 'isaias',
	},
	jeremias: {
		nome: 'Jeremias',
		original: 'יִרְמְיָהוּ',
		lang: 'he',
		translit: 'Yirmeyahu',
		ordem: 30,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'jr',
		en: 'Jeremiah',
		slugCat: 'jeremias',
	},
	lamentacoes: {
		nome: 'Lamentações',
		original: 'אֵיכָה',
		lang: 'he',
		translit: 'Eikhah',
		ordem: 31,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'lm',
		en: 'Lamentations',
		slugCat: 'lamentacoes',
	},
	baruque: {
		nome: 'Baruque',
		original: 'Βαρούχ',
		lang: 'grc',
		translit: 'Barouch',
		ordem: 32,
		bloco: 'Profetas',
		tradicoes: ['catolico', 'ortodoxo', 'etiope'],
		abrev: 'br',
		en: 'Baruch',
		slugCat: 'baruc',
	},
	ezequiel: {
		nome: 'Ezequiel',
		original: 'יְחֶזְקֵאל',
		lang: 'he',
		translit: 'Yehezqel',
		ordem: 33,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ez',
		en: 'Ezekiel',
		slugCat: 'ezequiel',
	},
	daniel: {
		nome: 'Daniel',
		original: 'דָּנִיֵּאל',
		lang: 'he',
		translit: 'Daniyyel',
		ordem: 34,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'dn',
		en: 'Daniel',
		slugCat: 'daniel',
	},
	oseias: {
		nome: 'Oséias',
		original: 'הוֹשֵׁעַ',
		lang: 'he',
		translit: 'Hoshea',
		ordem: 35,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'os',
		en: 'Hosea',
		slugCat: 'oseias',
	},
	joel: {
		nome: 'Joel',
		original: 'יוֹאֵל',
		lang: 'he',
		translit: 'Yoel',
		ordem: 36,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'jl',
		en: 'Joel',
		slugCat: 'joel',
	},
	amos: {
		nome: 'Amós',
		original: 'עָמוֹס',
		lang: 'he',
		translit: 'Amos',
		ordem: 37,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'am',
		en: 'Amos',
		slugCat: 'amos',
	},
	obadias: {
		nome: 'Obadias',
		original: 'עֹבַדְיָה',
		lang: 'he',
		translit: 'Ovadyah',
		ordem: 38,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ob',
		en: 'Obadiah',
		slugCat: 'abdias',
	},
	jonas: {
		nome: 'Jonas',
		original: 'יוֹנָה',
		lang: 'he',
		translit: 'Yonah',
		ordem: 39,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'jn',
		en: 'Jonah',
		slugCat: 'jonas',
	},
	miqueias: {
		nome: 'Miqueias',
		original: 'מִיכָה',
		lang: 'he',
		translit: 'Mikhah',
		ordem: 40,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'mq',
		en: 'Micah',
		slugCat: 'miqueias',
	},
	naum: {
		nome: 'Naum',
		original: 'נַחוּם',
		lang: 'he',
		translit: 'Nahum',
		ordem: 41,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'na',
		en: 'Nahum',
		slugCat: 'naum',
	},
	habacuque: {
		nome: 'Habacuque',
		original: 'חֲבַקּוּק',
		lang: 'he',
		translit: 'Havaqquq',
		ordem: 42,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'hc',
		en: 'Habakkuk',
		slugCat: 'habacuc',
	},
	sofonias: {
		nome: 'Sofonias',
		original: 'צְפַנְיָה',
		lang: 'he',
		translit: 'Tsefanyah',
		ordem: 43,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'sf',
		en: 'Zephaniah',
		slugCat: 'sofonias',
	},
	ageu: {
		nome: 'Ageu',
		original: 'חַגַּי',
		lang: 'he',
		translit: 'Haggai',
		ordem: 44,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ag',
		en: 'Haggai',
		slugCat: 'ageu',
	},
	zacarias: {
		nome: 'Zacarias',
		original: 'זְכַרְיָה',
		lang: 'he',
		translit: 'Zekharyah',
		ordem: 45,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'zc',
		en: 'Zechariah',
		slugCat: 'zacarias',
	},
	malaquias: {
		nome: 'Malaquias',
		original: 'מַלְאָכִי',
		lang: 'he',
		translit: 'Malakhi',
		ordem: 46,
		bloco: 'Profetas',
		tradicoes: ['hebraico', 'catolico', 'ortodoxo', 'etiope'],
		abrev: 'ml',
		en: 'Malachi',
		slugCat: 'malaquias',
	},

	// --------------------------------------------------- Deuterocanônicos/ortodoxos
	'esdras-1': {
		nome: '1 Esdras',
		original: 'Ἔσδρας Α',
		lang: 'grc',
		translit: 'Esdras A',
		ordem: 47,
		bloco: 'Ortodoxos',
		tradicoes: ['ortodoxo', 'etiope'],
	},
	'esdras-2': {
		nome: '2 Esdras',
		original: 'Ἔσδρας Β',
		lang: 'grc',
		translit: 'Esdras B',
		ordem: 48,
		bloco: 'Ortodoxos',
		tradicoes: ['ortodoxo', 'etiope'],
	},
	'oracao-manasses': {
		nome: 'Oração de Manassés',
		original: 'Προσευχὴ Μανασσῆ',
		lang: 'grc',
		translit: 'Proseuchē Manassē',
		ordem: 49,
		bloco: 'Ortodoxos',
		tradicoes: ['ortodoxo', 'etiope'],
	},
	'salmo-151': {
		nome: 'Salmo 151',
		original: 'Ψαλμὸς ΡΝΑ',
		lang: 'grc',
		translit: 'Psalmos 151',
		ordem: 50,
		bloco: 'Ortodoxos',
		tradicoes: ['ortodoxo', 'etiope'],
	},
	'macabeus-3': {
		nome: '3 Macabeus',
		original: 'Μακκαβαίων Γ',
		lang: 'grc',
		translit: 'Makkabaiōn G',
		ordem: 51,
		bloco: 'Ortodoxos',
		tradicoes: ['ortodoxo'],
	},
	'macabeus-4': {
		nome: '4 Macabeus',
		original: 'Μακκαβαίων Δ',
		lang: 'grc',
		translit: 'Makkabaiōn D',
		ordem: 52,
		bloco: 'Ortodoxos',
		tradicoes: ['ortodoxo'],
	},

	// ------------------------------------------------------------------ Etíopes
	'enoque-1': {
		nome: '1 Enoque',
		original: 'መጽሐፈ ሄኖክ',
		lang: 'gez',
		translit: 'Maṣḥafa Hēnok',
		ordem: 53,
		bloco: 'Etíopes',
		tradicoes: ['etiope'],
	},
	jubileus: {
		nome: 'Jubileus',
		original: 'መጽሐፈ ኩፋሌ',
		lang: 'gez',
		translit: 'Maṣḥafa Kufālē',
		ordem: 54,
		bloco: 'Etíopes',
		tradicoes: ['etiope'],
	},
	'meqabyan-1': {
		nome: '1 Meqabyan',
		original: 'መቃብያን',
		lang: 'gez',
		translit: 'Mäqabǝyan 1',
		ordem: 55,
		bloco: 'Etíopes',
		tradicoes: ['etiope'],
	},
	'meqabyan-2': {
		nome: '2 Meqabyan',
		original: 'መቃብያን',
		lang: 'gez',
		translit: 'Mäqabǝyan 2',
		ordem: 56,
		bloco: 'Etíopes',
		tradicoes: ['etiope'],
	},
	'meqabyan-3': {
		nome: '3 Meqabyan',
		original: 'መቃብያን',
		lang: 'gez',
		translit: 'Mäqabǝyan 3',
		ordem: 57,
		bloco: 'Etíopes',
		tradicoes: ['etiope'],
	},
	'baruque-4': {
		nome: '4 Baruque (Paralipômenos de Jeremias)',
		original: 'ብሩክ ዘርእየ',
		lang: 'gez',
		translit: 'Baruk za-ri’ya',
		ordem: 58,
		bloco: 'Etíopes',
		tradicoes: ['ortodoxo', 'etiope'],
	},
} as const;

export type Livro = keyof typeof LIVROS;
export type LivroMeta = (typeof LIVROS)[Livro];

/**
 * Catálogo de bíblias online em PT, com a tradição declarada.
 *
 * `exigeCanon` não é enfeite: um catálogo protestante simplesmente não tem
 * Tobias, Sabedoria ou 1 Macabeus (conferido por HTTP em 12-set-2026 — todos
 * 404), e oferecer o link seria prometer o que não existe. O componente filtra
 * pelo cânon que o livro segue, e quando nenhuma tradução do catálogo o
 * recebe ele diz isso em vez de renderizar uma lista vazia.
 *
 * Os padrões de URL foram conferidos por HTTP em 12-set-2026:
 *   - bibliaonline.com.br/ara/<abrev>/<cap> — 200 para os 39 livros conferidos.
 *     ARMADILHA: `jo` ali é JOÃO, não Jó — o Abreviado de Jó é `job`; `ab` dá
 *     404, e Obadias é `ob`.
 *   - bibliacatolica.com.br/biblia-ave-maria/<slug>/<cap>/ — 200 para
 *     Gênesis…Malaquias e para os deuterocanônicos. ARMADILHA: os slugs não
 *     seguem o nome (Baruque é `baruc`, Habacuque é `habacuc`, Obadias é
 *     `abdias`, crônicas são `i-cronicas`/`ii-cronicas`, macabeus são
 *     `i-macabeus`/`ii-macabeus`).
 */
export const BIBLIAS = [
	{
		id: 'ara',
		nome: 'Almeida Revista e Atualizada',
		sigla: 'ARA',
		tradicao: 'protestante',
		exigeCanon: 'hebraico',
		url: (l: LivroMeta, cap: string) =>
			`https://www.bibliaonline.com.br/ara/${l.abrev}/${cap}`,
	},
	{
		id: 'nvi',
		nome: 'Nova Versão Internacional',
		sigla: 'NVI',
		tradicao: 'protestante',
		exigeCanon: 'hebraico',
		url: (l: LivroMeta, cap: string) =>
			`https://www.bibliaonline.com.br/nvi/${l.abrev}/${cap}`,
	},
	{
		id: 'ave-maria',
		nome: 'Ave-Maria',
		sigla: 'Ave-Maria',
		tradicao: 'católica',
		exigeCanon: 'catolico',
		url: (l: LivroMeta, cap: string) =>
			`https://www.bibliacatolica.com.br/biblia-ave-maria/${l.slugCat}/${cap.split('-')[0]}/`,
	},
	{
		id: 'nvi-pt-gateway',
		nome: 'NVI (BibleGateway)',
		sigla: 'NVI',
		tradicao: 'protestante',
		exigeCanon: 'hebraico',
		url: (l: LivroMeta, cap: string) =>
			`https://www.biblegateway.com/passage/?search=${encodeURIComponent(`${l.en} ${cap}`)}&version=NVI-PT`,
	},
	{
		id: 'livre',
		nome: 'Bíblia Livre',
		sigla: 'livre',
		tradicao: 'licença aberta',
		exigeCanon: 'hebraico',
		url: () => 'https://ebible.org/find/show.php?id=porblivre',
	},
] as const;

/** Traduções online que recebem um livro, conforme o cânon que ele segue. */
export const bibliasPara = (slug: string) => {
	const trad = (LIVROS as Record<string, { tradicoes: readonly string[] }>)[slug]?.tradicoes ?? [];
	return BIBLIAS.filter((b) =>
		(trad as readonly string[]).includes((b as { exigeCanon: string }).exigeCanon)
	);
};

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
		descricao:
			'Comparação com a mitologia, as perguntas filosóficas, os debates teológicos e o que a ciência diz — e onde não tem competência.',
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

/** Rótulo de área pronto para exibição, com fallback. */
export const rotuloArea = (a: string): string => (AREAS as Record<string, string>)[a] ?? a;

/** Rótulo do livro, com fallback para o slug. */
export const rotuloLivro = (l: string): string =>
	(LIVROS as Record<string, { nome: string }>)[l]?.nome ?? l;

/** Rótulo do cânon, com fallback para o slug. */
export const rotuloCanon = (c: string): string =>
	(CANONES as Record<string, { rotulo: string }>)[c]?.rotulo ?? c;

/** Livros de um cânon, na ordem canônica. */
export const livrosDoCanon = (canon: Canon) =>
	Object.entries(LIVROS)
		.filter(([, m]) => (m.tradicoes as readonly string[]).includes(canon))
		.sort((a, b) => a[1].ordem - b[1].ordem)
		.map(([slug, meta]) => ({ slug, meta }));

/** O livro é recebido pelo cânon hebraico/protestante? */
export const noCanonHebraico = (slug: string) =>
	((LIVROS as Record<string, { tradicoes: readonly string[] }>)[slug]?.tradicoes ?? []).includes(
		'hebraico'
	);

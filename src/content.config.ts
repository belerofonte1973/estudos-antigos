import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { EIXOS, AREAS, LIVROS } from './taxonomia';

/**
 * Schemas das coleções de conteúdo.
 *
 * As constantes compartilhadas (eixos, áreas, livros) vivem em
 * `src/taxonomia.ts` e NÃO aqui — importar este arquivo de dentro de um
 * componente cria um ciclo via `astro:content` e as constantes chegam
 * indefinidas no build. Componentes importam de `taxonomia`, não daqui.
 */

const areaEnum = z.enum(Object.keys(AREAS) as [string, ...string[]]);
const eixoEnum = z.enum(Object.keys(EIXOS) as [string, ...string[]]);
const livrosEnum = z.enum(Object.keys(LIVROS) as [string, ...string[]]);

/**
 * BIBLIOTECA — dossiês longos. É o destino; não é otimizado para busca.
 *
 * `eixo` diz onde o material se posiciona no modelo; `area` diz a que
 * disciplina pertence. Um dossiê sobre o dilúvio é `nucleo` + `biblia`;
 * o da Suméria é `contexto` + `oriente`, e passa a aparecer ao lado certo.
 */
const biblioteca = defineCollection({
	loader: glob({ pattern: '**/*.mdx', base: './src/content/biblioteca' }),
	schema: z.object({
		title: z.string(),
		description: z.string(),
		eixo: eixoEnum,
		area: areaEnum,
		ordem: z.number().default(99),
		atualizado: z.coerce.date().optional(),
		/** Slug em `artigos` que serve de porta de entrada para este dossiê. */
		entrada: z.string().optional(),
		/** Livro bíblico relacionado, quando o dossiê trata de um só. */
		livro: livrosEnum.optional(),
		/**
		 * Livros cobertos, quando o dossiê trata a unidade canônica.
		 * No cânon hebraico Samuel e Reis não são divididos em 1 e 2 — o
		 * dossiê cobre os dois, e os dois hubs de livro apontam para ele.
		 */
		livros: z.array(livrosEnum).default([]),
	}),
});

/**
 * ARTIGOS — a revista. Uma pergunta por endereço.
 *
 * `pergunta` e `respostaRapida` não são decoração: são os campos que ganham
 * trecho em destaque no Google e citação em respostas de IA.
 */
const artigos = defineCollection({
	loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/artigos' }),
	schema: z.object({
		titulo: z.string(),
		pergunta: z.string(),
		/** Meta description. Limite real de SERP: ~160 caracteres. */
		descricao: z.string().max(160),
		/** 2 a 4 frases de resposta direta. Alimenta FAQPage e trecho em destaque. */
		respostaRapida: z.string(),
		eixo: eixoEnum,
		area: areaEnum,
		tags: z.array(z.string()).default([]),
		data: z.coerce.date(),
		atualizado: z.coerce.date().optional(),
		destaque: z.number().default(99),
		/** Slug do dossiê correspondente em `biblioteca`. */
		dossie: z.string().optional(),
		/** Livro bíblico, quando o artigo for sobre um. */
		livro: livrosEnum.optional(),
		/** URL do vídeo curto vertical derivado deste artigo. */
		video: z.string().optional(),
		fontes: z
			.array(z.object({ texto: z.string(), url: z.string().optional() }))
			.default([]),
	}),
});

/**
 * PASSAGENS — a unidade atômica do núcleo bíblico.
 *
 * A granularidade de um estudo bíblico não é o livro, é a passagem: Gênesis 1
 * não discute o mesmo que Gênesis 6–9 nem que Gênesis 22. Cada passagem tem
 * as três seções — Texto, Contexto, Recepção — e é isso que liga os eixos
 * num único endereço, em vez de espalhá-los por três ilhas.
 */
const passagens = defineCollection({
	loader: glob({ pattern: '**/*.mdx', base: './src/content/passagens' }),
	schema: z.object({
		livro: livrosEnum,
		/** Como se cita: "Gênesis 6–9". */
		referencia: z.string(),
		titulo: z.string(),
		pergunta: z.string(),
		descricao: z.string().max(160),
		respostaRapida: z.string(),
		ordem: z.number().default(99),
		data: z.coerce.date(),
		atualizado: z.coerce.date().optional(),
		dossie: z.string().optional(),
		temas: z.array(z.string()).default([]),
		fontes: z
			.array(z.object({ texto: z.string(), url: z.string().optional() }))
			.default([]),
	}),
});

export const collections = { biblioteca, artigos, passagens };

import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/** Áreas de estudo compartilhadas pelas duas coleções. */
export const AREAS = {
	biblia: 'Antiguidade Bíblica',
	classica: 'Antiguidade Clássica',
	'idade-media': 'Idade Média',
	'pre-historia': 'Pré-História',
	oriente: 'Oriente Próximo Antigo',
} as const;

const areaEnum = z.enum(Object.keys(AREAS) as [string, ...string[]]);

/**
 * BIBLIOTECA — dossiês longos, densos, com retroverificação acadêmica.
 * É o destino. Não é otimizado para busca; é otimizado para quem já chegou.
 */
const biblioteca = defineCollection({
	loader: glob({ pattern: '**/*.mdx', base: './src/content/biblioteca' }),
	schema: z.object({
		title: z.string(),
		description: z.string(),
		area: areaEnum,
		ordem: z.number().default(99),
		atualizado: z.coerce.date().optional(),
		/** Slug em `artigos` que serve de porta de entrada para este dossiê. */
		entrada: z.string().optional(),
	}),
});

/**
 * ARTIGOS — a revista. Uma pergunta por endereço.
 *
 * `pergunta` e `respostaRapida` não são decoração: são os campos que ganham
 * trecho em destaque no Google e citação em respostas de IA. A pergunta é
 * escrita como as pessoas realmente digitam, não como um acadêmico escreveria.
 */
const artigos = defineCollection({
	loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/artigos' }),
	schema: z.object({
		titulo: z.string(),
		/** A consulta literal que este artigo responde. */
		pergunta: z.string(),
		/** Meta description. Limite real de SERP: ~160 caracteres. */
		descricao: z.string().max(160),
		/** 2 a 4 frases de resposta direta. Alimenta FAQPage e trecho em destaque. */
		respostaRapida: z.string(),
		area: areaEnum,
		tags: z.array(z.string()).default([]),
		data: z.coerce.date(),
		atualizado: z.coerce.date().optional(),
		/** Menor número aparece primeiro na capa. */
		destaque: z.number().default(99),
		/** Slug do dossiê correspondente em `biblioteca`. */
		dossie: z.string().optional(),
		/** URL do vídeo curto vertical derivado deste artigo. */
		video: z.string().optional(),
		/** Fontes citadas no corpo, para o schema.org. */
		fontes: z
			.array(z.object({ texto: z.string(), url: z.string().optional() }))
			.default([]),
	}),
});

export const collections = { biblioteca, artigos };

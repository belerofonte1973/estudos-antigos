import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
	const artigos = (await getCollection('artigos')).sort(
		(a, b) => b.data.data.getTime() - a.data.data.getTime()
	);

	return rss({
		title: 'Estudos Antigos — Revista',
		description:
			'Perguntas sobre Antiguidade Bíblica, Clássica e Medieval, cada uma respondida com citação de fonte rastreável.',
		site: context.site ?? 'https://estudos-antigos.netlify.app',
		items: artigos.map((a) => ({
			title: a.data.titulo,
			description: a.data.descricao,
			pubDate: a.data.data,
			link: `/artigos/${a.id}/`,
			categories: [a.data.area, ...a.data.tags],
			author: 'Estudos Antigos',
		})),
		customData: `<language>pt-BR</language>`,
		stylesheet: false,
	});
}

// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import remarkLinguasAntigas from './src/plugins/remark-linguas-antigas.mjs';

// ---------------------------------------------------------------------------
// Estudos Antigos — revista + biblioteca
//
// Duas superfícies no mesmo build:
//   /            revista  -> artigos curtos, uma pergunta por endereço (alcance)
//   /biblioteca  biblioteca -> dossiês profundos com sidebar (profundidade)
//
// O Starlight foi removido de propósito: ele serve documentação para quem já
// sabe o que procura. A face pública precisa de <head> livre para SEO,
// schema.org e imagem social por artigo.
// ---------------------------------------------------------------------------

// Trocar por domínio próprio quando existir, ex.: 'https://estudosantigos.com.br'
export const SITE = 'https://estudos-antigos.netlify.app';

export default defineConfig({
	site: SITE,
	trailingSlash: 'ignore',
	integrations: [
		mdx(),
		sitemap({
			// A busca é página de serviço, não conteúdo: fica fora do sitemap e
			// leva `noindex` (ver `src/pages/busca.astro`).
			filter: (page) => !page.includes('/404') && !page.includes('/busca'),
		}),
	],
	markdown: {
		shikiConfig: { theme: 'github-light', wrap: true },
		// Aplica isolamento bidi e atributo lang a hebraico e grego antigo
		// escritos em texto simples no conteúdo.
		remarkPlugins: [remarkLinguasAntigas],
	},
});

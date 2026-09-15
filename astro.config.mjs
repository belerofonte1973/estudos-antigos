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

// Domínio próprio desde 15/set/2026. Trocar aqui muda canonical, sitemap, RSS
// e as URLs de imagem social de todo o site de uma vez — os `Astro.site ??
// 'https://…'` espalhados nos componentes são só fallback para quando este
// campo não está definido.
export const SITE = 'https://altaculturapopular.online';

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

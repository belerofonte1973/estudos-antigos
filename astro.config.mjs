// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://estudos-antigos.netlify.app',
	integrations: [
		starlight({
			title: 'Estudos Antigos — Bíblicos, Clássicos e Medievais',
			description: 'Portal de pesquisa e divulgação sobre Antiguidade Bíblica, Clássica (Grécia e Roma) e Idade Média. Artigos enciclopédicos, bibliografias comentadas e ferramentas de estudo.',
			logo: {
				src: './src/assets/logo.svg',
				alt: 'Estudos Antigos',
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/estudos-antigos' },
				{ icon: 'twitter', label: 'Twitter', href: 'https://twitter.com/estudos_antigos' },
			],
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{
					label: 'Início',
					slug: 'index',
				},
				{
					label: 'Antiguidade Bíblica',
					items: [
						{ label: 'Introdução', slug: 'biblia/introducao' },
						{ label: 'Gênesis (Bereshit)', slug: 'biblia/genesis' },
						{ label: 'Êxodo (Shemot)', slug: 'biblia/exodo' },
						{ label: 'Levítico (Vayikra)', slug: 'biblia/levitico' },
						{ label: 'Números (Bemidbar)', slug: 'biblia/numeros' },
						{ label: 'Deuteronômio (Devarim)', slug: 'biblia/deuteronomio' },
						{ label: 'Suméria', slug: 'biblia/sumeria' },
					],
				},
				{
					label: 'Antiguidade Clássica',
					items: [
						{ label: 'Introdução', slug: 'classica/introducao' },
					],
				},
				{
					label: 'Idade Média',
					items: [
						{ label: 'Introdução', slug: 'idade-media/introducao' },
					],
				},
				{
					label: 'Ferramentas de Estudo',
					items: [
						{ label: 'Como Pesquisar', slug: 'ferramentas/como-pesquisar' },
					],
				},
				{
					label: 'Sobre',
					items: [
						{ label: 'O Projeto', slug: 'sobre' },
						{ label: 'Contribua', slug: 'sobre/contribua' },
						{ label: 'Contato', slug: 'sobre/contato' },
					],
				},
			],
		}),
	],
});

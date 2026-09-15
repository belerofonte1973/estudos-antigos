// Gera as imagens sociais (Open Graph / Twitter Card) do site:
//
//   public/og-default.png          capa padrão (fallback de qualquer página)
//   public/og/<area>-<slug>.png    uma por dossiê da biblioteca
//   public/og/revista-<slug>.png   uma por artigo da revista
//
// A fonte dos dados é o PRÓPRIO frontmatter dos arquivos de conteúdo, não o
// build: assim o script roda antes do `astro build` e não depende de nada
// compilado. O caminho declarado por página é montado nos layouts
// (`BibliotecaLayout` usa o id `area/slug`; `ArtigoLayout`, `revista-<slug>`),
// e `scripts/conferir_og.py` confere que todo <meta og:image> do build aponta
// para um arquivo que existe — o par que impede a imagem sumir em silêncio.
//
// O texto é desenhado em SVG e rasterizado pelo sharp (librsvg). Como a fonte
// disponível varia por sistema, o script VERIFICA se o texto foi realmente
// renderizado (rasteriza com e sem texto e compara os bytes); se não foi, cai
// para um layout sem tipografia — imagem limpa é melhor que imagem vazia.

import sharp from 'sharp';
import { readFileSync, readdirSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';

const W = 1200;
const H = 630;

const BORDA = '#6b4423';
const FUNDO = '#f6f5f4';
const TINTA = '#1a1a1a';
const SUAVE = '#615d59';

const RAIZ = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const CONTEUDO = join(RAIZ, 'src', 'content');
const SAIDA = join(RAIZ, 'public', 'og');

// ------------------------------------------------------------------ taxonomia
// AREAS lida do próprio `src/taxonomia.ts` — duplicar os rótulos aqui criaria
// uma segunda verdade que envelhece calada.
const AREAS = (() => {
	const ts = readFileSync(join(RAIZ, 'src', 'taxonomia.ts'), 'utf8');
	const bloco = /export const AREAS = \{([\s\S]*?)\} as const;/.exec(ts)?.[1] ?? '';
	const mapa = {};
	for (const m of bloco.matchAll(/['"]?([\w-]+)['"]?:\s*'([^']+)'/g)) mapa[m[1]] = m[2];
	return mapa;
})();

// ------------------------------------------------------------------ frontmatter
const campo = (texto, chave) => {
	const m = new RegExp(`^${chave}:\\s*(.+)$`, 'm').exec(texto);
	return m ? m[1].trim().replace(/^['"]|['"]$/g, '').replace(/''/g, "'") : '';
};

const arquivosDe = (dir, extensao) => {
	const out = [];
	for (const e of readdirSync(dir, { withFileTypes: true })) {
		const p = join(dir, e.name);
		if (e.isDirectory()) out.push(...arquivosDe(p, extensao));
		else if (e.name.endsWith(extensao)) out.push(p);
	}
	return out;
};

/** Título de capa: sem o sufixo de gênero, que não diz nada no compartilhamento. */
const limparTitulo = (t) =>
	t
		.replace(/\s+—\s+(Artigo|Dossiê|Dossie)\s+Enciclopédico.*$/i, '')
		.replace(/\s+—\s+(Dossiê|Dossier)$/i, '')
		.trim();

/** Quebra em linhas por palavra, respeitando o limite de caracteres. */
const quebrar = (texto, maxChars, maxLinhas) => {
	const linhas = [];
	let atual = '';
	for (const palavra of texto.split(/\s+/)) {
		const tentativa = atual ? `${atual} ${palavra}` : palavra;
		if (tentativa.length <= maxChars) atual = tentativa;
		else {
			if (atual) linhas.push(atual);
			atual = palavra;
		}
	}
	if (atual) linhas.push(atual);
	if (linhas.length <= maxLinhas) return linhas;

	// Título longo demais: redistribui em maxLinhas equilibradas.
	const total = texto.length;
	const alvo = Math.ceil(total / maxLinhas) + 4;
	return quebrar(texto, alvo, maxLinhas + 1);
};

const marca = (cx, cy, escala, cor) => {
	const s = escala;
	const path = `
		M ${cx} ${cy - 4.4 * s}
		c ${-2.6 * s} ${-1.9 * s} ${-6.1 * s} ${-2.5 * s} ${-9.4 * s} ${-2.3 * s}
		v ${17.4 * s}
		c ${3.3 * s} ${-0.2 * s} ${6.8 * s} ${0.4 * s} ${9.4 * s} ${2.3 * s}
		c ${2.6 * s} ${-1.9 * s} ${6.1 * s} ${-2.5 * s} ${9.4 * s} ${-2.3 * s}
		v ${-17.4 * s}
		c ${-3.3 * s} ${-0.2 * s} ${-6.8 * s} ${0.4 * s} ${-9.4 * s} ${2.3 * s} Z
	`;
	return `<path d="${path}" fill="none" stroke="${cor}" stroke-width="${1.7 * s}" stroke-linejoin="round" stroke-linecap="round"/>
	        <path d="M ${cx} ${cy - 4.4 * s} v ${17.4 * s}" fill="none" stroke="${cor}" stroke-width="${1.7 * s}"/>`;
};

const escapar = (s) =>
	s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** SVG de uma página (dossiê ou artigo). */
const svgPagina = ({ titulo, eyebrow }) => {
	const linhas = quebrar(titulo, 27, 3);
	const corpo = linhas
		.map(
			(l, i) =>
				`<text x="0" y="${i * 76}" font-size="62" font-weight="700" fill="${TINTA}" letter-spacing="-1.4">${escapar(l)}</text>`
		)
		.join('\n\t\t');

	return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
	<rect width="${W}" height="${H}" fill="${FUNDO}"/>
	<rect x="0" y="0" width="10" height="${H}" fill="${BORDA}"/>

	<g transform="translate(96, 74)">
		${marca(0, 40, 1.9, BORDA)}
	</g>
	<g transform="translate(150, 92)" font-family="Georgia, 'Times New Roman', serif">
		<text x="0" y="0" font-size="30" font-weight="700" fill="${TINTA}" letter-spacing="-0.5">Estudos Antigos</text>
	</g>

	<g transform="translate(96, 216)" font-family="Arial, Helvetica, sans-serif">
		<text x="0" y="0" font-size="23" fill="${SUAVE}" letter-spacing="4.5">${escapar(eyebrow.toUpperCase())}</text>
	</g>

	<g transform="translate(96, 330)" font-family="Georgia, 'Times New Roman', serif">
		${corpo}
	</g>

	<rect x="96" y="540" width="72" height="4" fill="${BORDA}"/>
	<g transform="translate(96, 588)" font-family="Georgia, 'Times New Roman', serif">
		<text x="0" y="0" font-size="26" fill="${BORDA}" font-style="italic">Cada afirmação com fonte rastreável.</text>
	</g>
</svg>`;
};

/** Rasteriza e devolve o buffer PNG (paleta reduz o arquivo sem perder texto). */
const render = (svg) =>
	sharp(Buffer.from(svg), { density: 72 })
		.png({ compressionLevel: 9, palette: true, quality: 92 })
		.toBuffer();

// ------------------------------------------- sonda: o librsvg desenha texto?
const sondaSvg = svgPagina({ titulo: 'Sonda tipográfica', eyebrow: 'teste' });
const comTexto = await render(sondaSvg);
const semTexto = await render(
	sondaSvg.replace(/<text[\s\S]*?<\/text>/g, '').replace(/<g transform="translate\(96, 330\)"[\s\S]*?<\/g>/, '')
);
const textoRenderizou = Buffer.compare(comTexto, semTexto) !== 0;

if (!textoRenderizou) {
	console.log(
		'⚠ librsvg não desenhou texto neste sistema — as imagens sairão sem tipografia.\n' +
			'  Título e descrição continuam nos metadados og:title / og:description.'
	);
}

// ------------------------------------------------------------------ coleta
const paginas = [];

for (const caminho of arquivosDe(join(CONTEUDO, 'biblioteca'), '.mdx')) {
	const texto = readFileSync(caminho, 'utf8');
	const id = caminho
		.slice(join(CONTEUDO, 'biblioteca').length + 1)
		.replace(/\.mdx$/, '')
		.split(/[\\/]/)
		.join('/');
	const area = campo(texto, 'area') || id.split('/')[0];
	const bruto = campo(texto, 'title') || campo(texto, 'titulo') || basename(caminho, '.mdx');
	paginas.push({
		arquivo: `${id.replace(/\//g, '-')}.png`,
		titulo: limparTitulo(bruto),
		eyebrow: `Biblioteca · ${AREAS[area] ?? area}`,
		origem: `biblioteca/${id}`,
	});
}

for (const caminho of arquivosDe(join(CONTEUDO, 'artigos'), '.md')) {
	const texto = readFileSync(caminho, 'utf8');
	const slug = basename(caminho, '.md');
	const area = campo(texto, 'area');
	paginas.push({
		arquivo: `revista-${slug}.png`,
		titulo: limparTitulo(campo(texto, 'titulo') || campo(texto, 'title') || slug),
		eyebrow: `Revista · ${AREAS[area] ?? area}`,
		origem: `artigos/${slug}`,
	});
}

mkdirSync(SAIDA, { recursive: true });

let bytes = 0;
let geradas = 0;
for (const p of paginas) {
	const destino = join(SAIDA, p.arquivo);
	const buffer = textoRenderizou ? await render(svgPagina(p)) : await render(svgPagina({ ...p, titulo: '' }));
	const anterior = existsSync(destino) ? statSync(destino).size : 0;
	const { writeFileSync } = await import('node:fs');
	writeFileSync(destino, buffer);
	bytes += buffer.length;
	geradas++;
	if (process.argv.includes('--verboso')) {
		const delta = anterior ? ` (antes ${anterior} B)` : '';
		console.log(`  ${p.arquivo.padEnd(44)} ${String(buffer.length).padStart(6)} B${delta}  ${p.titulo}`);
	}
}

console.log(`✓ ${geradas} imagens sociais em public/og/ — ${(bytes / 1024 / 1024).toFixed(2)} MB no total`);

// ------------------------------------------------- capa padrão (fallback)
const svgPadrao = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
	<rect width="${W}" height="${H}" fill="${FUNDO}"/>
	<rect x="0" y="0" width="10" height="${H}" fill="${BORDA}"/>
	<g transform="translate(96, 120)">${marca(0, 60, 2.6, BORDA)}</g>
	${
		textoRenderizou
			? `<g transform="translate(96, 320)" font-family="Georgia, 'Times New Roman', serif">
		<text x="0" y="0" font-size="82" font-weight="700" fill="${TINTA}" letter-spacing="-2">Estudos Antigos</text>
	</g>
	<g transform="translate(98, 386)" font-family="Arial, Helvetica, sans-serif">
		<text x="0" y="0" font-size="27" fill="${SUAVE}" letter-spacing="5">BÍBLICOS · CLÁSSICOS · MEDIEVAIS</text>
	</g>
	<g transform="translate(96, 508)" font-family="Georgia, 'Times New Roman', serif">
		<text x="0" y="0" font-size="33" fill="${BORDA}" font-style="italic">Cada afirmação com fonte rastreável.</text>
	</g>`
			: ''
	}
	<rect x="96" y="452" width="72" height="4" fill="${BORDA}"/>
</svg>`;

const { writeFileSync: escrever } = await import('node:fs');
escrever(join(RAIZ, 'public', 'og-default.png'), await render(svgPadrao));
const meta = await sharp(join(RAIZ, 'public', 'og-default.png')).metadata();
const tamanho = statSync(join(RAIZ, 'public', 'og-default.png')).size;
console.log(`✓ og-default.png · ${meta.width}x${meta.height} · ${tamanho} B`);

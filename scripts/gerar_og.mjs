// Gera public/og-default.png (1200x630) para compartilhamento social.
//
// O texto é desenhado via SVG e rasterizado pelo sharp (librsvg). A fonte
// disponível no librsvg varia por sistema, então o script VERIFICA se o texto
// realmente foi renderizado: rasteriza uma versão com texto e outra sem e
// compara os bytes. Se forem idênticos, o texto não apareceu e o script cai
// para um layout sem tipografia — melhor uma imagem limpa do que uma vazia.

import sharp from 'sharp';
import { writeFileSync } from 'node:fs';

const W = 1200;
const H = 630;

const BORDA = '#6b4423';
const FUNDO = '#f6f5f4';
const TINTA = '#1a1a1a';
const SUAVE = '#615d59';

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

const svg = (comTexto) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
	<rect width="${W}" height="${H}" fill="${FUNDO}"/>
	<rect x="0" y="0" width="10" height="${H}" fill="${BORDA}"/>

	<g transform="translate(96, 120)">
		${marca(0, 60, 2.6, BORDA)}
	</g>

	${
		comTexto
			? `
	<g transform="translate(96, 320)" font-family="Georgia, 'Times New Roman', serif">
		<text x="0" y="0" font-size="82" font-weight="700" fill="${TINTA}" letter-spacing="-2">Estudos Antigos</text>
	</g>
	<g transform="translate(98, 386)" font-family="Arial, Helvetica, sans-serif">
		<text x="0" y="0" font-size="27" fill="${SUAVE}" letter-spacing="5">BÍBLICOS · CLÁSSICOS · MEDIEVAIS</text>
	</g>
	<g transform="translate(96, 508)" font-family="Georgia, 'Times New Roman', serif">
		<text x="0" y="0" font-size="33" fill="${BORDA}" font-style="italic">Cada afirmação com fonte rastreável.</text>
	</g>
	`
			: ''
	}

	<rect x="96" y="452" width="72" height="4" fill="${BORDA}"/>
</svg>`;

/** Rasteriza e devolve o buffer PNG. */
const render = (comTexto) =>
	sharp(Buffer.from(svg(comTexto)), { density: 72 })
		.png({ compressionLevel: 9 })
		.toBuffer();

const comTexto = await render(true);
const semTexto = await render(false);

const textoRenderizou = Buffer.compare(comTexto, semTexto) !== 0;

if (textoRenderizou) {
	writeFileSync('public/og-default.png', comTexto);
	console.log('✓ og-default.png gerado com tipografia (texto renderizou).');
} else {
	writeFileSync('public/og-default.png', semTexto);
	console.log(
		'⚠ librsvg não desenhou texto neste sistema — gerado layout sem tipografia.\n' +
			'  A imagem continua válida (marca + cor); o título vai nos metadados og:title.'
	);
}

const meta = await sharp('public/og-default.png').metadata();
console.log(`  dimensões: ${meta.width}x${meta.height}, ${meta.size ?? 0} bytes`);

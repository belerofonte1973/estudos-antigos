/**
 * Marca automaticamente trechos em hebraico e grego antigo.
 *
 * Por quê: o conteúdo traz hebraico e grego inline no meio de texto em
 * português. Sem isolamento bidi, a pontuação adjacente pode ser reposicionada
 * pelo algoritmo bidirecional, e leitores de tela não sabem que aquele trecho
 * está em outra língua. O CSS do projeto já define `.he` e `.grc` — mas nunca
 * eram aplicadas, porque o conteúdo escreve o texto puro, sem marcação.
 *
 * Este plugin fecha essa lacuna: envolve os trechos em
 * `<span class="he" dir="rtl" lang="he">` (e o equivalente grego), de modo que
 * quem escreve continue digitando texto simples.
 *
 * Só atua em nós de texto — nunca em código inline, blocos de código, URLs ou
 * atributos JSX, que não passam por nós `text`.
 */

// Hebraico (bloco U+0590–U+05FF) + marcas de controle bidi
const HEBRAICO = /[\u0590-\u05FF\u200E\u200F]+(?:\s+[\u0590-\u05FF\u200E\u200F]+)*/g;
// Grego antigo: bloco grego + extensões (politônico)
const GREGO = /[\u0370-\u03FF\u1F00-\u1FFF]+(?:\s+[\u0370-\u03FF\u1F00-\u1FFF]+)*/g;

/** Testa sem manter estado de regex global. */
const contem = (valor, re) => {
	re.lastIndex = 0;
	return re.test(valor);
};

/**
 * Substitui cada trecho encontrado por um nó `html` com o span apropriado.
 * Trabalha da direita para a esquerda para preservar os índices.
 */
const marcaTrechos = (valor, re, classe, lang, dir) => {
	const ocorrencias = [];
	re.lastIndex = 0;
	let m;
	while ((m = re.exec(valor)) !== null) ocorrencias.push([m.index, m.index + m[0].length, m[0]]);
	if (ocorrencias.length === 0) return null;

	const partes = [];
	let cursor = 0;
	for (const [ini, fim, trecho] of ocorrencias) {
		if (ini > cursor) partes.push({ type: 'text', value: valor.slice(cursor, ini) });
		const attrs = `class="${classe}"${dir ? ` dir="${dir}"` : ''} lang="${lang}"`;
		partes.push({ type: 'html', value: `<span ${attrs}>${trecho}</span>` });
		cursor = fim;
	}
	if (cursor < valor.length) partes.push({ type: 'text', value: valor.slice(cursor) });

	return partes;
};

export default function remarkLinguasAntigas() {
	return (tree) => {
		const pilha = [{ no: tree, indice: 0, pai: null }];

		// Travessia explícita: evita dependência de utilitário externo e
		// permite substituir vários nós irmãos com segurança.
		const processar = (no, pai, indice) => {
			if (!no || typeof no !== 'object') return;

			if (no.type === 'text' && pai && Array.isArray(pai.children)) {
				let partes = null;
				if (contem(no.value, HEBRAICO)) {
					partes = marcaTrechos(no.value, HEBRAICO, 'he', 'he', 'rtl');
				} else if (contem(no.value, GREGO)) {
					partes = marcaTrechos(no.value, GREGO, 'grc', 'grc', null);
				}
				if (partes) {
					pai.children.splice(indice, 1, ...partes);
					return;
				}
			}

			if (Array.isArray(no.children)) {
				// percorre de trás para frente: substituições não deslocam
				// os índices ainda não visitados
				for (let i = no.children.length - 1; i >= 0; i--) {
					processar(no.children[i], no, i);
				}
			}
		};

		processar(tree, null, 0);
		void pilha;
	};
}
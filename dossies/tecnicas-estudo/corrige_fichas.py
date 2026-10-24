#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""corrige_fichas.py — reconcilia as fichas das 5 figuras do MASTER com as
imagens que de fato foram baixadas.

Regra da casa: licença, autor, data e acervo saem da API do Commons na hora do
download; o que a API disser vence. Quatro das cinco fichas do MASTER citavam um
`File:` que não existe no Commons ou que é outra obra — o texto da legenda e o
`alt` precisam descrever a imagem real, não a imaginada.

    python dossies/tecnicas-estudo/corrige_fichas.py --seco
    python dossies/tecnicas-estudo/corrige_fichas.py
"""
from __future__ import annotations

import argparse
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
MASTER = AQUI / "00_tecnicas_estudo_master.md"

# (trecho antigo, trecho novo) — o trecho antigo e único no arquivo; o script
# asserta que casou exatamente uma vez antes de escrever.
TROCAS = [
    # Fig. 1 — a imagem e uma alegoria da arte da memória de 1699, nao Fludd 1619
    (
        "![A arte da memória — Ars Memoriæ, de Robert Fludd (1619). Gravura renascentista "
        "que ilustra o teatro da memória: um edifício com múltiplas câmaras e imagens "
        "simbólicas, representando a sistematização do conhecimento por meio de princípios "
        "mnemônicos.](imagens/01-ars-memoriae-fludd.jpg)",
        "![Alegoria da arte da memória: um edifício com múltiplas câmaras e imagens "
        "simbólicas, representando a sistematização do conhecimento por meio de princípios "
        "mnemônicos.](imagens/01-ars-memoriae-fludd.jpg)",
    ),
    (
        "**Fig. 1 — Ars Memoriæ, de Robert Fludd (1619).** Gravura do tratado "
        "*De praeternaturali utriusque mundi* de Robert Fludd, representação do teatro da "
        "memória renascentista. O edifício imaginário com fileiras de câmaras e imagens "
        "simbólicas materializa a tentativa de sistematizar o conhecimento usando associações "
        "mnemônicas — mesma lógica subjacente ao método dos loci descrito por Cícero. "
        "Cf. §§ 3 e 6. *Ficha: Robert Fludd. Licença: Public domain; fonte: "
        "[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Ars_Memori%C3%A6.jpg).*",
        "**Fig. 1 — Alegoria da arte da memória (1699).** Gravura de um livro impresso em 1699, "
        "representação do teatro da memória renascentista. O edifício imaginário com fileiras "
        "de câmaras e imagens simbólicas materializa a tentativa de sistematizar o "
        "conhecimento usando associações mnemônicas — mesma lógica subjacente ao método dos "
        "loci descrito por Cícero e levada ao extremo por Robert Fludd no "
        "*De praeternaturali utriusque mundi*. Cf. §§ 3 e 6. *Ficha: autoria anônima; obra "
        "impressa em 1699 (The Art of Memory, Internet Archive). Licença: Public domain; "
        "fonte: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Ars_Memori%C3%A6.jpg).*",
    ),
    # Fig. 2 — o File: citado nao existe; entrou a versao atualizada do mesmo diagrama
    (
        "![Cérebro humano com regiões da memória destacadas — ilustração esquemática do "
        "hipocampo, córtex pré-frontal e amígdala, envolvidos em diferentes tipos de memória.]"
        "(imagens/02-brain-memory-regions.jpg)",
        "![Regiões do cérebro destacadas numa ilustração esquemática das estruturas envolvidas "
        "na formação da memória.](imagens/02-brain-memory-regions.jpg)",
    ),
    (
        "**Fig. 2 — O cérebro e a memória.** Regiões cerebrais envolvidas na formação, "
        "consolidação e recuperação da memória de longo prazo. O hipocampo (em tons azuis) é "
        "essencial para a consolidação da memória declarativa; o córtex pré-frontal (em tons "
        "verdes) está envolvido na memória de trabalho e no controle executivo; a amígdala "
        "(em tons vermelhos) modula a consolidação emocional da memória. Cf. §§ 3, 4 e 7. "
        "*Ficha: Ilustração adaptada de pesquisa em neurociência cognitiva. Licença: "
        "CC BY-SA 4.0; fonte: [Wikimedia Commons](https://commons.wikimedia.org/wiki/"
        "File:Brain_regions_in_memory_formation.jpg).*",
        "**Fig. 2 — O cérebro e a memória.** Regiões cerebrais destacadas como centrais para a "
        "formação inicial da memória de longo prazo. O hipocampo é essencial à consolidação da "
        "memória declarativa, e o córtex pré-frontal participa da memória de trabalho e do "
        "controle executivo: é nesse circuito que a codificação do passo (2) se converte em "
        "traço duradouro. Cf. §§ 3, 4 e 7. *Ficha: Bernstein0275, 2021. Licença: CC BY-SA 4.0; "
        "fonte: [Wikimedia Commons](https://commons.wikimedia.org/wiki/"
        "File:Brain_regions_in_memory_formation_updated.jpg).*",
    ),
    # Fig. 3 — o File: citado nao existe; entrou a ilustracao verificada do metodo dos loci
    (
        "![Ilustração do método dos loci — um palácio da memória imaginário com cômodos "
        "numerados e imagens simbólicas em cada sala, representando a técnica mnemônica "
        "descrita por Cícero.](imagens/03-memory-palace-illustration.jpg)",
        "![Ilustração do método dos loci — um percurso por um palácio da memória com cômodos e "
        "imagens simbólicas servindo de âncoras para a informação.]"
        "(imagens/03-memory-palace-illustration.jpg)",
    ),
    (
        "**Fig. 3 — O palácio da memória.** Representação esquemática do método dos loci: um "
        "edifício imaginário (real ou fictício) cujos cômodos, corredores e objetos servem como "
        "\"âncoras\" para informações. Para recuperar a informação, o usuário percorre "
        "mentalmente o edifício, \"lendo\" as imagens em cada cômodo.",
        "**Fig. 3 — O palácio da memória.** Ilustração do método dos loci: um edifício "
        "imaginário (real ou fictício) cujos cômodos, corredores e objetos servem como "
        "\"âncoras\" para informações — aqui, os dígitos de π distribuídos ao longo de um "
        "percurso. Para recuperar a informação, o usuário percorre mentalmente o edifício, "
        "\"lendo\" as imagens em cada cômodo.",
    ),
    (
        "Cf. §§ 3 e 6. *Ficha: Ilustração conceitual baseada em tratados renascentistas. "
        "Licença: Public domain; fonte: [Wikimedia Commons](https://commons.wikimedia.org/wiki/"
        "File:De_praeternaturali_utriusque..._Fludd,_1621_Wellcome_L0016208.jpg).*",
        "Cf. §§ 3 e 6. *Ficha: Abratashov, 2023. Licença: CC BY-SA 4.0; fonte: "
        "[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Pi_Philology.png).*",
    ),
    # Fig. 4 — a ficha citava a MESMA imagem da Fig. 2; entrou a curva do esquecimento
    (
        "![Ilustração do ciclo do estudo e aprendizado: atenção → codificação → consolidação → "
        "recuperação, mostrando o papel do sono na consolidação.](imagens/04-learning-cycle.jpg)",
        "![A curva do esquecimento: o declínio da retenção ao longo do tempo e o efeito das "
        "revisões.](imagens/04-learning-cycle.jpg)",
    ),
    (
        "**Fig. 4 — O ciclo do aprendizado.** Do estímulo inicial à memória de longo prazo: "
        "(1) atenção seletiva filtra o estímulo; (2) codificação transforma a informação em "
        "representação mental; (3) consolidação, facilitada pelo sono, estabiliza o traço de "
        "memória; (4) recuperação ativa (testar-se) fortalece o traço e o torna resistente ao "
        "esquecimento. O ciclo se realimenta: cada recuperação bem-sucedida melhora a codificação "
        "subsequente. Cf. §§ 3, 4 e 7. *Ficha: Diagrama conceitual baseado no modelo de "
        "consolidação de Stickgold & Walker (2013). Licença: CC BY-SA 4.0; fonte: "
        "[Wikimedia Commons](https://commons.wikimedia.org/wiki/"
        "File:Brain_regions_in_memory_formation.jpg).*",
        "**Fig. 4 — A curva do esquecimento.** Ebbinghaus mediu em si mesmo a retenção de "
        "sílabas sem sentido e publicou em 1885 a curva que descreve o declínio da memória "
        "quando nenhum esforço de revisão é feito: queda abrupta nas primeiras horas e "
        "estabilização num patamar baixo. O diagrama contrasta esse declínio com o efeito das "
        "revisões, que elevam a curva a cada recuperação — o mesmo princípio dos passos (3) e "
        "(4) do ciclo do aprendizado: a consolidação, facilitada pelo sono, estabiliza o traço, "
        "e a recuperação ativa o fortalece contra o esquecimento. Cf. §§ 3, 4 e 7. *Ficha: "
        "Productive.Fish, 2023. Licença: CC0; fonte: [Wikimedia Commons](https://commons."
        "wikimedia.org/wiki/File:Forgetting_curve_and_work_of_Ebbinghaus.png).*",
    ),
    # Fig. 5 — o File: citado (Tizian 092) e o rapto de Lucrecia, nao o Sisifo
    (
        "Cf. § 10. *Ficha: Afresco de Ticiano, c. 1549. Licença: Public domain; fonte: "
        "[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Tizian_092.jpg).*",
        "Cf. § 10. *Ficha: Ticiano (Tiziano Vecellio), 1548–1549, óleo sobre tela, 237 × 216 cm, "
        "Museu do Prado, Madrid (P000426), série Las Furias. Licença: Public domain; fonte: "
        "[Wikimedia Commons](https://commons.wikimedia.org/wiki/"
        "File:Titian_-_Sisyphus_-_Madrid_-_Prado.jpg).*",
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    args = ap.parse_args()

    bruto = MASTER.read_bytes()
    crlf = bruto.count(b"\r\n")
    texto = bruto.decode("utf-8")
    e_crlf = crlf > 0
    if e_crlf:
        texto = texto.replace("\r\n", "\n")

    for antigo, novo in TROCAS:
        n = texto.count(antigo)
        assert n == 1, f"agulha casou {n} vezes (esperado 1): {antigo[:70]!r}"
        texto = texto.replace(antigo, novo, 1)

    print(f"MASTER: {len(TROCAS)} trechos trocados")
    if args.seco:
        print(f"  (--seco) quebra de linha preservada: "
              f"{'CRLF' if e_crlf else 'LF'} ({crlf} quebras); nada foi escrito")
        return
    saida = texto.replace("\n", "\r\n") if e_crlf else texto
    MASTER.write_bytes(saida.encode("utf-8"))
    print(f"  escrito: {MASTER}  ({'CRLF' if e_crlf else 'LF'})")


if __name__ == "__main__":
    main()

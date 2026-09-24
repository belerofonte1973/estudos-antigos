#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
montar_espec.py — monta `espec_figuras.json` (a especificação editorial) para o
dossiê 4-formatos da Suméria.

O único campo digitado à mão é o TRECHO que identifica a obra: o título exato
(`File:...`) é resolvido contra os JSON das buscas, que vieram da API — nunca
escrito de memória. Acervo/autor/data/licença continuam sendo reconferidos na
API pelo `baixar_figuras.py`.

`acervo: "-"` significa "deixe em branco" (o valor da API era boilerplate:
"Own work", "extracted from another file", link de Flickr).
"""
from __future__ import annotations

import json
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent

# (trecho único do título, seção, título PT, alt, legenda, técnica, acervo)
ESCOLHA = [
    ("Sumer satellite map", "1",
     "A planície aluvial vista do espaço",
     "Imagem de satélite do sul do Iraque, com o Tigre e o Eufrates, a planície "
     "aluvial entre os dois rios e a foz no Golfo Pérsico",
     "Imagem de satélite do sul da Mesopotâmia: entre o Tigre (a leste) e o "
     "Eufrates, a planície aluvial onde os sumérios construíram suas cidades, "
     "hoje o sul do Iraque, com a foz dos dois rios no Golfo Pérsico. É o "
     "território de que trata o § 3 — solo fértil de sedimentos, mas de chuvas "
     "insuficientes para a agricultura sem irrigação. Cf. § 3.",
     "", "NASA (imagem de satélite); sobreposição de पाटलिपुत्र"),
    ("Ziggurat of Ur Site in Nasiriyah 02", "1",
     "O zigurate de Ur, hoje",
     "Vista do conjunto do zigurate de Ur, em Nasiriyah, com a escadaria "
     "monumental e o pátio de tijolos",
     "O grande zigurate de Ur (Tell el-Muqayyar, sul do Iraque), a estrutura "
     "melhor preservada do tipo: as três escadarias convergiam para o templo no "
     "alto, dedicado a Nanna, deus da lua. O monumento é obra do Renascimento "
     "Sumério e está associado a Ur-Nammu e a Shulgi. Cf. §§ 3, 6 e 11.",
     "", "-"),
    ("Sumer Akkad.png", "2",
     "Mapa de Sumer e Acádia",
     "Mapa histórico com as cidades da Suméria e da Acádia, os rios Tigre e "
     "Eufrates e a linha de costa histórica do Golfo Pérsico",
     "Mapa das cidades sumérias e acádias, com os rios, a costa histórica do "
     "Golfo — hoje bem mais ao sul do que no terceiro milênio a.C. — e os "
     "assentamentos principais (Eridu, Uruk, Ur, Nippur, Lagash, Kish). "
     "Desenhado sobre dados Natural Earth e GSHHG. Cf. §§ 3 e 4.",
     "", "Mapa de Cattette, sobre dados Natural Earth e GSHHG"),
    ("Sumerian King List, 1800 BC, Larsa, Iraq.jpg", "3",
     "A Lista Real Suméria",
     "Tábua de argila coberta de escrita cuneiforme em colunas estreitas",
     "A Lista Real Suméria (tábua de Larsa, c. 1800 a.C.): a lista encadeia "
     "reis de Eridu a Isin, com reinados de duração fantástica antes do "
     "dilúvio. É a fonte que organiza a cronologia suméria e, ao mesmo tempo, o "
     "melhor exemplo de como a escrita servia à ideologia real — a lista é uma "
     "construção política, não um registro administrativo. Cf. § 3.",
     "argila", "-"),
    ("Ancient Uruk, Iraq (ASTER)", "3",
     "Uruk vista do espaço",
     "Imagem de satélite em falsa cor do sítio arqueológico de Uruk, no sul do "
     "Iraque",
     "Uruk em imagem do sensor ASTER (NASA/METI), num canal abandonado do "
     "Eufrates: no auge, por volta de 2900 a.C., a cidade teria tido mais de "
     "50 mil habitantes — a maior do mundo à época, segundo a descrição da "
     "própria NASA. Uruk dá nome ao período em que a escrita aparece. Cf. §§ 3, 4 e 5.",
     "", "NASA/METI/AIST/Japan Space Systems — sensor ASTER"),
    ("Diorite Victory Stele of Sargon", "3",
     "Estela de vitória de Sargão de Acad",
     "Fragmento de estela de pedra escura com relevo de figuras e inscrição "
     "cuneiforme",
     "Estela de vitória em diorito de Sargão de Acad (c. 2300 a.C.), no Louvre: "
     "fragmento do monumento que celebrava a conquista de cidades sumérias e a "
     "unificação de Sumer e Acad sob administração única — o modelo de todos os "
     "impérios posteriores da região. Cf. §§ 3 e 8.",
     "diorito", "Musée du Louvre, Paris; foto de Gary Todd"),
    ("Stele of Ur-Nammu (front and back)", "3",
     "Estela de Ur-Nammu",
     "Duas vistas de uma estela de pedra com relevos em registros e inscrição "
     "cuneiforme",
     "Estela de Ur-Nammu, fundador da III Dinastia de Ur (c. 2112-2094 a.C.), "
     "vista de frente e de verso: o relevo em registros mostra o rei em tarefas "
     "rituais e de construção, e a inscrição enumera os trabalhos do reinado. "
     "Cf. §§ 3, 8 e 11.",
     "pedra calcária", "-"),
    ("Ziggurat at Eridu (30809118442)", "4",
     "Os tijolos do zigurate de Eridu",
     "Parede de tijolos cozidos de um zigurate em ruínas, com tijolos "
     "estampados",
     "Tijolos cozidos do zigurate de Eridu, a sudoeste de Nasiriyah: muitos "
     "levam estampado o nome do rei Ur-Nammu (2123-2106 a.C.), o que data a "
     "fase final do santuário. Eridu é o assentamento urbano mais antigo "
     "conhecido da região, com ocupação desde o período Ubaid. Cf. §§ 3, 4 e 6.",
     "", "Sítio de Eridu (Tell Abu Shahrain), Iraque; foto de David Stanley"),
    ("plan of Nippur (Hilprecht", "4",
     "A planta de Nippur",
     "Tábua de argila com desenho de planta urbana, com linhas de ruas, canais "
     "e recintos",
     "Tábua de argila com a planta da cidade de Nippur, publicada por Hermann "
     "V. Hilprecht em 1903 a partir de um original de cerca de 1400 a.C.: ruas, "
     "canais, portas e o recinto do templo de Enlil. O documento mostra a cidade "
     "suméria como objeto de desenho técnico, não apenas de descrição literária. "
     "Cf. § 4.",
     "argila", "Explorations in Bible Lands during the 19th Century (1903)"),
    ("Stele of the Vultures in the Louvre Museum", "4",
     "A Estela dos Abutres",
     "Estela de pedra com relevos em registros: soldados em formação, carros de "
     "combate e aves carregando restos",
     "A Estela dos Abutres, de Lagash (c. 2450 a.C.), no Louvre: um lado narra "
     "a vitória de Eannatum sobre Umma e o outro, a intervenção divina — os "
     "abutres que dão nome à peça carregam restos dos inimigos. É o mais antigo "
     "monumento histórico-narrativo conhecido da Mesopotâmia e documento do "
     "conflito entre cidades-estado pela terra e pela água. Cf. §§ 4, 8 e 11.",
     "calcário", "Musée du Louvre, Paris; imagem composta de duas fotografias"),
    ("proto-cuneiform signs, food issue list", "5",
     "Proto-cuneiforme: lista de rações",
     "Tábua de argila com sinais proto-cuneiformes incisos em colunas",
     "Tábua proto-cuneiforme do fim do período Uruk (3300-3100 a.C.): a lista "
     "de rações combina o sinal da cabeça humana com o da tigela, e o triângulo "
     "é o símbolo regular do pão — em sumério posterior, o verbo \"comer\". A "
     "escrita nasce como contabilidade, não como literatura. Cf. § 5.",
     "argila", "British Museum, Londres; foto de Osama Shukir Muhammed Amin"),
    ("administrative account concerning the distribution of barley and emmer MET", "5",
     "Registro da distribuição de cevada e trigo",
     "Tábua de argila de contorno arredondado com sinais cuneiformes "
     "incisos",
     "Tábua administrativa suméria que registra a distribuição de cevada e de "
     "trigo-emmer (c. 3100 a.C.), do acervo aberto do Metropolitan Museum. É o "
     "tipo de documento que constitui a massa dos primeiros arquivos escritos: "
     "quantidades, pessoas e dias de trabalho. Cf. §§ 5 e 7.",
     "argila", "The Metropolitan Museum of Art, Nova York (Open Access)"),
    ("58 different terms for pig", "5",
     "Lista lexical: 58 termos para \"porco\"",
     "Tábua de argila com lista de sinais cuneiformes em colunas regulares",
     "Tábua lexical de Uruk (c. 3200 a.C.), no Museu Pergamon: uma lista de 58 "
     "termos diferentes para \"porco\". As listas de palavras são o gênero mais "
     "antigo da literatura mesopotâmica e a base do ensino nas escolas de "
     "escribas — a escrita já não serve apenas para contar, mas para ordenar o "
     "mundo. Cf. § 5.",
     "argila queimada", "Museu Pergamon, Berlim; foto de Osama Shukir Muhammed Amin"),
    ("School tablet - Sumerian cuneiform - Susa - 2nd mil BC - National Museum of Iran - Inventory number - 1885.jpg",
     "5",
     "Tábua escolar de Susa",
     "Tábua de argila com sinais cuneiformes repetidos em colunas, exercício de "
     "aprendiz de escriba",
     "Tábua escolar de escrita suméria, copiada em Susa no segundo milênio a.C. "
     "(Museu Nacional do Irã): é o exercício de um aprendiz de escriba, com "
     "sinais repetidos em colunas. Prova material de que a formação nas "
     "*edubba* se estendia muito além do núcleo sumério. Cf. § 5.",
     "argila", "Museu Nacional do Irã, Teerã (nº 1885); foto de Darafsh"),
    ("Warka Vase, Iraq Museum", "6",
     "O Vaso de Warka",
     "Vaso alto de pedra clara com relevos em faixas: uma procissão de figuras "
     "levando oferendas",
     "O Vaso de Warka (Uruk, período Jemdet Nasr, 3000-2900 a.C.), no Museu do "
     "Iraque (IM 19606): em três registros, uma procissão leva oferendas à "
     "deusa Inanna diante do templo. É a obra que fixa a iconografia da relação "
     "entre a cidade, o templo e a divindade. Cf. §§ 6 e 11.",
     "", "Museu do Iraque, Bagdá (IM 19606); foto de Osama Shukir Muhammed Amin"),
    ("Warka Mask, Iraq Museum", "6",
     "A Máscara de Warka",
     "Rosto feminino esculpido em pedra clara, sem os olhos incrustados",
     "A Máscara de Warka (Uruk, 3000-2900 a.C.), Museu do Iraque (IM 45434): "
     "rosto feminino em pedra, provavelmente da deusa Inanna, o mais antigo "
     "rosto humano em escultura monumental do sul da Mesopotâmia. Cf. §§ 6 e 11.",
     "", "Museu do Iraque, Bagdá (IM 45434); foto de Osama Shukir Muhammed Amin"),
    ("Square Temple of Abu, Shrine II, Early Dynastic period, 2700-2600 BC, gypsum, shell, bitumen",
     "6",
     "Estátua votiva de Tell Asmar",
     "Estátua de adorador barbado, de olhos grandes incrustados, com as mãos "
     "cruzadas sobre o peito",
     "Estátua votiva de adorador barbado, do Templo Quadrado de Abu em Tell "
     "Asmar (Dinástico Antigo, 2700-2600 a.C.), no Oriental Institute de "
     "Chicago. As estátuas votivas eram depositadas nos templos para que o "
     "devoto \"orasse\" permanentemente diante do deus — e a maior parte foi "
     "enterrada ritualmente quando o santuário foi reformado. Cf. § 6.",
     "gesso, concha, betume e calcário negro",
     "Oriental Institute Museum, Universidade de Chicago"),
    ("Bronze foundation figurine of Ur-Nammu from the Temple of Inanna at Uruk",
     "6",
     "Figura de fundação de Ur-Nammu",
     "Pequena figura humana de bronze, ajoelhada e com uma cesta à cabeça",
     "Figura de fundação em bronze de Ur-Nammu, do templo de Inanna em Uruk "
     "(British Museum): o rei aparece carregando a cesta do construtor, gesto "
     "que faz do monarca o primeiro operário do templo. Peças como esta eram "
     "depositadas nos alicerces e davam ao edifício um valor ao mesmo tempo "
     "religioso e jurídico. Cf. §§ 6 e 11.",
     "bronze", "British Museum, Londres; foto de Gary Todd"),
    ("Man carrying a box, possibly for offerings", "7",
     "Homem carregando uma caixa de oferendas",
     "Figurinha de metal de um homem em pé, com uma caixa apoiada nos ombros, "
     "vista de lado",
     "Figura suméria de um homem carregando aos ombros uma caixa, talvez de "
     "oferendas (c. 2900-2600 a.C.), no Metropolitan Museum. Objetos como este "
     "documentam o trabalho e as oferendas que sustentavam a economia do "
     "templo, fora da iconografia oficial do rei. Cf. § 7.",
     "", "The Metropolitan Museum of Art, Nova York (Open Access)"),
    ("Inlaid Gold Ring from Archaic Period of Sumer", "7",
     "Anel de ouro com incrustações",
     "Anel largo de ouro com incrustações coloridas formando desenho geométrico",
     "Anel de ouro com incrustações, do período arcaico sumério (2900-2340 "
     "a.C.), no Louvre: peça de adorno pessoal que mostra o domínio da "
     "ourivesaria e o acesso a metais importados — o ouro do sul da Mesopotâmia "
     "vinha de fora, por redes de longa distância. Cf. §§ 7 e 13.",
     "ouro com incrustações", "Musée du Louvre, Paris; foto de Gary Todd"),
    ("Gameboard recovered from the royal cemetery of Ur", "7",
     "Tabuleiro do Cemitério Real de Ur",
     "Tabuleiro quadrado com casas e peças de concha e pedra azul, em vitrine",
     "Tabuleiro de jogo recuperado do Cemitério Real de Ur (2550-2450 a.C.), no "
     "Penn Museum: o chamado Jogo Real de Ur, com casas e peças de concha e "
     "lápis-lazúli. É prova material do lazer nas elites urbanas, e o tabuleiro "
     "reaparece em relevos e em listas de bens. Cf. § 7.",
     "", "Penn Museum, Filadélfia; foto de Mary Harrsch"),
    ("Head of a Sumerian woman, from Khafajah", "7",
     "Cabeça de mulher suméria",
     "Cabeça esculpida de mulher, com penteado em faixas e olhos vazados",
     "Cabeça de mulher suméria em alabastro e calcário, de Khafajah, escavada "
     "pelo Oriental Institute na quarta campanha (1933-1934), Dinástico Antigo "
     "III, c. 2400 a.C. A cabeça não pertence ao corpo da estátua — a maior "
     "parte das estátuas votivas foi desmontada na Antiguidade. Cf. §§ 4 e 7.",
     "alabastro e calcário", "Museu de Sulaymaniyah, Iraque; foto de Osama Shukir Muhammed Amin"),
    ("Cylinder seal MET 159183", "7",
     "Selo cilíndrico sumério",
     "Pequeno cilindro de pedra gravado, com a impressão que ele deixa na argila",
     "Selo cilíndrico sumério (c. 2500 a.C.), do acervo aberto do Metropolitan "
     "Museum: rolado sobre a argila, o cilindro repetia a mesma cena quantas "
     "vezes fosse preciso, servindo de assinatura e de garantia de propriedade. "
     "A prática atravessou três milênios e passou a acádios, babilônios e "
     "assírios. Cf. §§ 5 e 7.",
     "pedra gravada", "The Metropolitan Museum of Art, Nova York (Open Access)"),
    ("Gudea, City Ruler of Lagash, Sumer - Ny Carlsberg Glyptotek", "8",
     "Gudea de Lagash",
     "Estátua de homem sentado, de cabeça raspada, manto com inscrição "
     "cuneiforme e mãos cruzadas",
     "Estátua de Gudea, *ensi* de Lagash (c. 2144-2124 a.C.), na Ny Carlsberg "
     "Glyptotek, Copenhague: a série de estátuas em pedra escura — outras estão "
     "no Louvre — é a principal fonte figurativa sobre o governante sumério e "
     "sobre sua função votiva. Cf. §§ 3 e 8.",
     "", "Ny Carlsberg Glyptotek, Copenhague; foto de Jakub Hałun"),
    ("Disk of Enheduanna.JPG", "8",
     "O Disco de Enheduana",
     "Disco de pedra clara com relevo de figuras em cortejo diante de um "
     "santurário",
     "O Disco de Enheduana (c. 2350-2300 a.C.), em calcário, no Penn Museum "
     "(B16665, U.6612): a sacerdotisa aparece no relevo, precedida por um "
     "cortejo, num monumento encontrado no templo de Nin-Gal em Ur. Enheduana, "
     "filha de Sargão de Acad, é a primeira autora identificada por nome na "
     "história. Cf. § 8.",
     "calcário/calcite", "Penn Museum, Filadélfia (B16665, U.6612)"),
    ("CBS7847 Ninmeshara Penn Museum", "8",
     "Cópia do hino de Enheduana",
     "Tábua de argila com hino cuneiforme em colunas, restaurada",
     "Tábua com cópia do hino *Exaltação de Inanna* (Ninmešarra), de Enheduana, "
     "encontrada em Nippur (período paleobabilônico, 1900-1600 a.C.), no Penn "
     "Museum (CBS 7847): o texto de autoria mais antiga conhecida sobrevive em "
     "cópias escolares posteriores. Cf. §§ 5, 8 e 16.",
     "argila", "Penn Museum, Filadélfia (CBS 7847)"),
    ("Birth Sargon of Akkad Louvre AO7673", "8",
     "O nascimento de Sargão",
     "Tábua de argila com texto cuneiforme denso em ambas as faces",
     "Tábua de argila com o relato do nascimento de Sargão e de sua disputa com "
     "o rei Ur-Zababa de Kish, em cópia paleobabilônica (Louvre AO 7673). O "
     "texto compõe a lenda do primeiro imperador — o menino exposto no rio — "
     "que a literatura comparada aproxima do relato de Moisés. Cf. §§ 8 e 9.",
     "argila", "Musée du Louvre, Paris (AO 7673); foto de Marie-Lan Nguyen"),
    ("Relief Ur-Nanshe Louvre AO2344", "8",
     "Ur-Nanshe de Lagash",
     "Relevo de pedra com o governante carregando uma cesta à cabeça, cercado "
     "de figuras menores",
     "Relevo de Ur-Nanshe (Louvre AO 2344), fundador da I Dinastia de Lagash "
     "(c. 2500 a.C.): o governante aparece carregando a cesta de argamassa para "
     "a construção do templo, no alto de um painel com seus filhos e oficiais. "
     "A cena fixa o modelo do rei-construtor que reaparece em Gudea e em "
     "Ur-Nammu. Cf. §§ 4 e 8.",
     "calcário", "Musée du Louvre, Paris (AO 2344); foto de Marie-Lan Nguyen"),
    ("Tablet XI or the Flood Tablet of the Epic of Gilgamesh", "9",
     "A tabuleta do dilúvio (Gilgamesh XI)",
     "Tábua de argila coberta de escrita cuneiforme, em vitrine de museu",
     "A tabuleta XI da epopeia de Gilgamesh, escavada por Hormuzd Rassam na "
     "biblioteca de Assurbanipal em Nínive (século VII a.C.), no British "
     "Museum: é a cópia que George Smith leu em 1872, com o relato do dilúvio "
     "contado por Utnapishtim. A peça transformou a comparação entre Gênesis e "
     "a Mesopotâmia de especulação em filologia. Cf. §§ 9 e 16.",
     "argila", "British Museum, Londres; foto de Osama Shukir Muhammed Amin"),
    ("Epic of Gilgamesh, from Hattusa, Turkey. 13th century BCE. Neues Museum", "9",
     "Gilgamesh em Hattusa",
     "Pequena tábua de argila com escrita cuneiforme, restaurada, em vitrine",
     "Fragmento da epopeia de Gilgamesh encontrado em Hattusa, capital hitita "
     "(século XIII a.C.), hoje no Neues Museum de Berlim (VAT 12890): o texto "
     "mesopotâmico circulava em cópias fora do mundo sumério-acádio, o que mede "
     "o alcance do épico. Cf. §§ 9 e 13.",
     "argila", "Neues Museum, Berlim (VAT 12890); foto de Osama Shukir Muhammed Amin"),
    ("Bull Headed Lyre of Ur", "10",
     "A lira de cabeça de touro de Ur",
     "Lira reconstituída, com a cabeça de touro em ouro e barba de pedra azul "
     "no alto da caixa de ressonância",
     "A lira de cabeça de touro do Cemitério Real de Ur, no Penn Museum: a "
     "cabeça do touro em folha de ouro, com barba de lápis-lazúli, é o "
     "instrumento mais conhecido da música suméria e uma das peças que sustenta "
     "as reconstruções das afinações da época. Cf. § 10.",
     "", "Penn Museum, Filadélfia; foto de Binxedits"),
    ("Queen's Lyre Ur Royal Cemetery", "10",
     "A lira da rainha",
     "Lira com a caixa de ressonância decorada por painéis de conchas e pedra "
     "escura com cenas de animais",
     "A lira da rainha, do túmulo de Puabi no Cemitério Real de Ur (c. 2550-2450 "
     "a.C.): a caixa de ressonância traz painéis de conchas e betume com cenas "
     "de animais, e o instrumento integra o conjunto que a arqueologia associou "
     "à música ritual de Ur. Cf. §§ 7 e 10.",
     "", "-"),
    ("Silver lyre, PG 1237", "10",
     "A lira de prata de Ur",
     "Lira com a caixa de ressonância revestida de prata e cabeça de touro "
     "modelada",
     "A lira de prata do túmulo PG 1237 — o \"Poço da Morte\" do Cemitério Real "
     "de Ur (c. 2550-2450 a.C.): os instrumentos foram encontrados junto aos "
     "corpos de quem os tocava, nos enterros de acompanhamento. Cf. §§ 7 e 10.",
     "prata", "-"),
    ("Ram in a thicket - British", "10",
     "O carneiro no arbusto",
     "Escultura de um carneiro empinado num arbusto, com corpo revestido de "
     "folhas de ouro e concha",
     "O carneiro no arbusto (Ur, túmulo PG 1237, c. 2500 a.C.), no British "
     "Museum: um dos dois exemplares — o par está no Penn Museum —, com núcleo "
     "de madeira e incrustações fixadas por betume. É objeto de adorno e de "
     "prestígio, e mostra a base material do artesanato de Ur. Cf. §§ 7 e 10.",
     "madeira, ouro e concha, fixados com betume",
     "British Museum, Londres; foto de Szilas"),
    ("Standard of Ur - Peace.jpg", "11",
     "O Estandarte de Ur: face da paz",
     "Painel de mosaico em três faixas: banquete, procissão de animais e "
     "transporte de bens diante de um rei entronizado",
     "O Estandarte de Ur, face da paz (c. 2600 a.C., British Museum): em três "
     "registros aparecem o banquete, a procissão de animais e o transporte de "
     "bens diante do rei entronizado. É a imagem mais difundida da hierarquia "
     "suméria — rei, sacerdotes, músicos, servidores. Cf. §§ 7 e 11.",
     "", "British Museum, Londres; foto de LeastCommonAncestor"),
    ("Standard of Ur - War.jpg", "11",
     "O Estandarte de Ur: face da guerra",
     "Painel de mosaico em três faixas: carros de combate puxados por animais, "
     "infantaria e prisioneiros",
     "O Estandarte de Ur, face da guerra (c. 2600 a.C., British Museum): carros "
     "de combate de quatro rodas puxados por equídeos, infantaria com capas, "
     "inimigos mortos e prisioneiros conduzidos à presença do rei. O par de "
     "faces — guerra e paz — é a razão de o objeto ser lido como programa "
     "político, e não só como caixa de ressonância ou estandarte. Cf. §§ 7 e 11.",
     "", "British Museum, Londres"),
    ("Relief Ninsun Louvre AO2761", "11",
     "Relevo de Ninsun",
     "Fragmento de relevo com figura feminina de vestido escalonado, em perfil",
     "Relevo de Ninsun (Louvre AO 2761), de meados do terceiro milênio a.C.: a "
     "deusa é apresentada em baixo-relevo com o vestido de lã regular, tipo de "
     "peça que demonstra a padronização da escultura religiosa suméria. "
     "Cf. § 11.",
     "calcário", "Musée du Louvre, Paris (AO 2761); foto de Jastrow"),
]


def main() -> None:
    banco: list[dict] = []
    for nome in ("_bruto_candidatos.json", "_bruto_candidatos2.json"):
        p = AQUI / nome
        if p.exists():
            for itens in json.loads(p.read_text(encoding="utf-8")).values():
                banco += itens

    figuras, problemas = [], []
    for trecho, secao, titulo, alt, legenda, tecnica, acervo in ESCOLHA:
        cands = [c for c in banco if trecho.lower() in c["arquivo"].lower()]
        if not cands:
            problemas.append((trecho, "não achei nos JSON de busca"))
            continue
        c = sorted(cands, key=lambda x: (x["grupo"] != "LIVRE", -x["largura"]))[0]
        if c["grupo"] == "NAO-USAR":
            problemas.append((trecho, f"licença {c['licenca']}"))
            continue
        figuras.append({"arquivo": c["arquivo"], "titulo": titulo, "alt": alt,
                        "legenda": legenda, "tecnica": tecnica, "acervo": acervo,
                        "secao": secao, "posicao": "fim"})

    espec = {
        "slug": "sumeria-4f",
        "titulo_dossie": "A Civilização Suméria: O Berço da Civilização",
        "figuras": figuras,
    }
    (AQUI / "espec_figuras.json").write_text(
        json.dumps(espec, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(figuras)} figuras na especificação")
    por_secao: dict[str, int] = {}
    for f in figuras:
        por_secao[f["secao"]] = por_secao.get(f["secao"], 0) + 1
    print("por seção: " + ", ".join(f"{k}:{v}" for k, v in sorted(
        por_secao.items(), key=lambda x: int(x[0]))))
    if problemas:
        print("PROBLEMAS:", problemas)


if __name__ == "__main__":
    main()

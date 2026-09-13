from urllib.parse import quote

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Comercio, Praia


def _link_busca_booking(nome_estabelecimento: str, cidade: str) -> str:
    """Monta um link de busca no Booking.com para o estabelecimento.

    O ID de afiliado (BOOKING_AFFILIATE_ID) e adicionado dinamicamente na
    hora de exibir o link (ver app/services/affiliate.py), entao o mesmo
    link ja funciona hoje e passa a gerar comissao assim que o ID real for
    configurado, sem precisar rodar o seed novamente.
    """
    termo_busca = quote(f"{nome_estabelecimento}, {cidade}")
    return f"https://www.booking.com/searchresults.html?ss={termo_busca}"


PRAIAS = [
    {
        "nome": "Juquehy",
        "cidade": "São Sebastião",
        "latitude": -23.7653,
        "longitude": -45.7347,
        "nivel_infraestrutura": 5,
        "descricao": (
            "Praia extensa e arborizada, dividida por um costão em dois trechos com "
            "climas bem diferentes: o lado esquerdo é mais família, o direito mais jovem. "
            "Excelente estrutura de pousadas, restaurantes e quiosques."
        ),
        "caracteristicas_mar": (
            "Mar calmo a moderado no trecho central e à esquerda, protegido, bom para "
            "banho de família e crianças. À direita, perto da ponta, as ondas aumentam "
            "e atraem surfistas iniciantes."
        ),
        "faixa_areia": "Areia clara e larga, cerca de 2,5 km de extensão, com boa sombra de coqueiros.",
        "dicas_seguranca": (
            "Evite se afastar muito da faixa de areia perto dos costões nas pontas, onde "
            "podem se formar correntes de retorno. Fique atento à sinalização da guarda-vidas, "
            "presente nos meses de alta temporada."
        ),
    },
    {
        "nome": "Maresias",
        "cidade": "São Sebastião",
        "latitude": -23.7918,
        "longitude": -45.5608,
        "nivel_infraestrutura": 5,
        "descricao": (
            "Uma das praias mais famosas do Brasil para o surf, com forte agito noturno, "
            "bares, baladas e público jovem. Estrutura completa de pousadas e restaurantes."
        ),
        "caracteristicas_mar": (
            "Mar aberto com ondas fortes e constantes, ótimo para surf e bodyboard, mas "
            "não recomendado para banho tranquilo com crianças pequenas, especialmente "
            "no trecho central mais exposto."
        ),
        "faixa_areia": "Areia grossa e dourada, faixa larga com cerca de 3 km de extensão.",
        "dicas_seguranca": (
            "Correntes de retorno (valas) são comuns, principalmente com mar agitado. "
            "Prefira nadar próximo aos postos de guarda-vidas e evite entrar no mar após "
            "consumo de álcool, algo frequente por conta da vida noturna do local."
        ),
    },
    {
        "nome": "Camburi",
        "cidade": "São Sebastião",
        "latitude": -23.7999,
        "longitude": -45.6197,
        "nivel_infraestrutura": 4,
        "descricao": (
            "Praia charmosa e menos comercial, cercada por Mata Atlântica preservada, "
            "com um vilarejo tranquilo de pousadas boutique e restaurantes descolados."
        ),
        "caracteristicas_mar": (
            "Mar com ondas moderadas, bom para surf de nível intermediário e para banho "
            "com atenção, principalmente na maré cheia."
        ),
        "faixa_areia": "Areia escura e fofa, faixa estreita a moderada emoldurada pela mata.",
        "dicas_seguranca": (
            "Atenção às pedras nas extremidades da praia e à formação de correntes em dias "
            "de ressaca. Poucos comércios significam menor movimento de banhistas para pedir ajuda."
        ),
    },
    {
        "nome": "Barra do Una",
        "cidade": "São Sebastião",
        "latitude": -23.8194,
        "longitude": -45.4808,
        "nivel_infraestrutura": 2,
        "descricao": (
            "Vila de pescadores rústica e tranquila, na divisa com Ubatuba, cercada por "
            "natureza preservada e com poucos comércios."
        ),
        "caracteristicas_mar": (
            "Mar calmo próximo à foz do rio, formando uma espécie de piscina natural "
            "segura para crianças; mais aberto e ondulado nas extremidades."
        ),
        "faixa_areia": "Areia clara, faixa estreita, com encontro do rio com o mar.",
        "dicas_seguranca": (
            "Cuidado ao nadar próximo à barra do rio devido à correnteza da água doce "
            "encontrando o mar. Estrutura de socorro limitada, avalie as condições antes de entrar."
        ),
    },
    {
        "nome": "Baleia",
        "cidade": "São Sebastião",
        "latitude": -23.8464,
        "longitude": -45.4211,
        "nivel_infraestrutura": 2,
        "descricao": (
            "Praia deserta e preservada, cercada por costões e vegetação nativa, "
            "procurada por quem busca sossego e paisagens intocadas."
        ),
        "caracteristicas_mar": "Mar de ondas moderadas a fortes, indicado para surfistas mais experientes.",
        "faixa_areia": "Areia clara e fina, faixa estreita entre costões rochosos.",
        "dicas_seguranca": (
            "Praia sem posto de guarda-vidas fixo; correntes de retorno são frequentes "
            "perto das pedras. Recomendado apenas para nadadores experientes e com cautela."
        ),
    },
    {
        "nome": "Guaecá",
        "cidade": "São Sebastião",
        "latitude": -23.7893,
        "longitude": -45.4227,
        "nivel_infraestrutura": 4,
        "descricao": (
            "Praia residencial e familiar, próxima ao centro de São Sebastião, com boa "
            "infraestrutura de quiosques e fácil acesso."
        ),
        "caracteristicas_mar": "Mar geralmente calmo e protegido, ideal para famílias e crianças.",
        "faixa_areia": "Areia clara, faixa larga e de fácil acesso.",
        "dicas_seguranca": (
            "Uma das praias mais seguras da região para banho, mas ainda assim vale "
            "observar bandeiras de sinalização em dias de ressaca."
        ),
    },
    {
        "nome": "Toque-Toque Grande",
        "cidade": "São Sebastião",
        "latitude": -23.8391,
        "longitude": -45.4079,
        "nivel_infraestrutura": 2,
        "descricao": (
            "Enseada pequena e charmosa cercada por costões, com águas geralmente "
            "verdes e cristalinas, ótima para quem busca tranquilidade."
        ),
        "caracteristicas_mar": "Mar calmo e protegido pela enseada fechada, boa visibilidade para snorkel.",
        "faixa_areia": "Areia clara, faixa curta em formato de meia-lua.",
        "dicas_seguranca": (
            "Acesso por escadaria e estrada estreita e sinuosa; poucos serviços de apoio, "
            "leve água e protetor solar. Atenção a pedras submersas próximas aos costões."
        ),
    },
    {
        "nome": "Prainha (Ilhabela)",
        "cidade": "Ilhabela",
        "latitude": -23.8272,
        "longitude": -45.3583,
        "nivel_infraestrutura": 3,
        "descricao": (
            "Point tradicional de surf em Ilhabela, com bares e pousadas simples na "
            "orla e clima descontraído."
        ),
        "caracteristicas_mar": "Mar com ondas constantes e boas para surf, correnteza lateral perceptível.",
        "faixa_areia": "Areia escura, faixa moderada.",
        "dicas_seguranca": (
            "Preste atenção a correntes laterais formadas pela quebra das ondas, "
            "mais indicada para quem já tem experiência no mar."
        ),
    },
    {
        "nome": "Praia do Bonete",
        "cidade": "Ilhabela",
        "latitude": -23.8969,
        "longitude": -45.3167,
        "nivel_infraestrutura": 2,
        "descricao": (
            "Vila caiçara isolada, acessível apenas por trilha ou barco, com paisagem "
            "preservada e poucos moradores. Um dos destinos mais desejados de Ilhabela."
        ),
        "caracteristicas_mar": "Mar com ondas boas para surf e águas limpas, variando com o vento.",
        "faixa_areia": "Areia clara e extensa, cercada por coqueiros e Mata Atlântica.",
        "dicas_seguranca": (
            "Estrutura de saúde e resgate praticamente inexistente por ser isolada; "
            "planeje a trilha (cerca de 4 a 5 horas) ou o barco com antecedência e leve "
            "suprimentos suficientes."
        ),
    },
    {
        "nome": "Praia do Pereque",
        "cidade": "Ilhabela",
        "latitude": -23.7936,
        "longitude": -45.3572,
        "nivel_infraestrutura": 4,
        "descricao": (
            "Praia urbana próxima ao terminal de balsas, com boa infraestrutura de "
            "restaurantes, pousadas e fácil acesso para quem chega à ilha."
        ),
        "caracteristicas_mar": "Mar calmo, protegido pelo Canal de São Sebastião, sem ondas fortes.",
        "faixa_areia": "Areia escura, faixa estreita a moderada.",
        "dicas_seguranca": (
            "Águas calmas e seguras para banho, mas fique atento ao tráfego de embarcações "
            "próximo ao canal e ao terminal."
        ),
    },
    {
        "nome": "Praia Martim de Sá",
        "cidade": "Caraguatatuba",
        "latitude": -23.6392,
        "longitude": -45.4028,
        "nivel_infraestrutura": 4,
        "descricao": (
            "Orla urbana extensa de Caraguatatuba, com calçadão, ciclovia e boa "
            "estrutura de comércio ao longo de toda a praia."
        ),
        "caracteristicas_mar": "Mar aberto, ondas moderadas, variando de calmo a agitado conforme o trecho.",
        "faixa_areia": "Areia clara, faixa larga com mais de 6 km de extensão.",
        "dicas_seguranca": (
            "Por ser extensa e com mar aberto, procure sempre os trechos com posto de "
            "guarda-vidas sinalizado e evite as áreas próximas à foz de rios após chuvas fortes."
        ),
    },
    {
        "nome": "Prainha (Caraguatatuba)",
        "cidade": "Caraguatatuba",
        "latitude": -23.6083,
        "longitude": -45.3833,
        "nivel_infraestrutura": 3,
        "descricao": (
            "Pequena enseada procurada por surfistas, com clima mais tranquilo que a "
            "orla principal de Caraguatatuba."
        ),
        "caracteristicas_mar": "Mar com ondas boas para surf iniciante a intermediário.",
        "faixa_areia": "Areia clara, faixa curta entre costões.",
        "dicas_seguranca": (
            "Atenção a pedras submersas nas laterais da enseada e à formação de "
            "correntes em dias de ressaca."
        ),
    },
    {
        "nome": "Praia Grande (Ubatuba)",
        "cidade": "Ubatuba",
        "latitude": -23.4372,
        "longitude": -45.0806,
        "nivel_infraestrutura": 5,
        "descricao": (
            "Uma das praias mais movimentadas de Ubatuba, com ampla estrutura de "
            "quiosques, pousadas e fácil acesso pelo centro da cidade."
        ),
        "caracteristicas_mar": "Mar de ondas moderadas a fortes, popular entre surfistas e bodyboarders.",
        "faixa_areia": "Areia clara, faixa larga e extensa.",
        "dicas_seguranca": (
            "Mar aberto sujeito a correntes de retorno; respeite a sinalização dos "
            "guarda-vidas, presentes na alta temporada, e evite banho em dias de ressaca."
        ),
    },
    {
        "nome": "Praia da Enseada",
        "cidade": "Ubatuba",
        "latitude": -23.4867,
        "longitude": -45.1189,
        "nivel_infraestrutura": 4,
        "descricao": (
            "Praia familiar bastante procurada em Ubatuba, com águas mais protegidas "
            "e boa oferta de pousadas e restaurantes."
        ),
        "caracteristicas_mar": "Mar calmo e protegido, uma das opções mais seguras da região para crianças.",
        "faixa_areia": "Areia clara, faixa larga e arborizada.",
        "dicas_seguranca": (
            "Praia relativamente segura, mas ainda assim vale observar a sinalização "
            "de bandeiras e evitar as pontas rochosas nas extremidades."
        ),
    },
    {
        "nome": "Lagoinha",
        "cidade": "Ubatuba",
        "latitude": -23.5389,
        "longitude": -45.1489,
        "nivel_infraestrutura": 3,
        "descricao": (
            "Praia charmosa com um pequeno arquipélago de ilhas na frente, conhecida "
            "por vilarejo de pescadores e boa gastronomia local."
        ),
        "caracteristicas_mar": "Mar geralmente calmo, protegido pelas ilhas próximas à costa.",
        "faixa_areia": "Areia clara, faixa moderada com vista para as Ilhas da Lagoinha.",
        "dicas_seguranca": (
            "Boa opção para banho tranquilo, mas fique atento ao tráfego de barcos de "
            "passeio que saem da praia em direção às ilhas."
        ),
    },
]

COMERCIOS = [
    {
        "praia_nome": "Juquehy",
        "praia_cidade": "São Sebastião",
        "nome": "Badauê",
        "categoria": "Restaurante",
        "distancia_areia_metros": 0,
        "link_afiliado": "https://booking.com/afiliado-teste-1",
    },
    {
        "praia_nome": "Maresias",
        "praia_cidade": "São Sebastião",
        "nome": "Santo Gole",
        "categoria": "Quiosque",
        "distancia_areia_metros": 50,
        "link_afiliado": "https://rentcars.com/afiliado-teste-2",
    },
    {
        "praia_nome": "Juquehy",
        "praia_cidade": "São Sebastião",
        "nome": "Pousada Sol e Mar",
        "categoria": "Pousada",
        "distancia_areia_metros": 300,
        "link_afiliado": _link_busca_booking("Pousada Sol e Mar", "Juquehy, São Sebastião"),
    },
    {
        "praia_nome": "Maresias",
        "praia_cidade": "São Sebastião",
        "nome": "Pousada Porto Mare",
        "categoria": "Pousada",
        "distancia_areia_metros": 50,
        "link_afiliado": _link_busca_booking("Pousada Porto Mare", "Maresias, São Sebastião"),
    },
    {
        "praia_nome": "Camburi",
        "praia_cidade": "São Sebastião",
        "nome": "Pousada Quintal da Mata",
        "categoria": "Pousada",
        "distancia_areia_metros": 1500,
        "link_afiliado": _link_busca_booking("Pousada Quintal da Mata", "Camburi, São Sebastião"),
    },
    {
        "praia_nome": "Barra do Una",
        "praia_cidade": "São Sebastião",
        "nome": "Pousada Una",
        "categoria": "Pousada",
        "distancia_areia_metros": 200,
        "link_afiliado": _link_busca_booking("Pousada Una", "Barra do Una, São Sebastião"),
    },
    {
        "praia_nome": "Baleia",
        "praia_cidade": "São Sebastião",
        "nome": "Pousada Praia da Baleia",
        "categoria": "Pousada",
        "distancia_areia_metros": 100,
        "link_afiliado": _link_busca_booking("Pousada Praia da Baleia", "São Sebastião"),
    },
    {
        "praia_nome": "Guaecá",
        "praia_cidade": "São Sebastião",
        "nome": "Pousada Castelinho",
        "categoria": "Pousada",
        "distancia_areia_metros": 500,
        "link_afiliado": _link_busca_booking("Pousada Castelinho", "Guaecá, São Sebastião"),
    },
    {
        "praia_nome": "Toque-Toque Grande",
        "praia_cidade": "São Sebastião",
        "nome": "Paraíso de Toque Toque Grande",
        "categoria": "Pousada",
        "distancia_areia_metros": 50,
        "link_afiliado": _link_busca_booking(
            "Paraíso de Toque Toque Grande", "São Sebastião"
        ),
    },
    {
        "praia_nome": "Prainha (Ilhabela)",
        "praia_cidade": "Ilhabela",
        "nome": "Pousada Ilhote da Prainha",
        "categoria": "Pousada",
        "distancia_areia_metros": 150,
        "link_afiliado": _link_busca_booking("Pousada Ilhote da Prainha", "Ilhabela"),
    },
    {
        "praia_nome": "Praia do Bonete",
        "praia_cidade": "Ilhabela",
        "nome": "Pousada da Rosa",
        "categoria": "Pousada",
        "distancia_areia_metros": 70,
        "link_afiliado": _link_busca_booking("Pousada da Rosa Bonete", "Ilhabela"),
    },
    {
        "praia_nome": "Praia do Pereque",
        "praia_cidade": "Ilhabela",
        "nome": "Pousada Perequê",
        "categoria": "Pousada",
        "distancia_areia_metros": 80,
        "link_afiliado": _link_busca_booking("Pousada Perequê", "Ilhabela"),
    },
    {
        "praia_nome": "Praia Martim de Sá",
        "praia_cidade": "Caraguatatuba",
        "nome": "Pousada Villa Del Mare",
        "categoria": "Pousada",
        "distancia_areia_metros": 150,
        "link_afiliado": _link_busca_booking("Pousada Villa Del Mare", "Caraguatatuba"),
    },
    {
        "praia_nome": "Prainha (Caraguatatuba)",
        "praia_cidade": "Caraguatatuba",
        "nome": "Pousada Morada da Prainha",
        "categoria": "Pousada",
        "distancia_areia_metros": 50,
        "link_afiliado": _link_busca_booking("Pousada Morada da Prainha", "Caraguatatuba"),
    },
    {
        "praia_nome": "Praia Grande (Ubatuba)",
        "praia_cidade": "Ubatuba",
        "nome": "Pousada Peixes do Mar",
        "categoria": "Pousada",
        "distancia_areia_metros": 200,
        "link_afiliado": _link_busca_booking(
            "Pousada Peixes do Mar", "Praia Grande, Ubatuba"
        ),
    },
    {
        "praia_nome": "Praia da Enseada",
        "praia_cidade": "Ubatuba",
        "nome": "Hotel Porto Di Mare",
        "categoria": "Pousada",
        "distancia_areia_metros": 100,
        "link_afiliado": _link_busca_booking("Hotel Porto Di Mare", "Enseada, Ubatuba"),
    },
    {
        "praia_nome": "Lagoinha",
        "praia_cidade": "Ubatuba",
        "nome": "Aldeia da Lagoinha",
        "categoria": "Pousada",
        "distancia_areia_metros": 300,
        "link_afiliado": _link_busca_booking("Aldeia da Lagoinha", "Ubatuba"),
    },
]


def seed() -> None:
    with SessionLocal() as db:
        try:
            praias_por_chave: dict[tuple[str, str], Praia] = {}

            for praia_data in PRAIAS:
                chave = (praia_data["nome"], praia_data["cidade"])
                praia = db.scalar(
                    select(Praia).where(
                        Praia.nome == praia_data["nome"],
                        Praia.cidade == praia_data["cidade"],
                    )
                )
                if praia is None:
                    praia = Praia(**praia_data)
                    db.add(praia)
                    db.flush()

                praias_por_chave[chave] = praia

            for comercio_data in COMERCIOS:
                chave = (comercio_data["praia_nome"], comercio_data["praia_cidade"])
                praia = praias_por_chave[chave]
                comercio_atributos = {
                    chave_atributo: valor
                    for chave_atributo, valor in comercio_data.items()
                    if chave_atributo not in ("praia_nome", "praia_cidade")
                }
                comercio = db.scalar(
                    select(Comercio).where(
                        Comercio.nome == comercio_atributos["nome"],
                        Comercio.praia_id == praia.id,
                    )
                )
                if comercio is None:
                    db.add(Comercio(praia_id=praia.id, **comercio_atributos))

            db.commit()
            print(f"Seed concluido: {len(PRAIAS)} praias verificadas/inseridas.")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed()

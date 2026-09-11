import logging
import random
import unicodedata

from app.services.weather_service import ClimaAtual, obter_climas_atuais


logger = logging.getLogger(__name__)


_CIDADES_LITORAL_NORTE = ("São Sebastião", "Ilhabela", "Caraguatatuba", "Ubatuba")

_PALAVRAS_CRIANCA = {
    "crianca", "criancas", "filho", "filhos", "filha", "filhas", "familia",
    "bebe", "infantil", "pequenos",
}
_PALAVRAS_CALMO = {
    "calma", "calmo", "tranquila", "tranquilo", "sossego", "descanso",
    "relaxar", "paz", "quieta", "quieto",
}
_PALAVRAS_SURF = {
    "surf", "surfar", "onda", "ondas", "bodyboard", "swell", "surfista",
}
_PALAVRAS_COMIDA = {
    "restaurante", "restaurantes", "quiosque", "quiosques", "comer",
    "comida", "almoco", "almocar", "bar", "gastronomia",
}
_MAR_TRANQUILO = ("calmo", "protegid", "tranquil", "abrigad", "raso", "sem ondas")
_MAR_AGITADO = ("ondas fortes", "agitad", "correnteza forte", "ondas boas para surf", "boas ondas")

_ABERTURAS_CRIANCA = (
    "Para curtir com a família em segurança, essas são minhas favoritas hoje:",
    "Ótima escolha pensar na criançada! Olha essas opções tranquilas:",
)
_ABERTURAS_SURF = (
    "Bora pegar onda! Essas praias estão com o mar mais favorável hoje:",
    "Para surfar hoje, essas são as melhores pedidas do Litoral Norte:",
)
_ABERTURAS_CIDADE = (
    "Olha o que encontrei em {cidade} para você:",
    "Em {cidade}, essas são as melhores opções agora:",
)
_ABERTURAS_GERAL = (
    "Show, deixa eu te ajudar a escolher! 🌊",
    "Com base no clima de hoje, aqui vão minhas recomendações:",
    "Boa pergunta! Olha só o que separei para você:",
)
_FECHAMENTOS = (
    "Quer que eu foque em outro perfil (família, surf, tranquilidade) ou em uma cidade específica?",
    "Se quiser, me conta mais sobre o que procura (surf, sossego, estrutura) que eu refino a sugestão.",
    "Posso detalhar mais alguma dessas praias, é só pedir!",
)


def _normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(caractere for caractere in texto if not unicodedata.combining(caractere))


def _contem_palavra(texto_normalizado: str, palavras: set[str]) -> bool:
    tokens = set(texto_normalizado.replace(",", " ").replace(".", " ").split())
    return not tokens.isdisjoint(palavras)


def _detectar_intencoes(mensagem: str, praias_contexto: list) -> dict:
    mensagem_normalizada = _normalizar(mensagem)

    cidade_mencionada = None
    for cidade in _CIDADES_LITORAL_NORTE:
        if _normalizar(cidade) in mensagem_normalizada:
            cidade_mencionada = cidade
            break

    praia_mencionada = None
    for praia in praias_contexto:
        if _normalizar(praia.nome) in mensagem_normalizada:
            praia_mencionada = praia.nome
            break

    return {
        "quer_familia": _contem_palavra(mensagem_normalizada, _PALAVRAS_CRIANCA),
        "quer_calmo": _contem_palavra(mensagem_normalizada, _PALAVRAS_CALMO),
        "quer_surf": _contem_palavra(mensagem_normalizada, _PALAVRAS_SURF),
        "quer_comida": _contem_palavra(mensagem_normalizada, _PALAVRAS_COMIDA),
        "cidade": cidade_mencionada,
        "praia_especifica": praia_mencionada,
    }


def _obter_climas_por_cidade(praias_contexto: list) -> dict[str, ClimaAtual | None]:
    coordenadas_por_cidade: dict[str, tuple[float, float]] = {}
    for praia in praias_contexto:
        coordenadas_por_cidade.setdefault(praia.cidade, (praia.latitude, praia.longitude))

    if not coordenadas_por_cidade:
        return {}

    try:
        climas_por_coordenada = obter_climas_atuais(list(coordenadas_por_cidade.values()))
    except Exception:
        logger.exception("Falha inesperada ao consultar o clima em lote")
        climas_por_coordenada = {}

    climas_por_cidade: dict[str, ClimaAtual | None] = {}
    for cidade, (latitude, longitude) in coordenadas_por_cidade.items():
        chave = (round(latitude, 2), round(longitude, 2))
        climas_por_cidade[cidade] = climas_por_coordenada.get(chave)

    return climas_por_cidade


def _pontuar_praia(praia, clima: ClimaAtual | None, intencoes: dict) -> float:
    if intencoes["praia_especifica"] and praia.nome == intencoes["praia_especifica"]:
        return 1000.0

    caracteristicas = _normalizar(f"{praia.caracteristicas_mar} {praia.descricao}")
    pontuacao = float(praia.nivel_infraestrutura) * 0.1

    quer_tranquilidade = intencoes["quer_familia"] or intencoes["quer_calmo"]
    if quer_tranquilidade:
        if any(termo in caracteristicas for termo in _MAR_TRANQUILO):
            pontuacao += 3
        if any(termo in caracteristicas for termo in _MAR_AGITADO):
            pontuacao -= 2
        if intencoes["quer_familia"]:
            pontuacao += praia.nivel_infraestrutura * 0.3

    if intencoes["quer_surf"]:
        if any(termo in caracteristicas for termo in _MAR_AGITADO) or "surf" in caracteristicas:
            pontuacao += 3
        if any(termo in caracteristicas for termo in _MAR_TRANQUILO):
            pontuacao -= 1

    if intencoes["quer_comida"]:
        pontuacao += len(getattr(praia, "comercios", [])) * 1.5

    if clima is not None:
        if clima.categoria in ("chuva", "frente_fria", "tempestade"):
            if any(termo in caracteristicas for termo in _MAR_TRANQUILO):
                pontuacao += 2
            if any(termo in caracteristicas for termo in _MAR_AGITADO):
                pontuacao -= 1.5
        elif clima.categoria == "sol":
            pontuacao += 0.5

    return pontuacao


def _resumo_clima(clima: ClimaAtual | None) -> str:
    if clima is None:
        return "não consegui confirmar o clima agora"
    return f"{clima.condicao}, {clima.temperatura_celsius:.0f}°C"


def _bloco_praia(praia, clima: ClimaAtual | None, mencionar_falta_de_comercio: bool = False) -> str:
    titulo = praia.nome if praia.cidade in praia.nome else f"{praia.nome} ({praia.cidade})"
    linhas = [f"### {titulo}"]
    linhas.append(f"Hoje está **{_resumo_clima(clima)}** por lá. {praia.caracteristicas_mar}")
    linhas.append(f"**Faixa de areia:** {praia.faixa_areia}")

    comercios = getattr(praia, "comercios", [])
    if comercios:
        comercio = comercios[0]
        if comercio.link_afiliado:
            linhas.append(
                f"**Para comer:** [{comercio.nome}]({comercio.link_afiliado}) ({comercio.categoria})."
            )
        else:
            linhas.append(f"**Para comer:** {comercio.nome} ({comercio.categoria}).")
    elif mencionar_falta_de_comercio:
        linhas.append("**Para comer:** ainda não tenho comércios cadastrados perto dessa praia.")

    linhas.append(f"**Dica de segurança:** {praia.dicas_seguranca}")
    return "\n\n".join(linhas)


def gerar_recomendacao_regras(mensagem_usuario: str, praias_contexto: list) -> str:
    """Motor de recomendacao por regras: cruza clima simulado + palavras-chave
    da pergunta do usuario para escolher praias, sem depender de nenhuma API
    de IA de terceiros. Usado como resposta principal quando nenhuma IA
    generativa esta configurada, e como fallback automatico quando a
    chamada a IA (Groq) falha por qualquer motivo.
    """
    if not praias_contexto:
        return "Ainda não tenho nenhuma praia cadastrada para recomendar. Volte em breve!"

    intencoes = _detectar_intencoes(mensagem_usuario, praias_contexto)
    climas_por_cidade = _obter_climas_por_cidade(praias_contexto)

    candidatas = praias_contexto
    if intencoes["cidade"] is not None:
        filtradas = [praia for praia in praias_contexto if praia.cidade == intencoes["cidade"]]
        if filtradas:
            candidatas = filtradas

    semente = random.Random(hash(mensagem_usuario.strip().lower()) & 0xFFFFFFFF)

    candidatas_ordenadas = sorted(
        candidatas,
        key=lambda praia: _pontuar_praia(praia, climas_por_cidade.get(praia.cidade), intencoes),
        reverse=True,
    )

    limite = 1 if intencoes["praia_especifica"] else 2
    escolhidas = candidatas_ordenadas[:limite]

    if intencoes["praia_especifica"]:
        abertura = f"Sobre a {intencoes['praia_especifica']}, aqui está o que sei:"
    elif intencoes["quer_familia"]:
        abertura = semente.choice(_ABERTURAS_CRIANCA)
    elif intencoes["quer_surf"]:
        abertura = semente.choice(_ABERTURAS_SURF)
    elif intencoes["cidade"]:
        abertura = semente.choice(_ABERTURAS_CIDADE).format(cidade=intencoes["cidade"])
    else:
        abertura = semente.choice(_ABERTURAS_GERAL)

    blocos = [
        _bloco_praia(
            praia,
            climas_por_cidade.get(praia.cidade),
            mencionar_falta_de_comercio=intencoes["quer_comida"],
        )
        for praia in escolhidas
    ]
    fechamento = semente.choice(_FECHAMENTOS)

    return "\n\n".join([abertura, *blocos, fechamento])

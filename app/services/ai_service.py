import logging
import os

from groq import Groq

from app.services.recommendation_rules import gerar_recomendacao_regras
from app.services.weather_service import ClimaAtual, obter_climas_atuais


logger = logging.getLogger(__name__)

GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_INSTRUCTION = """
Voce e a pra.ia, uma guia local carismatica e especialista no Litoral Norte de
Sao Paulo. Priorize conforto, praticidade e seguranca do turista. Recomende
trilhas pesadas somente quando o usuario solicitar explicitamente. Baseie suas
respostas no contexto recebido; se faltar informacao, deixe isso claro. Ao
mencionar comercios com links, apresente-os em Markdown (ex: [Nome](url)),
sem inventar estabelecimentos, precos, horarios ou URLs que nao estejam no
contexto.

Voce recebe o clima atual de cada cidade do Litoral Norte. Use essas
informacoes para adaptar a recomendacao:
- Chuva, frente fria ou tempestade: priorize praias com mar calmo e abrigado,
  reforce as dicas de seguranca, e sugira comercios proximos para o turista
  se abrigar.
- Sol: pode sugerir tanto praias calmas para familia quanto praias de ondas
  fortes para surf/bodyboard, conforme o perfil do turista.
- Sempre que recomendar uma praia, mencione de forma natural a condicao
  climatica atual da cidade dela.

Responda em portugues brasileiro, de forma objetiva e acolhedora, usando
Markdown (titulos, negrito, listas com marcadores) para organizar a resposta.
Nao use tabelas: prefira listas com marcadores, que ficam mais legiveis em
telas de celular. Seja conciso o suficiente para caber a resposta completa
sem cortar no meio.
""".strip()


class AIServiceError(RuntimeError):
    pass


def _formatar_contexto_clima(climas_por_cidade: dict[str, ClimaAtual | None]) -> str:
    if not climas_por_cidade:
        return "Nenhuma cidade disponivel para consulta de clima."

    linhas = []
    for cidade, clima in climas_por_cidade.items():
        if clima is None:
            linhas.append(f"- {cidade}: clima indisponivel no momento.")
            continue
        linhas.append(
            f"- {cidade}: {clima.condicao}, {clima.temperatura_celsius:.1f}°C, "
            f"vento {clima.velocidade_vento_kmh:.0f} km/h, categoria: {clima.categoria}."
        )
    return "\n".join(linhas)


def _formatar_contexto_praias(praias_contexto: list) -> str:
    blocos = []
    for praia in praias_contexto:
        detalhes = [
            f"Praia: {praia.nome}",
            f"Cidade: {praia.cidade}",
            f"Nivel de infraestrutura: {praia.nivel_infraestrutura}",
            f"Descricao: {praia.descricao}",
            f"Caracteristicas do mar: {praia.caracteristicas_mar}",
            f"Faixa de areia: {praia.faixa_areia}",
            f"Dicas de seguranca: {praia.dicas_seguranca}",
        ]

        comercios = getattr(praia, "comercios", [])
        if comercios:
            detalhes.append("Comercios proximos:")
            for comercio in comercios:
                link = f" Link: {comercio.link_afiliado}." if comercio.link_afiliado else ""
                detalhes.append(f"- {comercio.nome} ({comercio.categoria}).{link}")

        blocos.append("\n".join(detalhes))

    return "\n\n".join(blocos)


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


def _gerar_recomendacao_groq(mensagem_usuario: str, praias_contexto: list) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    climas_por_cidade = _obter_climas_por_cidade(praias_contexto)
    contexto_clima = _formatar_contexto_clima(climas_por_cidade)
    contexto_praias = _formatar_contexto_praias(praias_contexto)

    try:
        client = Groq(api_key=api_key)
        resposta = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {
                    "role": "user",
                    "content": (
                        f"Clima atual nas cidades do Litoral Norte:\n{contexto_clima}\n\n"
                        f"Contexto de praias cadastradas:\n{contexto_praias}\n\n"
                        f"Pergunta do turista: {mensagem_usuario}"
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=1400,
            reasoning_effort="low",
        )
    except Exception:
        logger.warning("Falha ao consultar a Groq; usando motor de regras.", exc_info=True)
        return None

    conteudo = resposta.choices[0].message.content
    if not conteudo or not conteudo.strip():
        logger.warning("Groq retornou resposta vazia; usando motor de regras.")
        return None

    return conteudo.strip()


def gerar_recomendacao(mensagem_usuario: str, praias_contexto: list) -> str:
    """Gera a recomendacao de praia para o turista.

    Tenta primeiro a IA generativa (Groq) para uma conversa mais natural e
    flexivel. Se a chave nao estiver configurada, a chamada falhar (rede,
    limite de uso, etc.) ou vier vazia, cai automaticamente no motor de
    regras local, que nunca depende de rede e sempre responde.
    """
    if not praias_contexto:
        return "Ainda não tenho nenhuma praia cadastrada para recomendar. Volte em breve!"

    resposta_groq = _gerar_recomendacao_groq(mensagem_usuario, praias_contexto)
    if resposta_groq is not None:
        return resposta_groq

    return gerar_recomendacao_regras(mensagem_usuario, praias_contexto)

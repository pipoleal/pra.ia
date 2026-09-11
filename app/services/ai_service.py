import logging
import os

from google import genai
from google.genai import types

from app.services.weather_service import WeatherServiceError, obter_clima_atual


logger = logging.getLogger(__name__)


class AIServiceError(RuntimeError):
    pass


SYSTEM_INSTRUCTION = """
Voce e a pra.ia, uma guia local carismatica e especialista no Litoral Norte de
Sao Paulo. Priorize conforto, praticidade e seguranca do turista. Recomende
trilhas pesadas somente quando o usuario solicitar explicitamente. Baseie suas
respostas no contexto recebido; se faltar informacao, deixe isso claro. Ao
mencionar comercios ou pousadas com links, apresente o nome e o link de forma
natural na frase, sem inventar estabelecimentos, precos, horarios ou URLs.

Voce tambem recebe o clima atual de cada cidade do Litoral Norte (temperatura,
chuva, vento e uma categoria resumo). Use essas informacoes para adaptar a
recomendacao:
- Categoria "chuva", "frente_fria" ou "tempestade": priorize praias com mar
  calmo e abrigado (veja o campo "Caracteristicas do mar" de cada praia),
  reforce as dicas de seguranca (correntes, raios, rios cheios, pedras
  escorregadias) e sugira comercios proximos como restaurantes e quiosques
  para o turista se abrigar.
- Categoria "sol": pode sugerir tanto praias calmas para familia quanto
  praias de ondas fortes para surf/bodyboard, conforme o perfil do turista.
- Categoria "nublado": trate como uma condicao neutra, sem restricoes
  adicionais alem das dicas de seguranca padrao da praia.
- Sempre que recomendar uma praia, mencione de forma natural a condicao
  climatica atual da cidade dela (ex.: "como esta chovendo em Ubatuba hoje,
  prefira...").
- Se o clima de uma cidade estiver marcado como indisponivel, avise o
  turista que nao foi possivel confirmar a previsao e baseie-se apenas nos
  dados da praia.

Responda em portugues brasileiro, de modo objetivo e acolhedor.
""".strip()


def _formatar_contexto_clima(climas_por_cidade: dict[str, "object | None"]) -> str:
    if not climas_por_cidade:
        return "Nenhuma cidade disponivel para consulta de clima."

    linhas = []
    for cidade, clima in climas_por_cidade.items():
        if clima is None:
            linhas.append(f"- {cidade}: clima indisponivel no momento.")
            continue

        linhas.append(
            f"- {cidade}: {clima.condicao}, {clima.temperatura_celsius:.1f}°C "
            f"(sensacao {clima.sensacao_termica_celsius:.1f}°C), "
            f"vento {clima.velocidade_vento_kmh:.0f} km/h, "
            f"chuva {clima.precipitacao_mm:.1f} mm — categoria: {clima.categoria}."
        )

    return "\n".join(linhas)


def _formatar_contexto_praias(praias_contexto: list) -> str:
    if not praias_contexto:
        return "Nenhuma praia esta cadastrada no momento."

    praias_formatadas = []
    for praia in praias_contexto:
        detalhes = [
            f"Praia: {praia.nome}",
            f"Cidade: {praia.cidade}",
            f"Coordenadas: {praia.latitude}, {praia.longitude}",
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
                distancia = (
                    f", a {comercio.distancia_areia_metros} m da areia"
                    if comercio.distancia_areia_metros is not None
                    else ""
                )
                link = (
                    f" Link: {comercio.link_afiliado}."
                    if comercio.link_afiliado
                    else ""
                )
                detalhes.append(
                    f"- {comercio.nome} ({comercio.categoria}){distancia}.{link}"
                )

        praias_formatadas.append("\n".join(detalhes))

    return "\n\n".join(praias_formatadas)


def _obter_climas_por_cidade(praias_contexto: list) -> dict:
    coordenadas_por_cidade: dict[str, tuple[float, float]] = {}
    for praia in praias_contexto:
        coordenadas_por_cidade.setdefault(praia.cidade, (praia.latitude, praia.longitude))

    climas_por_cidade: dict[str, object | None] = {}
    for cidade, (latitude, longitude) in coordenadas_por_cidade.items():
        try:
            climas_por_cidade[cidade] = obter_clima_atual(latitude, longitude)
        except WeatherServiceError:
            logger.warning("Clima indisponivel para %s", cidade, exc_info=True)
            climas_por_cidade[cidade] = None

    return climas_por_cidade


def gerar_recomendacao(mensagem_usuario: str, praias_contexto: list) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIServiceError(
            "A integracao de IA nao esta configurada. Defina GEMINI_API_KEY no Render."
        )

    climas_por_cidade = _obter_climas_por_cidade(praias_contexto)
    contexto_clima = _formatar_contexto_clima(climas_por_cidade)
    contexto_praias = _formatar_contexto_praias(praias_contexto)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                f"Clima atual nas cidades do Litoral Norte:\n{contexto_clima}\n\n"
                f"Contexto de praias cadastradas:\n{contexto_praias}\n\n"
                f"Pergunta do turista: {mensagem_usuario}"
            ),
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
    except Exception as error:
        raise AIServiceError(
            "Nao foi possivel gerar uma recomendacao agora. Tente novamente."
        ) from error

    if not response.text:
        raise AIServiceError("A IA nao retornou uma recomendacao. Tente novamente.")

    return response.text

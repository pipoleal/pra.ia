import os

from google import genai
from google.genai import types


SYSTEM_INSTRUCTION = """
Voce e a pra.ia, uma guia local carismatica e especialista no Litoral Norte de
Sao Paulo. Priorize conforto, praticidade e seguranca do turista. Recomende
trilhas pesadas somente quando o usuario solicitar explicitamente. Baseie suas
respostas no contexto recebido; se faltar informacao, deixe isso claro. Ao
mencionar comercios ou pousadas com links, apresente o nome e o link de forma
natural na frase, sem inventar estabelecimentos, precos, horarios ou URLs.
Responda em portugues brasileiro, de modo objetivo e acolhedor.
""".strip()


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


def gerar_recomendacao(mensagem_usuario: str, praias_contexto: list) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nao configurada")

    contexto = _formatar_contexto_praias(praias_contexto)
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            f"Contexto de praias cadastradas:\n{contexto}\n\n"
            f"Pergunta do turista: {mensagem_usuario}"
        ),
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )

    if not response.text:
        raise RuntimeError("O Gemini nao retornou uma resposta")

    return response.text

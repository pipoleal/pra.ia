import logging
import threading
import time
from dataclasses import dataclass


import httpx


logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Cache "fresco": dentro desse intervalo, nunca voltamos a chamar a API externa.
CACHE_TTL_SEGUNDOS = 7200  # 2 horas
TIMEOUT_SEGUNDOS = 5.0

_CODIGOS_CHUVA = {51, 53, 55, 61, 63, 65, 80, 81, 82}
_CODIGOS_TEMPESTADE = {95, 96, 99}
_CODIGOS_NUBLADO = {2, 3, 45, 48}

_DESCRICOES_WEATHER_CODE = {
    0: "céu limpo",
    1: "predominantemente ensolarado",
    2: "parcialmente nublado",
    3: "encoberto",
    45: "neblina",
    48: "neblina com formação de geada",
    51: "garoa fraca",
    53: "garoa moderada",
    55: "garoa forte",
    61: "chuva fraca",
    63: "chuva moderada",
    65: "chuva forte",
    71: "neve fraca",
    80: "pancadas de chuva fracas",
    81: "pancadas de chuva moderadas",
    82: "pancadas de chuva fortes",
    95: "tempestade com trovoadas",
    96: "tempestade com granizo",
    99: "tempestade forte com granizo",
}


class WeatherServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class ClimaAtual:
    temperatura_celsius: float
    sensacao_termica_celsius: float
    precipitacao_mm: float
    velocidade_vento_kmh: float
    condicao: str
    categoria: str


@dataclass
class _EntradaCache:
    clima: ClimaAtual
    obtido_em: float


Coordenada = tuple[float, float]

# Cache global do processo. Guarda o ultimo clima valido de cada coordenada,
# mesmo depois de expirado, para servir de fallback (cache estaleiro) caso a
# API externa falhe ou retorne 429. Protegido por _lock pois a rota /chat/ e
# sincrona e pode ser executada em threads concorrentes.
_cache: dict[Coordenada, _EntradaCache] = {}
_lock = threading.Lock()


def _chave(latitude: float, longitude: float) -> Coordenada:
    return (round(latitude, 2), round(longitude, 2))


def _cache_fresco(entrada: _EntradaCache, agora: float) -> bool:
    return (agora - entrada.obtido_em) < CACHE_TTL_SEGUNDOS


def _descrever_weather_code(codigo: int) -> str:
    return _DESCRICOES_WEATHER_CODE.get(codigo, "condições indefinidas")


def _categorizar(codigo: int, temperatura: float, vento_kmh: float) -> str:
    if codigo in _CODIGOS_TEMPESTADE:
        return "tempestade"
    if codigo in _CODIGOS_CHUVA:
        if temperatura < 21 and vento_kmh > 25:
            return "frente_fria"
        return "chuva"
    if codigo in _CODIGOS_NUBLADO:
        return "nublado"
    return "sol"


def _buscar_lote(coordenadas: list[Coordenada]) -> dict[Coordenada, ClimaAtual]:
    """Consulta o clima de varias coordenadas em uma unica requisicao HTTP.

    O Open-Meteo aceita listas de latitude/longitude separadas por virgula e
    devolve um item por coordenada, na mesma ordem em que foram enviadas.
    """
    resposta = httpx.get(
        OPEN_METEO_URL,
        params={
            "latitude": ",".join(str(lat) for lat, _ in coordenadas),
            "longitude": ",".join(str(lon) for _, lon in coordenadas),
            "current": (
                "temperature_2m,apparent_temperature,precipitation,"
                "weather_code,wind_speed_10m"
            ),
            "timezone": "America/Sao_Paulo",
        },
        timeout=TIMEOUT_SEGUNDOS,
    )
    resposta.raise_for_status()
    dados = resposta.json()

    # Com uma unica coordenada a API responde um objeto; com varias, uma lista.
    itens = dados if isinstance(dados, list) else [dados]
    if len(itens) != len(coordenadas):
        raise WeatherServiceError("Resposta do Open-Meteo em formato inesperado.")

    climas: dict[Coordenada, ClimaAtual] = {}
    for coordenada, item in zip(coordenadas, itens):
        atual = item["current"]
        codigo = int(atual["weather_code"])
        temperatura = float(atual["temperature_2m"])
        vento = float(atual["wind_speed_10m"])

        climas[coordenada] = ClimaAtual(
            temperatura_celsius=temperatura,
            sensacao_termica_celsius=float(atual["apparent_temperature"]),
            precipitacao_mm=float(atual["precipitation"]),
            velocidade_vento_kmh=vento,
            condicao=_descrever_weather_code(codigo),
            categoria=_categorizar(codigo, temperatura, vento),
        )

    return climas


def obter_climas_atuais(coordenadas: list[Coordenada]) -> dict[Coordenada, ClimaAtual]:
    """Retorna o clima atual para varias coordenadas de uma so vez.

    - Coordenadas com cache fresco (< CACHE_TTL_SEGUNDOS) nunca disparam
      requisicao de rede.
    - As coordenadas restantes sao buscadas em uma UNICA chamada em lote ao
      Open-Meteo, evitando o disparo de uma requisicao por praia/cidade.
    - Se a chamada em lote falhar (ex: 429, timeout, instabilidade), o ultimo
      valor conhecido de cada coordenada (cache estaleiro) e reaproveitado em
      vez de propagar o erro, para que o chat nunca quebre por causa do clima.
    - Uma coordenada sem nenhum cache previo e sem resposta valida da API
      simplesmente fica de fora do dicionario retornado; quem chamar deve
      tratar a ausencia como "clima indisponivel".
    """
    if not coordenadas:
        return {}

    agora = time.monotonic()
    resultado: dict[Coordenada, ClimaAtual] = {}

    with _lock:
        chaves_unicas = list(dict.fromkeys(_chave(lat, lon) for lat, lon in coordenadas))
        pendentes = []
        for chave in chaves_unicas:
            entrada = _cache.get(chave)
            if entrada is not None and _cache_fresco(entrada, agora):
                resultado[chave] = entrada.clima
            else:
                pendentes.append(chave)

        if not pendentes:
            return resultado

        try:
            climas_novos = _buscar_lote(pendentes)
        except (httpx.HTTPError, WeatherServiceError, KeyError, TypeError, ValueError) as error:
            logger.warning(
                "Falha ao consultar Open-Meteo em lote para %s coordenada(s): %s",
                len(pendentes),
                error,
            )
            climas_novos = {}

        for chave in pendentes:
            clima_novo = climas_novos.get(chave)
            if clima_novo is not None:
                _cache[chave] = _EntradaCache(clima=clima_novo, obtido_em=agora)
                resultado[chave] = clima_novo
                continue

            entrada_estaleira = _cache.get(chave)
            if entrada_estaleira is not None:
                logger.info("Usando cache estaleiro de clima para %s", chave)
                resultado[chave] = entrada_estaleira.clima

    return resultado


def obter_clima_atual(latitude: float, longitude: float) -> ClimaAtual:
    """Busca o clima de uma unica coordenada (usa o mesmo cache/lote)."""
    climas = obter_climas_atuais([(latitude, longitude)])
    clima = climas.get(_chave(latitude, longitude))
    if clima is None:
        raise WeatherServiceError("Nao foi possivel obter a previsao do tempo agora.")
    return clima

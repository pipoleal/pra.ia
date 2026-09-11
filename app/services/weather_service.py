import time
from dataclasses import dataclass

import httpx


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL_SEGUNDOS = 1800
TIMEOUT_SEGUNDOS = 4.0

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


_cache: dict[tuple[float, float], tuple[float, ClimaAtual]] = {}


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


def obter_clima_atual(latitude: float, longitude: float) -> ClimaAtual:
    chave_cache = (round(latitude, 2), round(longitude, 2))
    agora = time.monotonic()

    em_cache = _cache.get(chave_cache)
    if em_cache is not None:
        expira_em, clima = em_cache
        if agora < expira_em:
            return clima

    try:
        resposta = httpx.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,apparent_temperature,precipitation,"
                    "weather_code,wind_speed_10m"
                ),
                "timezone": "America/Sao_Paulo",
            },
            timeout=TIMEOUT_SEGUNDOS,
        )
        resposta.raise_for_status()
        dados = resposta.json()["current"]

        codigo = int(dados["weather_code"])
        temperatura = float(dados["temperature_2m"])
        vento = float(dados["wind_speed_10m"])

        clima = ClimaAtual(
            temperatura_celsius=temperatura,
            sensacao_termica_celsius=float(dados["apparent_temperature"]),
            precipitacao_mm=float(dados["precipitation"]),
            velocidade_vento_kmh=vento,
            condicao=_descrever_weather_code(codigo),
            categoria=_categorizar(codigo, temperatura, vento),
        )
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
        raise WeatherServiceError(
            "Nao foi possivel obter a previsao do tempo agora."
        ) from error

    _cache[chave_cache] = (agora + CACHE_TTL_SEGUNDOS, clima)
    return clima

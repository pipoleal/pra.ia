import hashlib
import random
from dataclasses import dataclass
from datetime import date


class WeatherServiceError(RuntimeError):
    """Mantida por compatibilidade com quem importa este modulo.

    O simulador climatico abaixo e puramente local (sem I/O de rede), entao
    na pratica nunca deveria levantar esta excecao.
    """


@dataclass(frozen=True)
class ClimaAtual:
    temperatura_celsius: float
    sensacao_termica_celsius: float
    precipitacao_mm: float
    velocidade_vento_kmh: float
    condicao: str
    categoria: str


Coordenada = tuple[float, float]


@dataclass(frozen=True)
class _PerfilSazonal:
    estacao: str
    temperatura_min: float
    temperatura_max: float
    vento_min: float
    vento_max: float
    distribuicao_categorias: tuple[tuple[str, float], ...]


# Perfis climaticos tipicos do Litoral Norte de SP por mes, seguindo as
# estacoes do hemisferio sul (verao: dez-mar, outono: mar-jun, inverno:
# jun-set, primavera: set-dez). Setembro/outubro/novembro (primavera) tem
# maior instabilidade por causa da passagem de frentes frias, por isso a
# categoria "frente_fria" e mais provavel nesses meses.
_PERFIS_POR_MES: dict[int, _PerfilSazonal] = {
    1: _PerfilSazonal("verão", 25.0, 32.0, 5.0, 22.0, (("sol", 0.45), ("nublado", 0.20), ("chuva", 0.15), ("tempestade", 0.20))),
    2: _PerfilSazonal("verão", 25.0, 32.0, 5.0, 22.0, (("sol", 0.45), ("nublado", 0.20), ("chuva", 0.15), ("tempestade", 0.20))),
    3: _PerfilSazonal("verão/outono", 23.0, 29.0, 5.0, 20.0, (("sol", 0.50), ("nublado", 0.22), ("chuva", 0.20), ("tempestade", 0.08))),
    4: _PerfilSazonal("outono", 21.0, 27.0, 5.0, 20.0, (("sol", 0.55), ("nublado", 0.25), ("chuva", 0.15), ("frente_fria", 0.05))),
    5: _PerfilSazonal("outono", 19.0, 25.0, 5.0, 22.0, (("sol", 0.50), ("nublado", 0.28), ("chuva", 0.15), ("frente_fria", 0.07))),
    6: _PerfilSazonal("inverno", 17.0, 23.0, 5.0, 25.0, (("sol", 0.55), ("nublado", 0.28), ("chuva", 0.10), ("frente_fria", 0.07))),
    7: _PerfilSazonal("inverno", 16.0, 22.0, 5.0, 25.0, (("sol", 0.55), ("nublado", 0.28), ("chuva", 0.08), ("frente_fria", 0.09))),
    8: _PerfilSazonal("inverno/primavera", 17.0, 24.0, 6.0, 28.0, (("sol", 0.50), ("nublado", 0.27), ("chuva", 0.13), ("frente_fria", 0.10))),
    9: _PerfilSazonal("primavera", 18.0, 25.0, 8.0, 30.0, (("sol", 0.35), ("nublado", 0.25), ("chuva", 0.25), ("frente_fria", 0.15))),
    10: _PerfilSazonal("primavera", 20.0, 27.0, 7.0, 28.0, (("sol", 0.40), ("nublado", 0.25), ("chuva", 0.20), ("frente_fria", 0.15))),
    11: _PerfilSazonal("primavera", 22.0, 29.0, 6.0, 25.0, (("sol", 0.45), ("nublado", 0.22), ("chuva", 0.20), ("frente_fria", 0.13))),
    12: _PerfilSazonal("verão", 24.0, 31.0, 5.0, 22.0, (("sol", 0.45), ("nublado", 0.20), ("chuva", 0.15), ("tempestade", 0.20))),
}

_CONDICOES_POR_CATEGORIA: dict[str, tuple[str, ...]] = {
    "sol": ("céu limpo", "predominantemente ensolarado", "parcialmente nublado com sol forte"),
    "nublado": ("parcialmente nublado", "encoberto", "nublado com aberturas de sol"),
    "chuva": ("garoa fraca", "chuva passageira", "pancadas de chuva moderadas"),
    "frente_fria": (
        "chuva e vento forte (frente fria)",
        "céu encoberto com vento forte (frente fria)",
        "chuva com queda de temperatura (frente fria)",
    ),
    "tempestade": (
        "pancadas de chuva fortes com trovoadas",
        "tempestade de verão à tarde",
        "chuva forte com risco de raios",
    ),
}


def _chave(latitude: float, longitude: float) -> Coordenada:
    return (round(latitude, 2), round(longitude, 2))


def _seed_para(coordenada: Coordenada, referencia: date) -> int:
    """Gera uma semente estavel para o dia e a coordenada dados.

    O clima simulado so muda de um dia para o outro (ou quando a coordenada
    muda); dentro do mesmo dia, a mesma coordenada sempre produz o mesmo
    resultado, garantindo estabilidade nas recomendacoes do chat.
    """
    chave = f"{referencia.isoformat()}:{coordenada[0]:.2f}:{coordenada[1]:.2f}"
    digest = hashlib.sha256(chave.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _gerar_clima_simulado(coordenada: Coordenada, referencia: date) -> ClimaAtual:
    perfil = _PERFIS_POR_MES[referencia.month]
    rng = random.Random(_seed_para(coordenada, referencia))

    categorias, pesos = zip(*perfil.distribuicao_categorias)
    categoria = rng.choices(categorias, weights=pesos, k=1)[0]

    temperatura = rng.uniform(perfil.temperatura_min, perfil.temperatura_max)
    vento = rng.uniform(perfil.vento_min, perfil.vento_max)
    precipitacao = 0.0

    if categoria == "nublado":
        temperatura -= rng.uniform(0.5, 1.5)
    elif categoria == "chuva":
        temperatura -= rng.uniform(1.0, 3.0)
        vento += rng.uniform(0.0, 5.0)
        precipitacao = rng.uniform(1.0, 8.0)
    elif categoria == "frente_fria":
        temperatura -= rng.uniform(3.0, 6.0)
        vento += rng.uniform(10.0, 20.0)
        precipitacao = rng.uniform(2.0, 15.0)
    elif categoria == "tempestade":
        temperatura -= rng.uniform(1.0, 4.0)
        vento += rng.uniform(5.0, 15.0)
        precipitacao = rng.uniform(8.0, 30.0)

    variacao_sensacao = rng.uniform(-1.0, 3.0) if categoria == "sol" else rng.uniform(-1.5, 1.0)
    condicao = rng.choice(_CONDICOES_POR_CATEGORIA[categoria])

    return ClimaAtual(
        temperatura_celsius=round(temperatura, 1),
        sensacao_termica_celsius=round(temperatura + variacao_sensacao, 1),
        precipitacao_mm=round(precipitacao, 1),
        velocidade_vento_kmh=round(max(vento, 0.0), 1),
        condicao=condicao,
        categoria=categoria,
    )


def obter_climas_atuais(coordenadas: list[Coordenada]) -> dict[Coordenada, ClimaAtual]:
    """Simula o clima atual para varias coordenadas, sem nenhuma chamada de rede.

    O resultado e determinado pela epoca do ano (mes atual) e pela coordenada,
    com uma pequena variacao pseudo-aleatoria porem estavel ao longo do dia
    (mesma coordenada + mesmo dia = mesmo resultado). Isso elimina por completo
    a dependencia de APIs externas de clima e o risco de erros como 429.
    """
    if not coordenadas:
        return {}

    referencia = date.today()
    resultado: dict[Coordenada, ClimaAtual] = {}
    for latitude, longitude in coordenadas:
        chave = _chave(latitude, longitude)
        if chave not in resultado:
            resultado[chave] = _gerar_clima_simulado(chave, referencia)

    return resultado


def obter_clima_atual(latitude: float, longitude: float) -> ClimaAtual:
    """Simula o clima atual de uma unica coordenada (ver obter_climas_atuais)."""
    return obter_climas_atuais([(latitude, longitude)])[_chave(latitude, longitude)]

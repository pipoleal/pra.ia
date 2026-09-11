from sqlalchemy import select

from app.database import SessionLocal
from app.models import Comercio, Praia


PRAIAS = [
    {
        "nome": "Juquehy",
        "cidade": "São Sebastião",
        "latitude": -23.7653,
        "longitude": -45.7347,
        "nivel_infraestrutura": 5,
        "descricao": (
            "Praia extensa, mar calmo no canto direito, ideal para famílias e "
            "com excelente estrutura de restaurantes."
        ),
    },
    {
        "nome": "Maresias",
        "cidade": "São Sebastião",
        "latitude": -23.7918,
        "longitude": -45.5608,
        "nivel_infraestrutura": 4,
        "descricao": (
            "Famosa pelas ondas, point de surfistas e jovens. Agito noturno "
            "forte e muitos bares."
        ),
    },
]

COMERCIOS = [
    {
        "praia_nome": "Juquehy",
        "nome": "Badauê",
        "categoria": "Restaurante",
        "distancia_areia_metros": 0,
        "link_afiliado": "https://booking.com/afiliado-teste-1",
    },
    {
        "praia_nome": "Maresias",
        "nome": "Santo Gole",
        "categoria": "Quiosque",
        "distancia_areia_metros": 50,
        "link_afiliado": "https://rentcars.com/afiliado-teste-2",
    },
]


def seed() -> None:
    with SessionLocal() as db:
        try:
            praias_por_nome: dict[str, Praia] = {}

            for praia_data in PRAIAS:
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

                praias_por_nome[praia.nome] = praia

            for comercio_data in COMERCIOS:
                praia_nome = comercio_data["praia_nome"]
                praia = praias_por_nome[praia_nome]
                comercio_atributos = {
                    chave: valor
                    for chave, valor in comercio_data.items()
                    if chave != "praia_nome"
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
            print("Dados iniciais inseridos com sucesso.")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed()

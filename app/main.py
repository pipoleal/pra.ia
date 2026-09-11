import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database import engine, get_db
from app.models import Base, Praia
from app.schemas import ChatRequest, ChatResponse, PraiaCreate, PraiaResponse
from app.seed import seed
from app.services.ai_service import AIServiceError, gerar_recomendacao


logger = logging.getLogger(__name__)


app = FastAPI(title="praIA", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _upgrade_schema() -> None:
    """Adiciona colunas novas em bancos ja existentes (nao ha Alembic no projeto)."""
    inspector = inspect(engine)
    if "praia" not in inspector.get_table_names():
        return

    colunas_existentes = {coluna["name"] for coluna in inspector.get_columns("praia")}
    colunas_novas = ("caracteristicas_mar", "faixa_areia", "dicas_seguranca")
    faltantes = [coluna for coluna in colunas_novas if coluna not in colunas_existentes]
    if not faltantes:
        return

    with engine.begin() as connection:
        for coluna in faltantes:
            connection.execute(
                text(f"ALTER TABLE praia ADD COLUMN {coluna} TEXT NOT NULL DEFAULT ''")
            )


Base.metadata.create_all(bind=engine)
_upgrade_schema()

try:
    seed()
except SQLAlchemyError:
    logger.exception("Falha ao executar o seed inicial de praias")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "praIA API online"}


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error

    return {"status": "ok", "database": "connected"}


@app.post("/praias/", response_model=PraiaResponse, status_code=201)
def create_praia(praia: PraiaCreate, db: Session = Depends(get_db)) -> Praia:
    nova_praia = Praia(**praia.model_dump())
    db.add(nova_praia)
    db.commit()
    db.refresh(nova_praia)
    return nova_praia


@app.get("/praias/", response_model=list[PraiaResponse])
def list_praias(db: Session = Depends(get_db)) -> list[Praia]:
    return list(db.scalars(select(Praia)).all())


@app.post("/praias/seed", status_code=200)
def seed_praias() -> dict[str, str]:
    try:
        seed()
    except SQLAlchemyError as error:
        logger.exception("Falha ao executar o seed de praias via endpoint")
        raise HTTPException(
            status_code=500, detail="Nao foi possivel executar o seed de praias."
        ) from error

    return {"status": "ok", "message": "Seed de praias executado com sucesso."}


@app.post("/chat/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        praias = list(
            db.scalars(select(Praia).options(selectinload(Praia.comercios))).all()
        )
        resposta = gerar_recomendacao(request.mensagem, praias)
    except AIServiceError as error:
        logger.exception("Falha ao gerar recomendacao")
        raise HTTPException(status_code=500, detail=str(error)) from error
    except SQLAlchemyError as error:
        logger.exception("Falha ao consultar praias para o chat")
        raise HTTPException(
            status_code=500,
            detail="Nao foi possivel consultar os dados das praias. Tente novamente.",
        ) from error
    except Exception as error:
        logger.exception("Falha inesperada na rota de chat")
        raise HTTPException(
            status_code=500,
            detail="Nao foi possivel processar sua mensagem. Tente novamente.",
        ) from error

    return ChatResponse(resposta=resposta)

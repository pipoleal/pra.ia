from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database import engine, get_db
from app.models import Base, Praia
from app.schemas import ChatRequest, ChatResponse, PraiaCreate, PraiaResponse
from app.services.ai_service import gerar_recomendacao


app = FastAPI(title="praIA", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


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


@app.post("/chat/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    praias = list(
        db.scalars(select(Praia).options(selectinload(Praia.comercios))).all()
    )

    try:
        resposta = gerar_recomendacao(request.mensagem, praias)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return ChatResponse(resposta=resposta)

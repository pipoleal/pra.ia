from pydantic import BaseModel, ConfigDict


class PraiaBase(BaseModel):
    nome: str
    cidade: str
    latitude: float
    longitude: float
    nivel_infraestrutura: int
    descricao: str
    caracteristicas_mar: str
    faixa_areia: str
    dicas_seguranca: str


class PraiaCreate(PraiaBase):
    pass


class PraiaResponse(PraiaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    mensagem: str


class ChatResponse(BaseModel):
    resposta: str

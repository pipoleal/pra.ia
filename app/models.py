from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Praia(Base):
    __tablename__ = "praia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String)
    cidade: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    nivel_infraestrutura: Mapped[int] = mapped_column(Integer)
    descricao: Mapped[str] = mapped_column(Text)
    caracteristicas_mar: Mapped[str] = mapped_column(Text, server_default="")
    faixa_areia: Mapped[str] = mapped_column(Text, server_default="")
    dicas_seguranca: Mapped[str] = mapped_column(Text, server_default="")

    comercios: Mapped[list["Comercio"]] = relationship(back_populates="praia")
    monitoramentos: Mapped[list["MonitoramentoPraia"]] = relationship(
        back_populates="praia"
    )


class Comercio(Base):
    __tablename__ = "comercio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    praia_id: Mapped[int] = mapped_column(ForeignKey("praia.id"))
    nome: Mapped[str] = mapped_column(String)
    categoria: Mapped[str] = mapped_column(String)
    link_afiliado: Mapped[str | None] = mapped_column(String, nullable=True)
    distancia_areia_metros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destaque: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    praia: Mapped["Praia"] = relationship(back_populates="comercios")


class MonitoramentoPraia(Base):
    __tablename__ = "monitoramento_praia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    praia_id: Mapped[int] = mapped_column(ForeignKey("praia.id"))
    balneabilidade: Mapped[str] = mapped_column(String)
    temperatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    alerta_transito: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_leitura: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    praia: Mapped["Praia"] = relationship(back_populates="monitoramentos")

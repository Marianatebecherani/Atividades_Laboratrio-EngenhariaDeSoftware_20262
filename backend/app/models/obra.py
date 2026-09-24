from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, ComDatas
from app.models.enums import TipoObra
from app.models.obra_genero import obras_generos
from app.models.tipos import enum_como_texto

if TYPE_CHECKING:
    from app.models.avaliacao import Avaliacao
    from app.models.genero import Genero
    from app.models.item_lista import ItemLista
    from app.models.poster import Poster

ANO_LANCAMENTO_MINIMO = 1888
CLASSIFICACOES_INDICATIVAS = (0, 10, 12, 14, 16, 18)


class Obra(ComDatas, Base):
    """Filme ou série do catálogo."""

    __tablename__ = "obras"
    __table_args__ = (
        CheckConstraint(
            "(tipo = 'filme' AND duracao_minutos IS NOT NULL AND temporadas IS NULL)"
            " OR (tipo = 'serie' AND temporadas IS NOT NULL AND duracao_minutos IS NULL)",
            name="duracao_conforme_tipo",
        ),
        CheckConstraint(f"ano_lancamento >= {ANO_LANCAMENTO_MINIMO}", name="ano_lancamento_valido"),
        CheckConstraint(
            f"classificacao_indicativa IN {CLASSIFICACOES_INDICATIVAS}",
            name="classificacao_indicativa_valida",
        ),
        CheckConstraint("duracao_minutos > 0", name="duracao_minutos_positiva"),
        CheckConstraint("temporadas > 0", name="temporadas_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), index=True)
    tipo: Mapped[TipoObra] = mapped_column(enum_como_texto(TipoObra, "tipo_obra"), index=True)
    ano_lancamento: Mapped[int] = mapped_column(SmallInteger, index=True)
    sinopse: Mapped[str | None] = mapped_column(Text)
    classificacao_indicativa: Mapped[int] = mapped_column(SmallInteger)
    duracao_minutos: Mapped[int | None] = mapped_column(SmallInteger)
    temporadas: Mapped[int | None] = mapped_column(SmallInteger)

    generos: Mapped[list["Genero"]] = relationship(
        secondary=obras_generos, back_populates="obras", passive_deletes=True
    )
    poster: Mapped["Poster | None"] = relationship(
        back_populates="obra", cascade="all, delete-orphan", passive_deletes=True
    )
    itens_lista: Mapped[list["ItemLista"]] = relationship(
        back_populates="obra", cascade="all, delete-orphan", passive_deletes=True
    )
    avaliacoes: Mapped[list["Avaliacao"]] = relationship(
        back_populates="obra", cascade="all, delete-orphan", passive_deletes=True
    )

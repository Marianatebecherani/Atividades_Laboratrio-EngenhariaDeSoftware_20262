from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, ComDatas
from app.models.usuario import Usuario

NOTA_MINIMA = 1
NOTA_MAXIMA = 5


class Avaliacao(ComDatas, Base):
    """Nota (1 a 5) e comentário opcional de um usuário sobre uma obra."""

    __tablename__ = "avaliacoes"
    __table_args__ = (
        UniqueConstraint("usuario_id", "tmdb_id", name="uq_avaliacoes_usuario_tmdb"),
        CheckConstraint(f"nota BETWEEN {NOTA_MINIMA} AND {NOTA_MAXIMA}", name="nota_valida"),
        CheckConstraint("tmdb_id > 0", name="tmdb_id_positivo"),
        Index("ix_avaliacoes_tmdb_id", "tmdb_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    tmdb_id: Mapped[int] = mapped_column(Integer)
    nota: Mapped[int] = mapped_column(SmallInteger)
    comentario: Mapped[str | None] = mapped_column(Text)

    usuario: Mapped["Usuario"] = relationship(back_populates="avaliacoes")

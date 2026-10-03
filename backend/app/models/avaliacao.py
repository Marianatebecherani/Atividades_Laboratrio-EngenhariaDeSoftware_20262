from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from app.models.obra import Obra
    from app.models.usuario import Usuario

NOTA_MINIMA = 1
NOTA_MAXIMA = 5


class Avaliacao(ComDatas, Base):
    """Nota (1 a 5) e comentário opcional de um usuário sobre uma obra."""

    __tablename__ = "avaliacoes"
    __table_args__ = (
        UniqueConstraint("usuario_id", "obra_id", name="uq_avaliacoes_usuario_obra"),
        UniqueConstraint("usuario_id", "tmdb_id", name="uq_avaliacoes_usuario_tmdb"),
        CheckConstraint(f"nota BETWEEN {NOTA_MINIMA} AND {NOTA_MAXIMA}", name="nota_valida"),
        CheckConstraint(
            "(obra_id IS NOT NULL AND tmdb_id IS NULL) OR "
            "(obra_id IS NULL AND tmdb_id IS NOT NULL)",
            name="um_alvo",
        ),
        CheckConstraint("tmdb_id IS NULL OR tmdb_id > 0", name="tmdb_id_positivo"),
        Index("ix_avaliacoes_tmdb_id", "tmdb_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    obra_id: Mapped[int | None] = mapped_column(
        ForeignKey("obras.id", ondelete="CASCADE"), index=True
    )
    tmdb_id: Mapped[int | None] = mapped_column(Integer)
    nota: Mapped[int] = mapped_column(SmallInteger)
    comentario: Mapped[str | None] = mapped_column(Text)

    usuario: Mapped["Usuario"] = relationship(back_populates="avaliacoes")
    obra: Mapped["Obra | None"] = relationship(back_populates="avaliacoes")

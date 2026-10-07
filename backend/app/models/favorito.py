from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Favorito(Base):
    """Referência de favorito do usuário a um filme externo, sem metadados cinematográficos."""

    __tablename__ = "favoritos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "tmdb_id", name="uq_favoritos_usuario_tmdb"),
        CheckConstraint("tmdb_id > 0", name="tmdb_id_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    tmdb_id: Mapped[int] = mapped_column(Integer, index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="favoritos")

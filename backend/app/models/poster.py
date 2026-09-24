from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.obra import Obra

TAMANHO_MAXIMO_BYTES = 2 * 1024 * 1024
TIPOS_MIME_PERMITIDOS = ("image/jpeg", "image/png", "image/webp")


class Poster(Base):
    """Imagem do pôster de uma obra, armazenada no próprio banco (1:1 com obras)."""

    __tablename__ = "posters"
    __table_args__ = (
        CheckConstraint(f"tipo_mime IN {TIPOS_MIME_PERMITIDOS}", name="tipo_mime_permitido"),
        CheckConstraint(
            f"tamanho_bytes > 0 AND tamanho_bytes <= {TAMANHO_MAXIMO_BYTES}",
            name="tamanho_permitido",
        ),
    )

    obra_id: Mapped[int] = mapped_column(
        ForeignKey("obras.id", ondelete="CASCADE"), primary_key=True
    )
    # Carregado apenas quando acessado, para não trafegar a imagem em consultas de obras.
    conteudo: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    tipo_mime: Mapped[str] = mapped_column(String(20))
    tamanho_bytes: Mapped[int] = mapped_column(Integer)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    obra: Mapped["Obra"] = relationship(back_populates="poster")

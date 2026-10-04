from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, ComDatas

if TYPE_CHECKING:
    from app.models.usuario import Usuario

CONTEUDO_TAMANHO_MAXIMO = 2000
NOTA_MINIMA = 1
NOTA_MAXIMA = 5


class Comentario(ComDatas, Base):
    """Comentário público de um usuário sobre um filme (identificado pelo tmdb_id)."""

    __tablename__ = "comentarios"
    __table_args__ = (
        CheckConstraint("tmdb_id > 0", name="tmdb_id_positivo"),
        CheckConstraint("length(trim(conteudo)) > 0", name="conteudo_nao_vazio"),
        CheckConstraint(
            f"nota IS NULL OR nota BETWEEN {NOTA_MINIMA} AND {NOTA_MAXIMA}", name="nota_valida"
        ),
        # Otimiza a listagem paginada mais recente-primeiro de um filme.
        Index("ix_comentarios_tmdb_criado", "tmdb_id", "criado_em"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    tmdb_id: Mapped[int] = mapped_column(Integer)
    conteudo: Mapped[str] = mapped_column(String(CONTEUDO_TAMANHO_MAXIMO))
    # Nota pessoal (1 a 5) opcional, exibida junto do comentário na listagem pública.
    nota: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    # Exclusão lógica: preserva o registro para uma futura moderação.
    removido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    usuario: Mapped["Usuario"] = relationship(back_populates="comentarios")

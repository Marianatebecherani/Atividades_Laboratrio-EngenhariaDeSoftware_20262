from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, ComDatas
from app.models.enums import StatusLista
from app.models.tipos import enum_como_texto

if TYPE_CHECKING:
    from app.models.obra import Obra
    from app.models.usuario import Usuario


class ItemLista(ComDatas, Base):
    """Obra na lista pessoal do usuário, com o status de acompanhamento."""

    __tablename__ = "itens_lista"
    __table_args__ = (
        UniqueConstraint("usuario_id", "obra_id", name="uq_itens_lista_usuario_obra"),
        Index("ix_itens_lista_usuario_status", "usuario_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id", ondelete="CASCADE"), index=True)
    status: Mapped[StatusLista] = mapped_column(enum_como_texto(StatusLista, "status_lista"))

    usuario: Mapped["Usuario"] = relationship(back_populates="itens_lista")
    obra: Mapped["Obra"] = relationship(back_populates="itens_lista")

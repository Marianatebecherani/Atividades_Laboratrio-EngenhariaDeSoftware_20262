from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, ComDatas
from app.models.enums import PapelUsuario
from app.models.tipos import enum_como_texto

if TYPE_CHECKING:
    from app.models.avaliacao import Avaliacao
    from app.models.item_lista import ItemLista


class Usuario(ComDatas, Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    papel: Mapped[PapelUsuario] = mapped_column(
        enum_como_texto(PapelUsuario, "papel_usuario"), default=PapelUsuario.USUARIO
    )

    itens_lista: Mapped[list["ItemLista"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )
    avaliacoes: Mapped[list["Avaliacao"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import COLLATION_PT_BR, Base
from app.models.obra_genero import obras_generos

if TYPE_CHECKING:
    from app.models.obra import Obra


class Genero(Base):
    __tablename__ = "generos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50, collation=COLLATION_PT_BR), unique=True)

    obras: Mapped[list["Obra"]] = relationship(
        secondary=obras_generos, back_populates="generos", passive_deletes=True
    )

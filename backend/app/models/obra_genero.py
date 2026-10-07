from sqlalchemy import Column, ForeignKey, Index, Table

from app.db.base import Base

# Associação N:N entre obras e gêneros.
# Excluir a obra remove as associações; excluir um gênero em uso é bloqueado (RESTRICT).
obras_generos = Table(
    "obras_generos",
    Base.metadata,
    Column("obra_id", ForeignKey("obras.id", ondelete="CASCADE"), primary_key=True),
    Column("genero_id", ForeignKey("generos.id", ondelete="RESTRICT"), primary_key=True),
    Index("ix_obras_generos_genero_id", "genero_id"),
)

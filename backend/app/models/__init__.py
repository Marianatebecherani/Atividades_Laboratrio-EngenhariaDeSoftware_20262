"""Modelos ORM. Importados aqui para que o Alembic e o SQLAlchemy conheçam todas as tabelas."""

from app.models.avaliacao import Avaliacao
from app.models.comentario import Comentario
from app.models.enums import PapelUsuario, StatusLista
from app.models.favorito import Favorito
from app.models.item_lista import ItemLista
from app.models.usuario import Usuario

__all__ = [
    "Avaliacao",
    "Comentario",
    "Favorito",
    "ItemLista",
    "PapelUsuario",
    "StatusLista",
    "Usuario",
]

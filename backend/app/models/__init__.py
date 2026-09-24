"""Modelos ORM. Importados aqui para que o Alembic e o SQLAlchemy conheçam todas as tabelas."""

from app.models.avaliacao import Avaliacao
from app.models.enums import PapelUsuario, StatusLista, TipoObra
from app.models.genero import Genero
from app.models.item_lista import ItemLista
from app.models.obra import Obra
from app.models.obra_genero import obras_generos
from app.models.poster import Poster
from app.models.usuario import Usuario

__all__ = [
    "Avaliacao",
    "Genero",
    "ItemLista",
    "Obra",
    "PapelUsuario",
    "Poster",
    "StatusLista",
    "TipoObra",
    "Usuario",
    "obras_generos",
]

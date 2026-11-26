from pydantic import BaseModel, Field

from app.models import StatusLista
from app.schemas.paginacao import Paginacao


class ItemListaEntrada(BaseModel):
    status: StatusLista


class FiltroFilmesUsuario(Paginacao):
    """Paginação da lista pessoal, com filtro opcional pela situação do filme."""

    status: StatusLista | None = Field(
        default=None, description="Mostra só os filmes da lista nesta situação"
    )

from datetime import datetime

from pydantic import BaseModel

from app.models import StatusLista
from app.schemas.obra import ObraResposta
from app.schemas.paginacao import Pagina, Paginacao


class ItemListaEntrada(BaseModel):
    status: StatusLista


class ItemListaResposta(BaseModel):
    obra: ObraResposta
    status: StatusLista
    criado_em: datetime
    atualizado_em: datetime


class PaginaItensLista(Pagina[ItemListaResposta]):
    pass


class FiltrosLista(Paginacao):
    status: StatusLista | None = None

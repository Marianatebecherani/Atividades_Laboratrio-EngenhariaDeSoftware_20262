from pydantic import BaseModel

from app.models import StatusLista


class ItemListaEntrada(BaseModel):
    status: StatusLista

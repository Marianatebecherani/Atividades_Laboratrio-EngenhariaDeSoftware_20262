from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.models.avaliacao import NOTA_MAXIMA, NOTA_MINIMA
from app.schemas.paginacao import Pagina
from app.schemas.validadores import texto_vazio_como_nulo

TAMANHO_MAXIMO_COMENTARIO = 2000


# O limite de tamanho vale só para o texto; comentário vazio vira nulo.
Comentario = Annotated[
    Annotated[str, Field(max_length=TAMANHO_MAXIMO_COMENTARIO)] | None,
    BeforeValidator(texto_vazio_como_nulo),
]


class AvaliacaoEntrada(BaseModel):
    nota: int = Field(ge=NOTA_MINIMA, le=NOTA_MAXIMA, description="Nota inteira de 1 a 5")
    comentario: Comentario = None


class AutorAvaliacao(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class AvaliacaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    obra_id: int
    usuario: AutorAvaliacao
    nota: int
    comentario: str | None
    criado_em: datetime
    atualizado_em: datetime


class PaginaAvaliacoes(Pagina[AvaliacaoResposta]):
    pass

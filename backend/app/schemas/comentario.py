from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.comentario import CONTEUDO_TAMANHO_MAXIMO


class ComentarioEntrada(BaseModel):
    """Corpo aceito ao criar ou editar um comentário. O autor nunca vem do cliente."""

    conteudo: str = Field(min_length=1, max_length=CONTEUDO_TAMANHO_MAXIMO)

    @field_validator("conteudo")
    @classmethod
    def validar_conteudo(cls, valor: str) -> str:
        texto = valor.strip()
        if not texto:
            raise ValueError("O comentário não pode ficar vazio")
        return texto


class ComentarioAutorResposta(BaseModel):
    """Dados públicos do autor, sem informações sensíveis (e-mail, papel etc.)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class ComentarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    usuario: ComentarioAutorResposta
    conteudo: str
    criado_em: datetime
    atualizado_em: datetime


class PaginaComentariosResposta(BaseModel):
    itens: list[ComentarioResposta]
    total: int = Field(ge=0)
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1)

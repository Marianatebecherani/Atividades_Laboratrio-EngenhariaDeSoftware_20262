from pydantic import BaseModel, Field

TAMANHO_PAGINA_PADRAO = 20
TAMANHO_PAGINA_MAXIMO = 100


class Paginacao(BaseModel):
    """Parâmetros de paginação comuns às listagens."""

    pagina: int = Field(default=1, ge=1)
    tamanho: int = Field(default=TAMANHO_PAGINA_PADRAO, ge=1, le=TAMANHO_PAGINA_MAXIMO)

    @property
    def deslocamento(self) -> int:
        return (self.pagina - 1) * self.tamanho


class Pagina[T](BaseModel):
    """Uma página de resultados e o total de itens encontrados."""

    itens: list[T]
    total: int
    pagina: int
    tamanho: int

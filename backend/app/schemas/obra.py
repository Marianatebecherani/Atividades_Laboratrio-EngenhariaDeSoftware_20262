from datetime import date
from enum import StrEnum
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models import TipoObra
from app.models.obra import ANO_LANCAMENTO_MINIMO, CLASSIFICACOES_INDICATIVAS
from app.schemas.genero import GeneroResposta

ANOS_FUTUROS_PERMITIDOS = 5
TAMANHO_PAGINA_PADRAO = 20
TAMANHO_PAGINA_MAXIMO = 100


def _texto_vazio_como_nulo(valor: object) -> object:
    if isinstance(valor, str):
        return valor.strip() or None
    return valor


Titulo = Annotated[str, AfterValidator(str.strip), Field(min_length=1, max_length=200)]
Sinopse = Annotated[str | None, BeforeValidator(_texto_vazio_como_nulo)]
Positivo = Annotated[int, Field(gt=0, le=32767)]


class ObraEntrada(BaseModel):
    """Dados completos de uma obra, usados no cadastro e na atualização."""

    titulo: Titulo
    tipo: TipoObra
    ano_lancamento: int
    sinopse: Sinopse = None
    classificacao_indicativa: int | None = Field(
        default=None, description="0 (livre), 10, 12, 14, 16, 18 ou nulo (não classificada)"
    )
    duracao_minutos: Positivo | None = Field(default=None, description="Obrigatória para filmes")
    temporadas: Positivo | None = Field(default=None, description="Obrigatória para séries")
    generos_ids: list[int] = Field(default_factory=list)

    @field_validator("ano_lancamento")
    @classmethod
    def validar_ano(cls, ano: int) -> int:
        limite = date.today().year + ANOS_FUTUROS_PERMITIDOS
        if not ANO_LANCAMENTO_MINIMO <= ano <= limite:
            raise ValueError(f"O ano deve estar entre {ANO_LANCAMENTO_MINIMO} e {limite}")
        return ano

    @field_validator("classificacao_indicativa")
    @classmethod
    def validar_classificacao(cls, valor: int | None) -> int | None:
        if valor is not None and valor not in CLASSIFICACOES_INDICATIVAS:
            raise ValueError(f"Use um destes valores: {CLASSIFICACOES_INDICATIVAS}")
        return valor

    @field_validator("generos_ids")
    @classmethod
    def remover_generos_repetidos(cls, ids: list[int]) -> list[int]:
        return list(dict.fromkeys(ids))

    @model_validator(mode="after")
    def validar_duracao_conforme_tipo(self) -> "ObraEntrada":
        if self.tipo == TipoObra.FILME and (self.duracao_minutos is None or self.temporadas):
            raise ValueError("Filmes exigem duracao_minutos e não possuem temporadas")
        if self.tipo == TipoObra.SERIE and (self.temporadas is None or self.duracao_minutos):
            raise ValueError("Séries exigem temporadas e não possuem duracao_minutos")
        return self


class ObraResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    tipo: TipoObra
    ano_lancamento: int
    sinopse: str | None
    classificacao_indicativa: int | None
    duracao_minutos: int | None
    temporadas: int | None
    generos: list[GeneroResposta]
    media_notas: float | None = Field(description="Média das notas, com uma casa decimal")
    total_avaliacoes: int
    url_poster: str | None = Field(description="Caminho do pôster na API, ou nulo se não houver")


class PaginaObras(BaseModel):
    itens: list[ObraResposta]
    total: int
    pagina: int
    tamanho: int


class OrdenacaoObras(StrEnum):
    MEDIA = "media"
    TITULO = "titulo"
    ANO_LANCAMENTO = "ano_lancamento"


class Direcao(StrEnum):
    ASC = "asc"
    DESC = "desc"


class FiltrosObras(BaseModel):
    """Parâmetros de busca, filtro, ordenação e paginação de obras."""

    texto: str | None = Field(default=None, description="Parte do título")
    tipo: TipoObra | None = None
    generos: list[int] = Field(
        default_factory=list, description="Obras com qualquer um dos gêneros"
    )
    ano_de: int | None = Field(default=None, description="Ano de lançamento mínimo")
    ano_ate: int | None = Field(default=None, description="Ano de lançamento máximo")
    nota_minima: float | None = Field(default=None, ge=1, le=5, description="Média mínima")
    classificacoes: list[int] = Field(
        default_factory=list, description="Classificações indicativas aceitas"
    )
    ordenar_por: OrdenacaoObras = OrdenacaoObras.MEDIA
    direcao: Direcao | None = Field(
        default=None, description="Padrão: crescente para título e decrescente para os demais"
    )
    pagina: int = Field(default=1, ge=1)
    tamanho: int = Field(default=TAMANHO_PAGINA_PADRAO, ge=1, le=TAMANHO_PAGINA_MAXIMO)

    @property
    def direcao_efetiva(self) -> Direcao:
        if self.direcao is not None:
            return self.direcao
        return Direcao.ASC if self.ordenar_por == OrdenacaoObras.TITULO else Direcao.DESC

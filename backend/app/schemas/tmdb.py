from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import StatusLista


class GeneroTmdbResposta(BaseModel):
    id: int = Field(gt=0)
    nome: str


class PessoaElencoTmdbResposta(BaseModel):
    tmdb_id: int
    nome: str
    personagem: str | None = None
    perfil_url: str | None = None


class PessoaEquipeTmdbResposta(BaseModel):
    tmdb_id: int
    nome: str
    departamento: str | None = None
    funcao: str | None = None
    perfil_url: str | None = None


class FilmeTmdbResposta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tmdb_id: int = Field(gt=0)
    titulo: str
    titulo_original: str
    sinopse: str | None = None
    data_lancamento: date | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    idioma_original: str | None = None
    nota_tmdb: float | None = None
    quantidade_votos: int = 0
    popularidade: float | None = None
    genero_ids: list[int] = Field(default_factory=list)
    poster_url: str | None = None
    backdrop_url: str | None = None
    elenco: list[PessoaElencoTmdbResposta] = Field(default_factory=list)
    diretor: str | None = None
    equipe_principal: list[PessoaEquipeTmdbResposta] = Field(default_factory=list)


class BuscaFilmesTmdbResposta(BaseModel):
    pagina: int = Field(ge=1)
    total_paginas: int = Field(ge=0)
    total_resultados: int = Field(ge=0)
    resultados: list[FilmeTmdbResposta]


OrdenacaoDiscoverTmdb = Literal[
    "popularity.desc",
    "popularity.asc",
    "vote_average.desc",
    "vote_average.asc",
    "primary_release_date.desc",
    "primary_release_date.asc",
    "title.asc",
    "title.desc",
]


class DescobrirFilmesParametros(BaseModel):
    """Filtros internos de Discover, limitados aos parâmetros suportados pelo TMDb."""

    page: int = Field(default=1, ge=1, le=500)
    genre_id: int | None = Field(default=None, gt=0)
    genre_ids: list[int] = Field(default_factory=list)
    genre_operator: Literal["AND", "OR"] = "AND"
    year: int | None = Field(default=None, ge=1870, le=2100)
    release_date_from: date | None = None
    release_date_to: date | None = None
    min_rating: float | None = Field(default=None, ge=0, le=10)
    max_rating: float | None = Field(default=None, ge=0, le=10)
    language: str = Field(default="pt-BR", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    sort_by: OrdenacaoDiscoverTmdb = "popularity.desc"

    # Previous version's public names remain accepted for compatibility.
    release_date_gte: date | None = None
    release_date_lte: date | None = None
    vote_average_gte: float | None = Field(default=None, ge=0, le=10)

    @field_validator("genre_ids", mode="before")
    @classmethod
    def parse_genre_ids(cls, valor: object) -> list[int]:
        if valor is None or valor == "":
            return []
        entradas = valor if isinstance(valor, list) else [valor]
        ids = []
        for entrada in entradas:
            for parte in str(entrada).split(","):
                parte = parte.strip()
                if parte:
                    try:
                        ids.append(int(parte))
                    except ValueError as erro:
                        raise ValueError(
                            "genre_ids deve conter IDs inteiros separados por vírgula"
                        ) from erro
        return list(dict.fromkeys(ids))

    @model_validator(mode="after")
    def validar_filtros(self) -> "DescobrirFilmesParametros":
        if self.genre_id is not None and self.genre_ids:
            raise ValueError("Use genre_id ou genre_ids, não ambos")
        if any(genre_id <= 0 for genre_id in self.genre_ids):
            raise ValueError("Todos os IDs de gênero devem ser positivos")
        if self.min_rating is not None and self.vote_average_gte is not None:
            raise ValueError("Use min_rating ou vote_average_gte, não ambos")
        nota_minima = self.min_rating if self.min_rating is not None else self.vote_average_gte
        if (
            self.max_rating is not None
            and nota_minima is not None
            and nota_minima > self.max_rating
        ):
            raise ValueError("min_rating deve ser menor ou igual a max_rating")
        data_de = self.release_date_from or self.release_date_gte
        data_ate = self.release_date_to or self.release_date_lte
        if self.release_date_from and self.release_date_gte:
            raise ValueError("Informe apenas um parâmetro de data inicial")
        if self.release_date_to and self.release_date_lte:
            raise ValueError("Informe apenas um parâmetro de data final")
        if data_de and data_ate and data_de > data_ate:
            raise ValueError("release_date_from deve ser anterior a release_date_to")
        return self

    @property
    def genero_ids_efetivos(self) -> list[int]:
        if self.genre_ids:
            return self.genre_ids
        return [self.genre_id] if self.genre_id is not None else []

    @property
    def data_de_efetiva(self) -> date | None:
        return self.release_date_from or self.release_date_gte

    @property
    def data_ate_efetiva(self) -> date | None:
        return self.release_date_to or self.release_date_lte

    @property
    def nota_minima_efetiva(self) -> float | None:
        return self.min_rating if self.min_rating is not None else self.vote_average_gte


class AvaliacaoTmdbEntrada(BaseModel):
    nota: int = Field(ge=1, le=5, description="Nota pessoal de 1 a 5, separada da nota TMDb")
    comentario: str | None = Field(default=None, max_length=2000)


class EstadoFilmeTmdbResposta(BaseModel):
    tmdb_id: int
    status: StatusLista | None = None
    nota_pessoal: int | None = None
    comentario: str | None = None
    favorito: bool = False
    atualizado_em: datetime | None = None


class FavoritoTmdbResposta(BaseModel):
    tmdb_id: int
    criado_em: datetime


class PaginaFavoritosTmdbResposta(BaseModel):
    itens: list[FavoritoTmdbResposta]
    total: int = Field(ge=0)
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1)


class PaginaEstadoFilmesTmdbResposta(BaseModel):
    itens: list[EstadoFilmeTmdbResposta]
    total: int = Field(ge=0)
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1)

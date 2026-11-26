"""Contrato do motor de recomendações (padrão Strategy).

Cada estratégia implementa `EstrategiaRecomendacao.recomendar` com um critério próprio.
O `RecomendacaoService` escolhe a estratégia em tempo de execução, sem conhecer os
detalhes de cada uma.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from app.models.enums import NomeEstrategia
from app.schemas.tmdb import FilmeTmdbResposta
from app.services.tmdb_service import TmdbService


@dataclass(frozen=True)
class ContextoRecomendacao:
    """Dados do usuário compartilhados por todas as estratégias.

    - `notas`: nota pessoal (1 a 5) de cada filme avaliado, pelo ID do TMDb.
    - `filmes_excluidos`: filmes que não devem ser recomendados (avaliados ou assistidos).
    - `limite`: quantidade máxima de filmes recomendados.
    """

    notas: dict[int, int]
    filmes_excluidos: frozenset[int]
    limite: int


@dataclass(frozen=True)
class Recomendacao:
    """Filme recomendado e o motivo, em linguagem simples, para exibir ao usuário."""

    filme: FilmeTmdbResposta
    motivo: str


class EstrategiaRecomendacao(ABC):
    """Interface comum das estratégias de recomendação."""

    nome: ClassVar[NomeEstrategia]

    def __init__(self, tmdb: TmdbService) -> None:
        self.tmdb = tmdb

    @abstractmethod
    async def recomendar(self, contexto: ContextoRecomendacao) -> list[Recomendacao]:
        """Retorna até `contexto.limite` recomendações, da mais para a menos relevante."""

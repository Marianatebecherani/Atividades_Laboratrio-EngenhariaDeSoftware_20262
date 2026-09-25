"""Contrato do motor de recomendações (padrão Strategy).

Cada estratégia implementa `EstrategiaRecomendacao.recomendar` com um critério próprio.
O serviço escolhe a estratégia em tempo de execução, sem conhecer os detalhes de cada uma.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from app.repositories.recomendacao_repository import RecomendacaoRepository


class NomeEstrategia(StrEnum):
    GENEROS = "generos"
    SIMILARES = "similares"
    POPULARES = "populares"


@dataclass(frozen=True)
class ContextoRecomendacao:
    """Dados do pedido de recomendação compartilhados por todas as estratégias."""

    usuario_id: int
    obras_excluidas: frozenset[int]
    limite: int


@dataclass(frozen=True)
class Recomendacao:
    obra_id: int
    pontuacao: float
    motivo: str


class EstrategiaRecomendacao(ABC):
    """Interface comum das estratégias de recomendação."""

    nome: ClassVar[NomeEstrategia]

    def __init__(self, repositorio: RecomendacaoRepository) -> None:
        self.repositorio = repositorio

    @abstractmethod
    def recomendar(self, contexto: ContextoRecomendacao) -> list[Recomendacao]:
        """Retorna até `contexto.limite` recomendações, da mais para a menos relevante."""

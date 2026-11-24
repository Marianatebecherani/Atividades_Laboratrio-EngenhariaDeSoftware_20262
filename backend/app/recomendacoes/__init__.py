"""Motor de recomendações com o padrão Strategy."""

from app.recomendacoes.base import ContextoRecomendacao, EstrategiaRecomendacao, Recomendacao
from app.recomendacoes.perfil import EstrategiaPerfil
from app.recomendacoes.populares import EstrategiaPopulares
from app.recomendacoes.similares import EstrategiaSimilares

__all__ = [
    "ContextoRecomendacao",
    "EstrategiaPerfil",
    "EstrategiaPopulares",
    "EstrategiaRecomendacao",
    "EstrategiaSimilares",
    "Recomendacao",
]

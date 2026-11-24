"""Motor de recomendações com o padrão Strategy."""

from app.recomendacoes.base import ContextoRecomendacao, EstrategiaRecomendacao
from app.recomendacoes.perfil import EstrategiaPerfil

__all__ = ["ContextoRecomendacao", "EstrategiaPerfil", "EstrategiaRecomendacao"]

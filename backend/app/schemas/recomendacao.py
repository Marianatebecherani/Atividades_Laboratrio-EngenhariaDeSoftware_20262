from pydantic import BaseModel, Field

from app.recomendacoes.base import NomeEstrategia
from app.schemas.obra import ObraResposta

LIMITE_PADRAO = 10
LIMITE_MAXIMO = 50


class ParametrosRecomendacao(BaseModel):
    estrategia: NomeEstrategia | None = Field(
        default=None,
        description="Padrão: `generos`. Sem histórico suficiente, usa `populares`.",
    )
    limite: int = Field(default=LIMITE_PADRAO, ge=1, le=LIMITE_MAXIMO)


class RecomendacaoResposta(BaseModel):
    obra: ObraResposta
    pontuacao: float = Field(description="Relevância relativa entre 0 e 1")
    motivo: str


class RecomendacoesResposta(BaseModel):
    estrategia: NomeEstrategia = Field(description="Estratégia efetivamente usada")
    itens: list[RecomendacaoResposta]
    tempo_ms: float = Field(description="Tempo de cálculo das recomendações, em milissegundos")

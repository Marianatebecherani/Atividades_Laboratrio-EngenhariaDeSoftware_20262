from dataclasses import dataclass
from time import perf_counter

from sqlalchemy.orm import Session

from app.models import Usuario
from app.recomendacoes.base import ContextoRecomendacao, NomeEstrategia, Recomendacao
from app.recomendacoes.estrategias import ESTRATEGIAS
from app.repositories.obra_repository import ObraComResumo, ObraRepository
from app.repositories.recomendacao_repository import RecomendacaoRepository

ESTRATEGIA_PADRAO = NomeEstrategia.GENEROS
ESTRATEGIA_RESERVA = NomeEstrategia.POPULARES


@dataclass(frozen=True)
class ResultadoRecomendacao:
    estrategia: NomeEstrategia
    itens: list[tuple[Recomendacao, ObraComResumo]]
    tempo_ms: float


class RecomendacaoService:
    """Seleciona a estratégia de recomendação e monta o resultado com os dados das obras."""

    def __init__(self, sessao: Session) -> None:
        self.repositorio = RecomendacaoRepository(sessao)
        self.obras = ObraRepository(sessao)

    def recomendar(
        self, usuario: Usuario, estrategia: NomeEstrategia | None, limite: int
    ) -> ResultadoRecomendacao:
        inicio = perf_counter()
        contexto = ContextoRecomendacao(
            usuario_id=usuario.id,
            obras_excluidas=frozenset(self.repositorio.obras_do_historico(usuario.id)),
            limite=limite,
        )

        nome = estrategia or ESTRATEGIA_PADRAO
        recomendacoes = ESTRATEGIAS[nome](self.repositorio).recomendar(contexto)
        if not recomendacoes and nome != ESTRATEGIA_RESERVA:
            # Sem histórico suficiente para a estratégia escolhida: usa a popularidade.
            nome = ESTRATEGIA_RESERVA
            recomendacoes = ESTRATEGIAS[nome](self.repositorio).recomendar(contexto)

        obras = self.obras.obter_varias_com_resumo([r.obra_id for r in recomendacoes])
        itens = [(r, obras[r.obra_id]) for r in recomendacoes]
        tempo_ms = round((perf_counter() - inicio) * 1000, 1)
        return ResultadoRecomendacao(estrategia=nome, itens=itens, tempo_ms=tempo_ms)

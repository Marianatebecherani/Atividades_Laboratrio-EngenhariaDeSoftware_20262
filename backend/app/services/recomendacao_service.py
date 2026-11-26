from time import perf_counter

from sqlalchemy.orm import Session

from app.models import StatusLista
from app.models.enums import NomeEstrategia
from app.recomendacoes import (
    ContextoRecomendacao,
    EstrategiaPerfil,
    EstrategiaPopulares,
    EstrategiaRecomendacao,
    EstrategiaSimilares,
)
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.comentario_repository import ComentarioRepository
from app.repositories.item_lista_repository import ItemListaRepository
from app.schemas.tmdb import FilmeRecomendadoResposta, RecomendacoesTmdbResposta
from app.services.tmdb_service import TmdbService


class RecomendacaoService:
    """Monta o contexto do usuário e delega o cálculo à estratégia escolhida (Strategy)."""

    # Não depende do histórico do usuário, por isso serve de reserva para as demais.
    ESTRATEGIA_RESERVA = NomeEstrategia.POPULARES

    def __init__(self, sessao: Session, tmdb: TmdbService) -> None:
        self.avaliacoes = AvaliacaoRepository(sessao)
        self.comentarios = ComentarioRepository(sessao)
        self.lista = ItemListaRepository(sessao)
        self.estrategias: dict[NomeEstrategia, EstrategiaRecomendacao] = {
            estrategia.nome: estrategia
            for estrategia in (
                EstrategiaPerfil(tmdb),
                EstrategiaSimilares(tmdb),
                EstrategiaPopulares(tmdb),
            )
        }

    async def recomendar(
        self,
        usuario_id: int,
        estrategia: NomeEstrategia = NomeEstrategia.PERFIL,
        limite: int = 10,
    ) -> RecomendacoesTmdbResposta:
        inicio = perf_counter()
        contexto = self._montar_contexto(usuario_id, limite)
        recomendacoes = await self.estrategias[estrategia].recomendar(contexto)

        # Sem resultados (por exemplo, usuário sem avaliações), usa a estratégia de reserva.
        if not recomendacoes and estrategia != self.ESTRATEGIA_RESERVA:
            estrategia = self.ESTRATEGIA_RESERVA
            recomendacoes = await self.estrategias[estrategia].recomendar(contexto)

        itens = [
            FilmeRecomendadoResposta(**item.filme.model_dump(), motivo=item.motivo)
            for item in recomendacoes
        ]
        return RecomendacoesTmdbResposta(
            estrategia=estrategia,
            itens=itens,
            total=len(itens),
            tempo_ms=round((perf_counter() - inicio) * 1000),
        )

    def _montar_contexto(self, usuario_id: int, limite: int) -> ContextoRecomendacao:
        notas: dict[int, int] = {
            avaliacao.tmdb_id: avaliacao.nota
            for avaliacao in self.avaliacoes.listar_tmdb(usuario_id)
        }

        # O comentário público mais recente prevalece sobre a avaliação privada.
        comentarios_processados: set[int] = set()

        for comentario in self.comentarios.listar_por_usuario(usuario_id):
            if comentario.tmdb_id in comentarios_processados:
                continue

            comentarios_processados.add(comentario.tmdb_id)

            if comentario.nota is not None:
                notas[comentario.tmdb_id] = comentario.nota

        filmes_assistidos = {
            item.tmdb_id
            for item in self.lista.listar_tmdb(usuario_id)
            if item.status == StatusLista.ASSISTIDO
        }

        return ContextoRecomendacao(
            notas=notas,
            filmes_excluidos=frozenset(notas) | filmes_assistidos,
            limite=limite,
        )

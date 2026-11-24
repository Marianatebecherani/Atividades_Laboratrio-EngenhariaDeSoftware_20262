from sqlalchemy.orm import Session

from app.models import StatusLista
from app.models.enums import NomeEstrategia
from app.recomendacoes import ContextoRecomendacao, EstrategiaPerfil, EstrategiaRecomendacao
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.comentario_repository import ComentarioRepository
from app.repositories.item_lista_repository import ItemListaRepository
from app.schemas.tmdb import RecomendacoesTmdbResposta
from app.services.tmdb_service import TmdbService


class RecomendacaoService:
    """Monta o contexto do usuário e delega o cálculo à estratégia escolhida (Strategy)."""

    def __init__(self, sessao: Session, tmdb: TmdbService) -> None:
        self.avaliacoes = AvaliacaoRepository(sessao)
        self.comentarios = ComentarioRepository(sessao)
        self.lista = ItemListaRepository(sessao)
        self.estrategias: dict[NomeEstrategia, EstrategiaRecomendacao] = {
            estrategia.nome: estrategia for estrategia in (EstrategiaPerfil(tmdb),)
        }

    async def recomendar(
        self,
        usuario_id: int,
        limite: int = 10,
    ) -> RecomendacoesTmdbResposta:
        contexto = self._montar_contexto(usuario_id, limite)
        filmes = await self.estrategias[NomeEstrategia.PERFIL].recomendar(contexto)

        return RecomendacoesTmdbResposta(itens=filmes, total=len(filmes))

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

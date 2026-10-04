from sqlalchemy.orm import Session

from app.core.excecoes import OperacaoNaoPermitida, RecursoNaoEncontrado
from app.models import Comentario
from app.repositories.comentario_repository import ComentarioRepository
from app.schemas.comentario import ComentarioEntrada, ComentarioResposta, PaginaComentariosResposta
from app.schemas.paginacao import Paginacao


class ComentarioService:
    """Comentários públicos de usuários sobre filmes TMDb."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = ComentarioRepository(sessao)

    def listar(self, tmdb_id: int, paginacao: Paginacao) -> PaginaComentariosResposta:
        itens, total = self.repositorio.listar_por_tmdb(
            tmdb_id, paginacao.deslocamento, paginacao.tamanho
        )
        return PaginaComentariosResposta(
            itens=[ComentarioResposta.model_validate(item) for item in itens],
            total=total,
            pagina=paginacao.pagina,
            tamanho=paginacao.tamanho,
        )

    def criar(self, usuario_id: int, tmdb_id: int, dados: ComentarioEntrada) -> ComentarioResposta:
        comentario = self.repositorio.criar(usuario_id, tmdb_id, dados.conteudo)
        self.sessao.commit()
        self.sessao.refresh(comentario)
        return ComentarioResposta.model_validate(comentario)

    def _obter_proprio(self, usuario_id: int, comentario_id: int) -> Comentario:
        comentario = self.repositorio.obter_por_id(comentario_id)
        if comentario is None:
            raise RecursoNaoEncontrado("Comentário não encontrado")
        if comentario.usuario_id != usuario_id:
            raise OperacaoNaoPermitida("Você só pode alterar seus próprios comentários")
        return comentario

    def atualizar(
        self, usuario_id: int, comentario_id: int, dados: ComentarioEntrada
    ) -> ComentarioResposta:
        comentario = self._obter_proprio(usuario_id, comentario_id)
        comentario = self.repositorio.atualizar(comentario, dados.conteudo)
        self.sessao.commit()
        self.sessao.refresh(comentario)
        return ComentarioResposta.model_validate(comentario)

    def remover(self, usuario_id: int, comentario_id: int) -> None:
        comentario = self._obter_proprio(usuario_id, comentario_id)
        self.repositorio.remover(comentario)
        self.sessao.commit()

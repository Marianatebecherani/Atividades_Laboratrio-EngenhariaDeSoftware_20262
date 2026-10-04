from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Comentario


class ComentarioRepository:
    """Acesso aos dados de comentários públicos (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def _condicao_ativo(self):
        return Comentario.removido_em.is_(None)

    def listar_por_tmdb(
        self, tmdb_id: int, deslocamento: int, tamanho: int
    ) -> tuple[Sequence[Comentario], int]:
        condicao = (Comentario.tmdb_id == tmdb_id) & self._condicao_ativo()
        total = self.sessao.scalar(select(func.count()).select_from(Comentario).where(condicao))
        itens = self.sessao.scalars(
            select(Comentario)
            # Eager loading evita N+1 ao montar o autor de cada comentário.
            .options(joinedload(Comentario.usuario))
            .where(condicao)
            .order_by(Comentario.criado_em.desc(), Comentario.id.desc())
            .offset(deslocamento)
            .limit(tamanho)
        ).all()
        return itens, total

    def obter_por_id(self, comentario_id: int) -> Comentario | None:
        return self.sessao.scalar(
            select(Comentario)
            .options(joinedload(Comentario.usuario))
            .where(Comentario.id == comentario_id, self._condicao_ativo())
        )

    def obter_por_usuario_e_filme(self, usuario_id: int, tmdb_id: int) -> Comentario | None:
        """Último comentário ativo do usuário nesse filme (usado pela UI de "minha avaliação")."""
        condicao = (
            (Comentario.usuario_id == usuario_id)
            & (Comentario.tmdb_id == tmdb_id)
            & self._condicao_ativo()
        )
        return self.sessao.scalar(
            select(Comentario)
            .options(joinedload(Comentario.usuario))
            .where(condicao)
            .order_by(Comentario.criado_em.desc(), Comentario.id.desc())
        )

    def listar_por_usuario(self, usuario_id: int) -> Sequence[Comentario]:
        """Comentários ativos do usuário em todos os filmes (um por filme, o mais recente)."""
        condicao = (Comentario.usuario_id == usuario_id) & self._condicao_ativo()
        return self.sessao.scalars(
            select(Comentario)
            .where(condicao)
            .order_by(Comentario.tmdb_id, Comentario.criado_em.desc(), Comentario.id.desc())
        ).all()

    def criar(
        self, usuario_id: int, tmdb_id: int, conteudo: str, nota: int | None = None
    ) -> Comentario:
        comentario = Comentario(
            usuario_id=usuario_id, tmdb_id=tmdb_id, conteudo=conteudo, nota=nota
        )
        self.sessao.add(comentario)
        self.sessao.flush()
        return comentario

    def atualizar(
        self, comentario: Comentario, conteudo: str, nota: int | None = None
    ) -> Comentario:
        comentario.conteudo = conteudo
        comentario.nota = nota
        self.sessao.flush()
        return comentario

    def remover(self, comentario: Comentario) -> None:
        comentario.removido_em = datetime.now(UTC)
        self.sessao.flush()

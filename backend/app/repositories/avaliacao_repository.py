from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Avaliacao


class AvaliacaoRepository:
    """Acesso aos dados de avaliações (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def obter_tmdb(self, usuario_id: int, tmdb_id: int) -> Avaliacao | None:
        return self.sessao.scalar(
            select(Avaliacao).where(
                Avaliacao.usuario_id == usuario_id, Avaliacao.tmdb_id == tmdb_id
            )
        )

    def listar_tmdb(self, usuario_id: int) -> Sequence[Avaliacao]:
        return self.sessao.scalars(
            select(Avaliacao).where(
                Avaliacao.usuario_id == usuario_id, Avaliacao.tmdb_id.is_not(None)
            )
        ).all()

    def salvar_tmdb(
        self, usuario_id: int, tmdb_id: int, nota: int, comentario: str | None
    ) -> Avaliacao:
        avaliacao = self.obter_tmdb(usuario_id, tmdb_id)
        if avaliacao is None:
            avaliacao = Avaliacao(
                usuario_id=usuario_id,
                tmdb_id=tmdb_id,
                nota=nota,
                comentario=comentario,
            )
            self.sessao.add(avaliacao)
        else:
            avaliacao.nota = nota
            avaliacao.comentario = comentario
        self.sessao.flush()
        return avaliacao

    def remover_tmdb(self, usuario_id: int, tmdb_id: int) -> bool:
        avaliacao = self.obter_tmdb(usuario_id, tmdb_id)
        if avaliacao is None:
            return False
        self.sessao.delete(avaliacao)
        self.sessao.flush()
        return True

    def obter_por_id(self, avaliacao_id: int) -> Avaliacao | None:
        return self.sessao.get(Avaliacao, avaliacao_id)

    def remover(self, avaliacao: Avaliacao) -> None:
        self.sessao.delete(avaliacao)
        self.sessao.flush()

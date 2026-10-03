from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Favorito


class FavoritoRepository:
    """Acesso às referências de filmes favoritos mantidas por cada usuário."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def obter(self, usuario_id: int, tmdb_id: int) -> Favorito | None:
        return self.sessao.scalar(
            select(Favorito).where(Favorito.usuario_id == usuario_id, Favorito.tmdb_id == tmdb_id)
        )

    def listar(
        self, usuario_id: int, deslocamento: int, tamanho: int
    ) -> tuple[Sequence[Favorito], int]:
        condicao = Favorito.usuario_id == usuario_id
        total = self.sessao.scalar(select(func.count()).select_from(Favorito).where(condicao))
        itens = self.sessao.scalars(
            select(Favorito)
            .where(condicao)
            .order_by(Favorito.id.desc())
            .offset(deslocamento)
            .limit(tamanho)
        ).all()
        return itens, total

    def listar_todos(self, usuario_id: int) -> Sequence[Favorito]:
        return self.sessao.scalars(select(Favorito).where(Favorito.usuario_id == usuario_id)).all()

    def adicionar(self, usuario_id: int, tmdb_id: int) -> Favorito:
        favorito = Favorito(usuario_id=usuario_id, tmdb_id=tmdb_id)
        self.sessao.add(favorito)
        self.sessao.flush()
        return favorito

    def remover(self, favorito: Favorito) -> None:
        self.sessao.delete(favorito)
        self.sessao.flush()

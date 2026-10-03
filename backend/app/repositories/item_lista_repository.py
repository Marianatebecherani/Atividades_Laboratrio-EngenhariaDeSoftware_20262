from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ItemLista, StatusLista


class ItemListaRepository:
    """Acesso aos dados da lista pessoal de obras (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def obter_por_tmdb_id(self, usuario_id: int, tmdb_id: int) -> ItemLista | None:
        return self.sessao.scalar(
            select(ItemLista).where(
                ItemLista.usuario_id == usuario_id, ItemLista.tmdb_id == tmdb_id
            )
        )

    def salvar_tmdb(self, usuario_id: int, tmdb_id: int, status: StatusLista) -> ItemLista:
        item = self.obter_por_tmdb_id(usuario_id, tmdb_id)
        if item is None:
            item = ItemLista(usuario_id=usuario_id, tmdb_id=tmdb_id, status=status)
            self.sessao.add(item)
        else:
            item.status = status
        self.sessao.flush()
        return item

    def listar_tmdb(self, usuario_id: int) -> Sequence[ItemLista]:
        return self.sessao.scalars(
            select(ItemLista)
            .where(ItemLista.usuario_id == usuario_id)
            .order_by(ItemLista.atualizado_em.desc(), ItemLista.id.desc())
        ).all()

    def remover_tmdb(self, usuario_id: int, tmdb_id: int) -> bool:
        item = self.obter_por_tmdb_id(usuario_id, tmdb_id)
        if item is None:
            return False
        self.sessao.delete(item)
        self.sessao.flush()
        return True

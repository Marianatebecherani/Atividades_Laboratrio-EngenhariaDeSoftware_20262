from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ItemLista, StatusLista
from app.schemas.item_lista import FiltrosLista


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
            .where(ItemLista.usuario_id == usuario_id, ItemLista.tmdb_id.is_not(None))
            .order_by(ItemLista.atualizado_em.desc(), ItemLista.id.desc())
        ).all()

    def remover_tmdb(self, usuario_id: int, tmdb_id: int) -> bool:
        item = self.obter_por_tmdb_id(usuario_id, tmdb_id)
        if item is None:
            return False
        self.sessao.delete(item)
        self.sessao.flush()
        return True

    def obter(self, usuario_id: int, obra_id: int) -> ItemLista | None:
        consulta = select(ItemLista).where(
            ItemLista.usuario_id == usuario_id, ItemLista.obra_id == obra_id
        )
        return self.sessao.scalar(consulta)

    def listar(self, usuario_id: int, filtros: FiltrosLista) -> tuple[Sequence[ItemLista], int]:
        consulta = select(ItemLista).where(
            ItemLista.usuario_id == usuario_id, ItemLista.obra_id.is_not(None)
        )
        if filtros.status is not None:
            consulta = consulta.where(ItemLista.status == filtros.status)

        total = self.sessao.scalar(select(func.count()).select_from(consulta.subquery()))
        itens = self.sessao.scalars(
            consulta.order_by(ItemLista.atualizado_em.desc(), ItemLista.id.desc())
            .offset(filtros.deslocamento)
            .limit(filtros.tamanho)
        ).all()
        return itens, total

    def status_por_obra(self, usuario_id: int, obra_ids: list[int]) -> dict[int, StatusLista]:
        consulta = select(ItemLista.obra_id, ItemLista.status).where(
            ItemLista.usuario_id == usuario_id, ItemLista.obra_id.in_(obra_ids)
        )
        return dict(self.sessao.execute(consulta).tuples().all())

    def adicionar(self, item: ItemLista) -> ItemLista:
        self.sessao.add(item)
        self.sessao.flush()
        return item

    def remover(self, item: ItemLista) -> None:
        self.sessao.delete(item)
        self.sessao.flush()

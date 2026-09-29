from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.excecoes import RecursoNaoEncontrado
from app.models import ItemLista, StatusLista, Usuario
from app.repositories.item_lista_repository import ItemListaRepository
from app.repositories.obra_repository import ObraComResumo, ObraRepository
from app.schemas.item_lista import FiltrosLista


class ListaService:
    """Regras de negócio da lista pessoal (quero assistir, assistindo, assistido)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = ItemListaRepository(sessao)
        self.obras = ObraRepository(sessao)

    def listar(
        self, usuario: Usuario, filtros: FiltrosLista
    ) -> tuple[list[tuple[ItemLista, ObraComResumo]], int]:
        itens, total = self.repositorio.listar(usuario.id, filtros)
        return self._com_obras(itens), total

    def definir_status(
        self, usuario: Usuario, obra_id: int, status: StatusLista
    ) -> tuple[ItemLista, ObraComResumo, bool]:
        """Adiciona a obra à lista ou altera seu status. Indica se o item foi criado."""
        if self.obras.obter_por_id(obra_id) is None:
            raise RecursoNaoEncontrado("Obra não encontrada")

        item = self.repositorio.obter(usuario.id, obra_id)
        criado = item is None
        if criado:
            item = self.repositorio.adicionar(
                ItemLista(usuario_id=usuario.id, obra_id=obra_id, status=status)
            )
        else:
            item.status = status
        self.sessao.commit()
        self.sessao.refresh(item)
        return item, self.obras.obter_com_resumo(obra_id), criado

    def remover(self, usuario: Usuario, obra_id: int) -> None:
        item = self.repositorio.obter(usuario.id, obra_id)
        if item is None:
            raise RecursoNaoEncontrado("Obra não está na sua lista")
        self.repositorio.remover(item)
        self.sessao.commit()

    def status_por_obra(self, usuario: Usuario, obra_ids: list[int]) -> dict[int, StatusLista]:
        return self.repositorio.status_por_obra(usuario.id, obra_ids)

    def _com_obras(self, itens: Sequence[ItemLista]) -> list[tuple[ItemLista, ObraComResumo]]:
        obras = self.obras.obter_varias_com_resumo([item.obra_id for item in itens])
        return [(item, obras[item.obra_id]) for item in itens]

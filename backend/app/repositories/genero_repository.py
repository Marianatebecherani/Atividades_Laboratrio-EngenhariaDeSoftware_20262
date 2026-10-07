from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Genero, obras_generos


class GeneroRepository:
    """Acesso aos dados de gêneros (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def listar(self) -> Sequence[Genero]:
        return self.sessao.scalars(select(Genero).order_by(Genero.nome)).all()

    def obter_por_id(self, genero_id: int) -> Genero | None:
        return self.sessao.get(Genero, genero_id)

    def obter_por_ids(self, ids: Sequence[int]) -> Sequence[Genero]:
        return self.sessao.scalars(select(Genero).where(Genero.id.in_(ids))).all()

    def obter_por_nome(self, nome: str) -> Genero | None:
        """Busca ignorando maiúsculas e minúsculas."""
        consulta = select(Genero).where(func.lower(Genero.nome) == nome.lower())
        return self.sessao.scalar(consulta)

    def contar_obras(self, genero_id: int) -> int:
        consulta = select(func.count()).where(obras_generos.c.genero_id == genero_id)
        return self.sessao.scalar(consulta)

    def adicionar(self, genero: Genero) -> Genero:
        self.sessao.add(genero)
        self.sessao.flush()
        return genero

    def remover(self, genero: Genero) -> None:
        self.sessao.delete(genero)
        self.sessao.flush()

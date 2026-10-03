from collections import defaultdict
from collections.abc import Iterable

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Avaliacao, Genero, ItemLista, Obra, StatusLista, obras_generos


class RecomendacaoRepository:
    """Consultas usadas pelas estratégias de recomendação (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self._medias = (
            select(
                Avaliacao.obra_id,
                func.avg(Avaliacao.nota).label("media"),
                func.count().label("total"),
            )
            .group_by(Avaliacao.obra_id)
            .subquery("medias")
        )

    def obras_do_historico(self, usuario_id: int) -> set[int]:
        """Obras que o usuário já tem na lista (qualquer status) ou já avaliou."""
        na_lista = select(ItemLista.obra_id).where(
            ItemLista.usuario_id == usuario_id, ItemLista.obra_id.is_not(None)
        )
        avaliadas = select(Avaliacao.obra_id).where(
            Avaliacao.usuario_id == usuario_id, Avaliacao.obra_id.is_not(None)
        )
        return set(self.sessao.scalars(na_lista.union(avaliadas)))

    def notas_do_usuario(self, usuario_id: int) -> dict[int, int]:
        consulta = select(Avaliacao.obra_id, Avaliacao.nota).where(
            Avaliacao.usuario_id == usuario_id,
            Avaliacao.obra_id.is_not(None),
        )
        return dict(self.sessao.execute(consulta).tuples().all())

    def obras_assistidas(self, usuario_id: int) -> set[int]:
        consulta = select(ItemLista.obra_id).where(
            ItemLista.usuario_id == usuario_id,
            ItemLista.obra_id.is_not(None),
            ItemLista.status.in_([StatusLista.ASSISTIDO, StatusLista.ASSISTINDO]),
        )
        return set(self.sessao.scalars(consulta))

    def generos_das_obras(self, obra_ids: Iterable[int] | None = None) -> dict[int, set[int]]:
        """Gêneros de cada obra. Sem ids, retorna o mapa do catálogo inteiro."""
        consulta = select(obras_generos.c.obra_id, obras_generos.c.genero_id)
        if obra_ids is not None:
            consulta = consulta.where(obras_generos.c.obra_id.in_(list(obra_ids)))
        mapa: dict[int, set[int]] = defaultdict(set)
        for obra_id, genero_id in self.sessao.execute(consulta):
            mapa[obra_id].add(genero_id)
        return dict(mapa)

    def nomes_dos_generos(self, genero_ids: Iterable[int]) -> dict[int, str]:
        consulta = select(Genero.id, Genero.nome).where(Genero.id.in_(list(genero_ids)))
        return dict(self.sessao.execute(consulta).tuples().all())

    def titulos(self, obra_ids: Iterable[int]) -> dict[int, str]:
        consulta = select(Obra.id, Obra.titulo).where(Obra.id.in_(list(obra_ids)))
        return dict(self.sessao.execute(consulta).tuples().all())

    def medias(self, obra_ids: Iterable[int]) -> dict[int, float]:
        consulta = select(self._medias.c.obra_id, self._medias.c.media).where(
            self._medias.c.obra_id.in_(list(obra_ids))
        )
        return {obra_id: float(media) for obra_id, media in self.sessao.execute(consulta)}

    def afinidade_por_generos(
        self, pesos: dict[int, float], excluir: set[int], limite: int
    ) -> list[tuple[int, float]]:
        """Soma, para cada obra, os pesos dos seus gêneros. Desempata pela média de notas."""
        peso = case(pesos, value=obras_generos.c.genero_id, else_=0.0)
        afinidade = func.sum(peso).label("afinidade")
        consulta = (
            select(obras_generos.c.obra_id, afinidade)
            .outerjoin(self._medias, self._medias.c.obra_id == obras_generos.c.obra_id)
            .group_by(obras_generos.c.obra_id, self._medias.c.media)
            .having(afinidade > 0)
            .order_by(
                afinidade.desc(), self._medias.c.media.desc().nulls_last(), obras_generos.c.obra_id
            )
            .limit(limite)
        )
        if excluir:
            consulta = consulta.where(obras_generos.c.obra_id.not_in(excluir))
        return [(obra_id, float(valor)) for obra_id, valor in self.sessao.execute(consulta)]

    def mais_bem_avaliadas(
        self, excluir: set[int], limite: int
    ) -> list[tuple[int, float | None, int]]:
        """Obras por média de notas; as sem avaliação vêm depois, das mais recentes às antigas."""
        consulta = (
            select(Obra.id, self._medias.c.media, self._medias.c.total)
            .outerjoin(self._medias, self._medias.c.obra_id == Obra.id)
            .order_by(
                self._medias.c.media.desc().nulls_last(),
                self._medias.c.total.desc().nulls_last(),
                Obra.ano_lancamento.desc(),
                Obra.id,
            )
            .limit(limite)
        )
        if excluir:
            consulta = consulta.where(Obra.id.not_in(excluir))
        return [
            (obra_id, float(media) if media is not None else None, total or 0)
            for obra_id, media, total in self.sessao.execute(consulta)
        ]

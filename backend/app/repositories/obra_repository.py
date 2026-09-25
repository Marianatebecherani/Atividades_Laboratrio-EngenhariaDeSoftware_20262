from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Avaliacao, Obra, Poster, obras_generos
from app.schemas.obra import Direcao, FiltrosObras, OrdenacaoObras


@dataclass(frozen=True)
class ObraComResumo:
    """Obra acompanhada do resumo de suas avaliações."""

    obra: Obra
    media_notas: float | None
    total_avaliacoes: int


class ObraRepository:
    """Acesso aos dados de obras e pôsteres (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self._resumo = (
            select(
                Avaliacao.obra_id,
                func.avg(Avaliacao.nota).label("media"),
                func.count().label("total"),
            )
            .group_by(Avaliacao.obra_id)
            .subquery("resumo_avaliacoes")
        )

    def buscar(self, filtros: FiltrosObras) -> tuple[list[ObraComResumo], int]:
        consulta = self._consulta_com_resumo().where(*self._condicoes(filtros))

        total = self.sessao.scalar(select(func.count()).select_from(consulta.subquery()))

        pagina = self.sessao.execute(
            consulta.order_by(*self._ordenacao(filtros))
            .offset(filtros.deslocamento)
            .limit(filtros.tamanho)
        )
        return [self._montar(linha) for linha in pagina], total

    def obter_com_resumo(self, obra_id: int) -> ObraComResumo | None:
        linha = self.sessao.execute(self._consulta_com_resumo().where(Obra.id == obra_id)).first()
        return self._montar(linha) if linha else None

    def obter_varias_com_resumo(self, obra_ids: list[int]) -> dict[int, ObraComResumo]:
        linhas = self.sessao.execute(self._consulta_com_resumo().where(Obra.id.in_(obra_ids)))
        return {resultado.obra.id: resultado for resultado in map(self._montar, linhas)}

    def obter_por_id(self, obra_id: int) -> Obra | None:
        return self.sessao.get(Obra, obra_id)

    def obter_poster(self, obra_id: int) -> Poster | None:
        return self.sessao.get(Poster, obra_id)

    def adicionar(self, obra: Obra) -> Obra:
        self.sessao.add(obra)
        self.sessao.flush()
        return obra

    def remover(self, objeto: Obra | Poster) -> None:
        self.sessao.delete(objeto)
        self.sessao.flush()

    def _consulta_com_resumo(self) -> Select:
        return (
            select(Obra, self._resumo.c.media, self._resumo.c.total)
            .outerjoin(self._resumo, self._resumo.c.obra_id == Obra.id)
            .options(selectinload(Obra.generos), selectinload(Obra.poster))
        )

    def _condicoes(self, filtros: FiltrosObras) -> list:
        condicoes = []
        if filtros.texto and filtros.texto.strip():
            condicoes.append(Obra.titulo.icontains(filtros.texto.strip(), autoescape=True))
        if filtros.tipo is not None:
            condicoes.append(Obra.tipo == filtros.tipo)
        if filtros.generos:
            obras_do_genero = select(obras_generos.c.obra_id).where(
                obras_generos.c.genero_id.in_(filtros.generos)
            )
            condicoes.append(Obra.id.in_(obras_do_genero))
        if filtros.ano_de is not None:
            condicoes.append(Obra.ano_lancamento >= filtros.ano_de)
        if filtros.ano_ate is not None:
            condicoes.append(Obra.ano_lancamento <= filtros.ano_ate)
        if filtros.nota_minima is not None:
            condicoes.append(self._resumo.c.media >= filtros.nota_minima)
        if filtros.classificacoes:
            condicoes.append(Obra.classificacao_indicativa.in_(filtros.classificacoes))
        return condicoes

    def _ordenacao(self, filtros: FiltrosObras) -> list:
        coluna = {
            OrdenacaoObras.MEDIA: self._resumo.c.media,
            OrdenacaoObras.TITULO: Obra.titulo,
            OrdenacaoObras.ANO_LANCAMENTO: Obra.ano_lancamento,
        }[filtros.ordenar_por]
        ordem = coluna.asc() if filtros.direcao_efetiva == Direcao.ASC else coluna.desc()
        # Obras sem avaliação ficam no fim; o id garante uma paginação estável.
        return [ordem.nulls_last(), Obra.id]

    @staticmethod
    def _montar(linha) -> ObraComResumo:
        obra, media, total = linha
        return ObraComResumo(
            obra=obra,
            media_notas=round(float(media), 1) if media is not None else None,
            total_avaliacoes=total or 0,
        )

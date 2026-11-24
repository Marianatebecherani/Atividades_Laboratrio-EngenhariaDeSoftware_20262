import asyncio

from app.models.enums import NomeEstrategia
from app.recomendacoes.base import ContextoRecomendacao, EstrategiaRecomendacao
from app.schemas.tmdb import FilmeTmdbResposta


class EstrategiaSimilares(EstrategiaRecomendacao):
    """Recomenda filmes parecidos com os que o usuário avaliou com nota alta.

    Usa as recomendações que o próprio TMDb calcula para cada filme de base.
    """

    nome = NomeEstrategia.SIMILARES

    NOTA_MINIMA = 4
    MAX_FILMES_BASE = 3

    async def recomendar(self, contexto: ContextoRecomendacao) -> list[FilmeTmdbResposta]:
        filmes_base = sorted(
            (
                (tmdb_id, nota)
                for tmdb_id, nota in contexto.notas.items()
                if nota >= self.NOTA_MINIMA
            ),
            key=lambda item: item[1],
            reverse=True,
        )[: self.MAX_FILMES_BASE]

        if not filmes_base:
            return []

        respostas = await asyncio.gather(
            *(self.tmdb.listar_recomendacoes_do_filme(tmdb_id) for tmdb_id, _ in filmes_base)
        )

        candidatos: dict[int, FilmeTmdbResposta] = {}
        pontuacao: dict[int, int] = {}

        # Nota 5 pesa mais que nota 4, e filmes indicados por mais de uma base sobem.
        for (_, nota), (_, recomendados) in zip(filmes_base, respostas, strict=True):
            peso = nota - 3

            for filme in recomendados:
                if filme.tmdb_id in contexto.filmes_excluidos:
                    continue

                candidatos[filme.tmdb_id] = filme
                pontuacao[filme.tmdb_id] = pontuacao.get(filme.tmdb_id, 0) + peso

        return sorted(
            candidatos.values(),
            key=lambda filme: (
                pontuacao[filme.tmdb_id],
                filme.popularidade or 0,
                filme.nota_tmdb or 0,
            ),
            reverse=True,
        )[: contexto.limite]

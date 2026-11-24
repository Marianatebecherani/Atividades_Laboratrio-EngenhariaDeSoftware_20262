from app.models.enums import NomeEstrategia
from app.recomendacoes.base import ContextoRecomendacao, EstrategiaRecomendacao
from app.schemas.tmdb import FilmeTmdbResposta


class EstrategiaPopulares(EstrategiaRecomendacao):
    """Recomenda os filmes populares do TMDb que o usuário ainda não avaliou nem assistiu.

    Não depende do histórico do usuário, então também atende quem acabou de se cadastrar.
    """

    nome = NomeEstrategia.POPULARES

    MAX_PAGINAS = 3

    async def recomendar(self, contexto: ContextoRecomendacao) -> list[FilmeTmdbResposta]:
        filmes: dict[int, FilmeTmdbResposta] = {}

        for pagina in range(1, self.MAX_PAGINAS + 1):
            resultado = await self.tmdb.listar_filmes("populares", pagina)

            for filme in resultado.resultados:
                if filme.tmdb_id not in contexto.filmes_excluidos:
                    filmes.setdefault(filme.tmdb_id, filme)

            if len(filmes) >= contexto.limite or pagina >= resultado.total_paginas:
                break

        return list(filmes.values())[: contexto.limite]

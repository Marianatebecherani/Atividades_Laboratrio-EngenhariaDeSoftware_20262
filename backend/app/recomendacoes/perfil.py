from app.models.enums import NomeEstrategia
from app.recomendacoes.base import ContextoRecomendacao, EstrategiaRecomendacao
from app.schemas.tmdb import DescobrirFilmesParametros, FilmeTmdbResposta


class EstrategiaPerfil(EstrategiaRecomendacao):
    """Recomenda filmes dos gêneros e países que o usuário avaliou melhor."""

    nome = NomeEstrategia.PERFIL

    MAX_PAGINAS_DISCOVER = 10
    MAX_PAISES_PREFERIDOS = 3

    async def recomendar(self, contexto: ContextoRecomendacao) -> list[FilmeTmdbResposta]:
        notas = contexto.notas
        filmes_excluidos = contexto.filmes_excluidos
        limite = contexto.limite

        if not notas:
            return []

        pontuacao_generos: dict[int, int] = {}
        frequencia_generos: dict[int, int] = {}

        pontuacao_paises: dict[str, int] = {}
        frequencia_paises: dict[str, int] = {}

        # Busca os detalhes de cada filme avaliado para descobrir
        # seus gêneros e países de produção.
        for tmdb_id, nota in notas.items():
            filme = await self.tmdb.obter_filme(tmdb_id)
            peso = nota - 3

            for genero_id in set(filme.genero_ids):
                pontuacao_generos[genero_id] = pontuacao_generos.get(genero_id, 0) + peso

                frequencia_generos[genero_id] = frequencia_generos.get(genero_id, 0) + 1

            for pais in set(filme.paises_producao):
                pontuacao_paises[pais] = pontuacao_paises.get(pais, 0) + peso

                frequencia_paises[pais] = frequencia_paises.get(pais, 0) + 1

        # Calcula afinidade positiva para cada gênero.
        afinidade_generos: dict[int, float] = {}

        for genero_id, pontuacao in pontuacao_generos.items():
            frequencia = frequencia_generos[genero_id]

            if pontuacao > 0 and frequencia > 0:
                afinidade_generos[genero_id] = frequencia + (pontuacao / frequencia / 2)

        # Calcula afinidade positiva para cada país.
        afinidade_paises: dict[str, float] = {}

        for pais, pontuacao in pontuacao_paises.items():
            frequencia = frequencia_paises[pais]

            if pontuacao > 0 and frequencia > 0:
                afinidade_paises[pais] = frequencia + (pontuacao / frequencia / 2)

        generos_preferidos = sorted(
            afinidade_generos,
            key=lambda genero_id: afinidade_generos[genero_id],
            reverse=True,
        )

        paises_preferidos = sorted(
            afinidade_paises,
            key=lambda pais: afinidade_paises[pais],
            reverse=True,
        )[: self.MAX_PAISES_PREFERIDOS]

        # Sem afinidade positiva em gênero ou país, não há perfil útil.
        if not generos_preferidos and not paises_preferidos:
            return []

        candidatos: dict[int, FilmeTmdbResposta] = {}

        # Registra quais países fizeram cada filme aparecer nas buscas.
        paises_dos_candidatos: dict[int, set[str]] = {}

        async def buscar_candidatos(pais: str | None = None) -> None:
            for pagina in range(1, self.MAX_PAGINAS_DISCOVER + 1):
                filtros = DescobrirFilmesParametros(
                    page=pagina,
                    genre_ids=generos_preferidos,
                    genre_operator="OR",
                    origin_country=pais,
                    sort_by="popularity.desc",
                )

                resultado = await self.tmdb.descobrir_filmes(filtros)

                for filme in resultado.resultados:
                    if filme.tmdb_id in filmes_excluidos:
                        continue

                    candidatos[filme.tmdb_id] = filme

                    if pais:
                        paises_dos_candidatos.setdefault(filme.tmdb_id, set()).add(pais)

                if (
                    len(candidatos) >= limite * 5
                    or pagina >= resultado.total_paginas
                    or not resultado.resultados
                ):
                    break

        # Busca geral por gêneros, sem limitar a um país.
        if generos_preferidos:
            await buscar_candidatos()

        # Complementa com buscas específicas pelos países preferidos.
        for pais in paises_preferidos:
            await buscar_candidatos(pais)

            if len(candidatos) >= limite * 5:
                break

        # Ordena combinando afinidade de gênero e país.
        def pontuar_filme(filme: FilmeTmdbResposta) -> tuple[float, float, float]:
            pontuacao_genero = sum(
                afinidade_generos.get(genero_id, 0) for genero_id in set(filme.genero_ids)
            )

            pontuacao_pais = sum(
                afinidade_paises.get(pais, 0)
                for pais in paises_dos_candidatos.get(filme.tmdb_id, set())
            )

            return (
                pontuacao_genero + pontuacao_pais,
                filme.popularidade or 0,
                filme.nota_tmdb or 0,
            )

        return sorted(
            candidatos.values(),
            key=pontuar_filme,
            reverse=True,
        )[:limite]

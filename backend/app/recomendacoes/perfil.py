import asyncio
import math

from app.core.excecoes import ErroTmdb
from app.models.enums import NomeEstrategia
from app.recomendacoes.base import ContextoRecomendacao, EstrategiaRecomendacao, Recomendacao
from app.schemas.tmdb import DescobrirFilmesParametros, FilmeTmdbResposta


class EstrategiaPerfil(EstrategiaRecomendacao):
    """Recomenda filmes dos gêneros e países que o usuário avaliou melhor."""

    nome = NomeEstrategia.PERFIL

    MAX_PAGINAS_DISCOVER = 10
    MAX_PAISES_PREFERIDOS = 3
    FILMES_POR_PAGINA = 20  # tamanho das páginas do TMDb

    async def recomendar(self, contexto: ContextoRecomendacao) -> list[Recomendacao]:
        notas = contexto.notas
        filmes_excluidos = contexto.filmes_excluidos
        limite = contexto.limite

        if not notas:
            return []

        pontuacao_generos: dict[int, int] = {}
        frequencia_generos: dict[int, int] = {}

        pontuacao_paises: dict[str, int] = {}
        frequencia_paises: dict[str, int] = {}

        # Busca em paralelo os detalhes de cada filme avaliado (gêneros e países de
        # produção) e os nomes dos gêneros, usados no motivo.
        avaliados = list(notas.items())
        *filmes_avaliados, nomes_generos = await asyncio.gather(
            *(self.tmdb.obter_filme(tmdb_id) for tmdb_id, _ in avaliados),
            self._nomes_dos_generos(),
        )

        for (_, nota), filme in zip(avaliados, filmes_avaliados, strict=True):
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

        meta = limite * 5

        async def buscar_candidatos(pais: str | None, paginas: range) -> bool:
            """Busca as páginas em paralelo e informa se ainda há páginas a buscar."""
            resultados = await asyncio.gather(
                *(
                    self.tmdb.descobrir_filmes(
                        DescobrirFilmesParametros(
                            page=pagina,
                            genre_ids=generos_preferidos,
                            genre_operator="OR",
                            origin_country=pais,
                            sort_by="popularity.desc",
                        )
                    )
                    for pagina in paginas
                )
            )

            for resultado in resultados:
                for filme in resultado.resultados:
                    if filme.tmdb_id in filmes_excluidos:
                        continue

                    candidatos[filme.tmdb_id] = filme

                    if pais:
                        paises_dos_candidatos.setdefault(filme.tmdb_id, set()).add(pais)

            ultimo = resultados[-1]
            return bool(ultimo.resultados) and paginas[-1] < min(
                ultimo.total_paginas, self.MAX_PAGINAS_DISCOVER
            )

        # Primeira rodada, em paralelo: as páginas da busca geral por gêneros que devem
        # bastar para a meta e a primeira página do país preferido.
        primeira_rodada: list[tuple[str | None, int]] = []
        if generos_preferidos:
            paginas_gerais = math.ceil(meta / self.FILMES_POR_PAGINA)
            primeira_rodada.append((None, min(paginas_gerais, self.MAX_PAGINAS_DISCOVER)))
        if paises_preferidos:
            primeira_rodada.append((paises_preferidos[0], 1))

        ha_mais_paginas = await asyncio.gather(
            *(buscar_candidatos(pais, range(1, paginas + 1)) for pais, paginas in primeira_rodada)
        )

        # Se ainda faltarem candidatos, continua página a página, na mesma ordem da
        # versão sequencial: busca geral, país preferido e os demais países.
        continuacoes = [
            (pais, paginas + 1, ha_mais)
            for (pais, paginas), ha_mais in zip(primeira_rodada, ha_mais_paginas, strict=True)
        ]
        continuacoes += [(pais, 1, True) for pais in paises_preferidos[1:]]

        for pais, pagina, ha_mais in continuacoes:
            while ha_mais and len(candidatos) < meta:
                ha_mais = await buscar_candidatos(pais, range(pagina, pagina + 1))
                pagina += 1

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

        recomendados = sorted(
            candidatos.values(),
            key=pontuar_filme,
            reverse=True,
        )[:limite]

        return [
            Recomendacao(
                filme=filme,
                motivo=self._motivo(
                    filme, generos_preferidos, nomes_generos, paises_dos_candidatos
                ),
            )
            for filme in recomendados
        ]

    async def _nomes_dos_generos(self) -> dict[int, str]:
        # Os nomes só enriquecem o motivo; sem eles, a recomendação continua válida.
        try:
            return {genero.id: genero.nome for genero in await self.tmdb.listar_generos()}
        except ErroTmdb:
            return {}

    @staticmethod
    def _motivo(
        filme: FilmeTmdbResposta,
        generos_preferidos: list[int],
        nomes_generos: dict[int, str],
        paises_dos_candidatos: dict[int, set[str]],
    ) -> str:
        generos_do_filme = set(filme.genero_ids)
        generos_em_comum = [g for g in generos_preferidos if g in generos_do_filme]
        nomes = [nomes_generos[g] for g in generos_em_comum if g in nomes_generos][:2]

        if nomes:
            return f"Porque você gosta de {' e '.join(nomes)}"
        if generos_em_comum:
            return "Combina com os gêneros que você avalia bem"
        if filme.tmdb_id in paises_dos_candidatos:
            return "Do mesmo país de filmes que você avaliou bem"
        return "Combina com as suas avaliações"

from time import monotonic
from typing import Any

import httpx
from pydantic import SecretStr, ValidationError

from app.core.excecoes import ErroTmdb
from app.schemas.tmdb import (
    BuscaFilmesTmdbResposta,
    DescobrirFilmesParametros,
    FilmeTmdbResposta,
    GeneroTmdbResposta,
    PessoaElencoTmdbResposta,
    PessoaEquipeTmdbResposta,
)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
IDIOMA = "pt-BR"
TIMEOUT_SEGUNDOS = 10.0
CACHE_GENEROS_SEGUNDOS = 6 * 60 * 60


class TmdbService:
    """Cliente isolado para pesquisa e detalhes de filmes no TMDb."""

    _cache_generos: list[GeneroTmdbResposta] | None = None
    _cache_generos_expira_em = 0.0

    def __init__(
        self,
        token: SecretStr | None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token = token
        self._transport = transport

    async def buscar_filmes(self, query: str, page: int = 1) -> BuscaFilmesTmdbResposta:
        termo = query.strip()
        if not termo:
            raise ErroTmdb(422, "Informe o nome de um filme para pesquisar.")

        dados = await self._get(
            "/search/movie",
            params={"query": termo, "language": IDIOMA, "page": page},
        )
        return self._mapear_pagina(dados)

    async def listar_filmes(self, categoria: str, page: int = 1) -> BuscaFilmesTmdbResposta:
        caminhos = {
            "populares": "/movie/popular",
            "top-rated": "/movie/top_rated",
            "now-playing": "/movie/now_playing",
            "upcoming": "/movie/upcoming",
        }
        if categoria not in caminhos:
            raise ErroTmdb(404, "Categoria de filmes não encontrada.")
        dados = await self._get(caminhos[categoria], params={"language": IDIOMA, "page": page})
        return self._mapear_pagina(dados)

    async def descobrir_filmes(
        self,
        filtros: DescobrirFilmesParametros,
    ) -> BuscaFilmesTmdbResposta:
        params: dict[str, str | int | float] = {
            "language": filtros.language,
            "page": filtros.page,
            "sort_by": filtros.sort_by,
        }
        genre_ids = filtros.genero_ids_efetivos
        if genre_ids:
            separador = "," if filtros.genre_operator == "AND" else "|"
            params["with_genres"] = separador.join(map(str, genre_ids))
        if filtros.year is not None:
            params["year"] = filtros.year
        if filtros.data_de_efetiva is not None:
            params["release_date.gte"] = filtros.data_de_efetiva.isoformat()
        if filtros.data_ate_efetiva is not None:
            params["release_date.lte"] = filtros.data_ate_efetiva.isoformat()
        if filtros.nota_minima_efetiva is not None:
            params["vote_average.gte"] = filtros.nota_minima_efetiva
        nota_maxima = filtros.max_rating
        if nota_maxima is not None:
            params["vote_average.lte"] = nota_maxima
        dados = await self._get("/discover/movie", params=params)
        return self._mapear_pagina(dados)

    async def listar_generos(self) -> list[GeneroTmdbResposta]:
        classe = type(self)
        if classe._cache_generos is not None and monotonic() < classe._cache_generos_expira_em:
            return classe._cache_generos

        dados = await self._get("/genre/movie/list", params={"language": IDIOMA})
        try:
            generos = [
                GeneroTmdbResposta.model_validate({"id": item["id"], "nome": item["name"]})
                for item in dados["genres"]
            ]
        except (KeyError, TypeError, ValidationError) as erro:
            raise ErroTmdb(502, "O TMDb retornou uma resposta inválida.") from erro
        classe._cache_generos = generos
        classe._cache_generos_expira_em = monotonic() + CACHE_GENEROS_SEGUNDOS
        return generos

    async def obter_filme(self, tmdb_id: int) -> FilmeTmdbResposta:
        dados = await self._get(
            f"/movie/{tmdb_id}",
            params={"language": IDIOMA, "append_to_response": "credits"},
        )
        try:
            return self._mapear_filme(dados)
        except (KeyError, TypeError, ValidationError) as erro:
            raise ErroTmdb(502, "O TMDb retornou uma resposta inválida.") from erro

    async def _get(self, caminho: str, params: dict[str, str | int | float]) -> dict[str, Any]:
        if self._token is None or not self._token.get_secret_value().strip():
            raise ErroTmdb(503, "A integração com o TMDb não está configurada no servidor.")

        try:
            async with httpx.AsyncClient(
                base_url=TMDB_BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._token.get_secret_value()}",
                    "Accept": "application/json",
                },
                timeout=TIMEOUT_SEGUNDOS,
                transport=self._transport,
            ) as cliente:
                resposta = await cliente.get(caminho, params=params)
        except httpx.TimeoutException as erro:
            raise ErroTmdb(504, "O TMDb demorou demais para responder.") from erro
        except httpx.RequestError as erro:
            raise ErroTmdb(502, "Não foi possível conectar ao TMDb.") from erro

        if resposta.status_code == 404:
            raise ErroTmdb(404, "Filme não encontrado no TMDb.")
        if resposta.status_code == 429:
            raise ErroTmdb(429, "O TMDb limitou temporariamente as consultas.")
        if resposta.status_code in (401, 403):
            raise ErroTmdb(502, "A autenticação do serviço TMDb falhou.")
        if resposta.is_error:
            raise ErroTmdb(502, "O TMDb não conseguiu atender à consulta.")

        try:
            dados = resposta.json()
        except ValueError as erro:
            raise ErroTmdb(502, "O TMDb retornou uma resposta inválida.") from erro
        if not isinstance(dados, dict):
            raise ErroTmdb(502, "O TMDb retornou uma resposta inválida.")
        return dados

    @staticmethod
    def _mapear_pagina(dados: dict[str, Any]) -> BuscaFilmesTmdbResposta:
        try:
            return BuscaFilmesTmdbResposta.model_validate(
                {
                    "pagina": dados["page"],
                    "total_paginas": dados["total_pages"],
                    "total_resultados": dados["total_results"],
                    "resultados": [TmdbService._mapear_filme(item) for item in dados["results"]],
                }
            )
        except (KeyError, TypeError, ValidationError) as erro:
            raise ErroTmdb(502, "O TMDb retornou uma resposta inválida.") from erro

    @staticmethod
    def _mapear_filme(dados: dict[str, Any]) -> FilmeTmdbResposta:
        poster_path = dados.get("poster_path")
        backdrop_path = dados.get("backdrop_path")
        credits = dados.get("credits") or {}
        elenco = [
            PessoaElencoTmdbResposta(
                tmdb_id=pessoa["id"],
                nome=pessoa["name"],
                personagem=pessoa.get("character"),
                perfil_url=TmdbService._url_imagem(pessoa.get("profile_path"), "w185"),
            )
            for pessoa in credits.get("cast", [])[:20]
        ]
        equipe_principal = [
            PessoaEquipeTmdbResposta(
                tmdb_id=pessoa["id"],
                nome=pessoa["name"],
                departamento=pessoa.get("department"),
                funcao=pessoa.get("job"),
                perfil_url=TmdbService._url_imagem(pessoa.get("profile_path"), "w185"),
            )
            for pessoa in credits.get("crew", [])
            if pessoa.get("job") in {"Director", "Screenplay", "Writer", "Producer"}
        ][:20]
        diretor = next(
            (pessoa.nome for pessoa in equipe_principal if pessoa.funcao == "Director"), None
        )
        generos = dados.get("genres") or dados.get("genre_ids") or []
        genero_ids = [item["id"] if isinstance(item, dict) else item for item in generos]
        return FilmeTmdbResposta.model_validate(
            {
                "tmdb_id": dados.get("id"),
                "titulo": dados.get("title"),
                "titulo_original": dados.get("original_title"),
                "sinopse": dados.get("overview") or None,
                "data_lancamento": dados.get("release_date") or None,
                "poster_path": poster_path,
                "backdrop_path": backdrop_path,
                "idioma_original": dados.get("original_language"),
                "nota_tmdb": dados.get("vote_average"),
                "quantidade_votos": dados.get("vote_count", 0),
                "popularidade": dados.get("popularity"),
                "genero_ids": genero_ids,
                "poster_url": TmdbService._url_imagem(poster_path, "w500"),
                "backdrop_url": TmdbService._url_imagem(backdrop_path, "w780"),
                "elenco": elenco,
                "diretor": diretor,
                "equipe_principal": equipe_principal,
            }
        )

    @staticmethod
    def _url_imagem(path: str | None, tamanho: str) -> str | None:
        return f"{TMDB_IMAGE_BASE_URL}/{tamanho}{path}" if path else None

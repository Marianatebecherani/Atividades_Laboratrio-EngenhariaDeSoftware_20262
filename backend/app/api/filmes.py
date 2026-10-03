from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.dependencias import FilmesUsuarioServiceDep, UsuarioAtualDep
from app.core.config import obter_configuracoes
from app.schemas.tmdb import (
    BuscaFilmesTmdbResposta,
    DescobrirFilmesParametros,
    FavoritoTmdbResposta,
    FilmeTmdbResposta,
)
from app.services.tmdb_service import TmdbService

router = APIRouter(prefix="/filmes", tags=["Filmes TMDb"])


def obter_tmdb_service() -> TmdbService:
    return TmdbService(obter_configuracoes().tmdb_api_token)


TmdbServiceDep = Annotated[TmdbService, Depends(obter_tmdb_service)]
PaginaQuery = Annotated[int, Query(ge=1, le=500)]
TmdbIdPath = Annotated[int, Path(gt=0)]


@router.get("/buscar", response_model=BuscaFilmesTmdbResposta, summary="Busca filmes no TMDb")
async def buscar_filmes(
    query: Annotated[str, Query(min_length=1, description="Título ou parte do título")],
    service: TmdbServiceDep,
    page: Annotated[int, Query(ge=1, le=500)] = 1,
) -> BuscaFilmesTmdbResposta:
    return await service.buscar_filmes(query, page)


@router.get("/populares", response_model=BuscaFilmesTmdbResposta)
async def listar_populares(service: TmdbServiceDep, page: PaginaQuery = 1):
    return await service.listar_filmes("populares", page)


@router.get("/top-rated", response_model=BuscaFilmesTmdbResposta)
async def listar_top_rated(service: TmdbServiceDep, page: PaginaQuery = 1):
    return await service.listar_filmes("top-rated", page)


@router.get("/now-playing", response_model=BuscaFilmesTmdbResposta)
async def listar_now_playing(service: TmdbServiceDep, page: PaginaQuery = 1):
    return await service.listar_filmes("now-playing", page)


@router.get("/upcoming", response_model=BuscaFilmesTmdbResposta)
async def listar_upcoming(service: TmdbServiceDep, page: PaginaQuery = 1):
    return await service.listar_filmes("upcoming", page)


@router.get("/discover", response_model=BuscaFilmesTmdbResposta)
async def descobrir_filmes(
    filtros: Annotated[DescobrirFilmesParametros, Query()],
    service: TmdbServiceDep,
) -> BuscaFilmesTmdbResposta:
    return await service.descobrir_filmes(filtros)


@router.get("/generos", summary="Lista os gêneros de filmes do TMDb")
async def listar_generos_tmdb(service: TmdbServiceDep):
    return await service.listar_generos()


@router.get(
    "/{tmdb_id}", response_model=FilmeTmdbResposta, summary="Obtém detalhes de um filme TMDb"
)
async def obter_filme(tmdb_id: int, service: TmdbServiceDep) -> FilmeTmdbResposta:
    return await service.obter_filme(tmdb_id)


@router.post(
    "/{tmdb_id}/favoritar",
    status_code=status.HTTP_201_CREATED,
    response_model=FavoritoTmdbResposta,
    summary="Adiciona um filme TMDb aos favoritos do usuário",
)
def favoritar_filme(
    tmdb_id: TmdbIdPath,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
    resposta: Response,
) -> FavoritoTmdbResposta:
    criado_em, criado = servico.favoritar(usuario.id, tmdb_id)
    if not criado:
        resposta.status_code = status.HTTP_200_OK
    return FavoritoTmdbResposta(tmdb_id=tmdb_id, criado_em=criado_em)


@router.delete(
    "/{tmdb_id}/favoritar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um filme TMDb dos favoritos do usuário",
)
def desfavoritar_filme(
    tmdb_id: TmdbIdPath,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> None:
    servico.desfavoritar(usuario.id, tmdb_id)

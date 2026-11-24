from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.dependencias import (
    FilmesUsuarioServiceDep,
    RecomendacaoServiceDep,
    UsuarioAtualDep,
    UsuarioServiceDep,
)
from app.models.enums import NomeEstrategia
from app.schemas.item_lista import FiltroFilmesUsuario, ItemListaEntrada
from app.schemas.paginacao import Paginacao
from app.schemas.tmdb import (
    AvaliacaoTmdbEntrada,
    EstadoFilmeTmdbResposta,
    PaginaEstadoFilmesTmdbResposta,
    PaginaFavoritosTmdbResposta,
    RecomendacoesTmdbResposta,
)
from app.schemas.usuario import UsuarioAtualizacao, UsuarioExclusao, UsuarioResposta

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

RESPOSTA_401 = {401: {"description": "Token ausente, inválido ou expirado"}}
TmdbIdPath = Annotated[int, Path(gt=0)]


@router.get(
    "/me/recomendacoes",
    response_model=RecomendacoesTmdbResposta,
    summary="Recomenda filmes ao usuário com a estratégia escolhida",
    description=(
        "Estratégias (padrão Strategy): `perfil` usa os gêneros e países dos filmes que o "
        "usuário avaliou bem; `similares` usa as recomendações do TMDb para os filmes com "
        "nota 4 ou 5; `populares` traz os filmes populares do TMDb. Filmes avaliados ou "
        "já assistidos não são recomendados. Quando a estratégia escolhida não encontra "
        "filmes, a resposta usa `populares` e informa isso no campo `estrategia`. O campo "
        "`tempo_ms` informa quanto tempo o cálculo levou."
    ),
    responses=RESPOSTA_401,
)
async def recomendar_filmes(
    usuario: UsuarioAtualDep,
    servico: RecomendacaoServiceDep,
    estrategia: Annotated[
        NomeEstrategia, Query(description="Critério usado para recomendar")
    ] = NomeEstrategia.PERFIL,
    limite: Annotated[int, Query(ge=1, le=50)] = 10,
) -> RecomendacoesTmdbResposta:
    return await servico.recomendar(usuario.id, estrategia=estrategia, limite=limite)


@router.get("/me", summary="Retorna o usuário autenticado", responses=RESPOSTA_401)
def obter_perfil(usuario: UsuarioAtualDep) -> UsuarioResposta:
    return usuario


@router.patch(
    "/me",
    summary="Atualiza nome, e-mail ou senha do usuário autenticado",
    description="Para alterar o e-mail ou a senha, informe também `senha_atual`.",
    responses={
        **RESPOSTA_401,
        403: {"description": "Senha atual incorreta"},
        409: {"description": "E-mail já cadastrado"},
    },
)
def atualizar_perfil(
    dados: UsuarioAtualizacao, usuario: UsuarioAtualDep, servico: UsuarioServiceDep
) -> UsuarioResposta:
    return servico.atualizar(usuario, dados)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui a conta do usuário autenticado",
    description="Remove também a lista e as avaliações do usuário. Exige a senha.",
    responses={
        **RESPOSTA_401,
        403: {"description": "Senha incorreta"},
        409: {"description": "Único administrador do sistema"},
    },
)
def excluir_conta(
    dados: UsuarioExclusao, usuario: UsuarioAtualDep, servico: UsuarioServiceDep
) -> None:
    servico.excluir(usuario, dados.senha)


@router.get(
    "/me/favoritos",
    response_model=PaginaFavoritosTmdbResposta,
    summary="Lista os filmes TMDb favoritos do usuário",
    responses=RESPOSTA_401,
)
def listar_favoritos(
    paginacao: Annotated[Paginacao, Query()],
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> PaginaFavoritosTmdbResposta:
    return servico.listar_favoritos(usuario.id, paginacao)


@router.get(
    "/me/filmes",
    response_model=PaginaEstadoFilmesTmdbResposta,
    summary="Lista os IDs TMDb acompanhados pelo usuário",
    description=(
        "Use `status` para ver só os filmes da lista em uma situação: `quero_assistir`, "
        "`assistindo` ou `assistido`. O `total` e a paginação consideram o filtro."
    ),
    responses=RESPOSTA_401,
)
def listar_filmes_tmdb_usuario(
    filtros: Annotated[FiltroFilmesUsuario, Query()],
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> PaginaEstadoFilmesTmdbResposta:
    return servico.listar_filmes(usuario.id, filtros, status=filtros.status)


@router.get(
    "/me/filmes/{tmdb_id}",
    response_model=EstadoFilmeTmdbResposta,
    summary="Retorna o estado pessoal do usuário para um filme TMDb",
    responses=RESPOSTA_401,
)
def obter_estado_filme_tmdb(
    tmdb_id: TmdbIdPath,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> EstadoFilmeTmdbResposta:
    return servico.obter_estado(usuario.id, tmdb_id)


@router.put(
    "/me/filmes/{tmdb_id}/lista",
    response_model=EstadoFilmeTmdbResposta,
    summary="Adiciona ou atualiza o status pessoal de um filme TMDb",
    responses=RESPOSTA_401,
)
def definir_status_filme_tmdb(
    tmdb_id: TmdbIdPath,
    dados: ItemListaEntrada,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> EstadoFilmeTmdbResposta:
    return servico.definir_status(usuario.id, tmdb_id, dados)


@router.delete(
    "/me/filmes/{tmdb_id}/lista",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove o status pessoal de um filme TMDb",
    responses=RESPOSTA_401,
)
def remover_status_filme_tmdb(
    tmdb_id: TmdbIdPath,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> None:
    servico.remover_da_lista(usuario.id, tmdb_id)


@router.put(
    "/me/filmes/{tmdb_id}/avaliacao",
    response_model=EstadoFilmeTmdbResposta,
    summary="Cria ou atualiza a nota pessoal de um filme TMDb",
    responses=RESPOSTA_401,
)
def avaliar_filme_tmdb(
    tmdb_id: TmdbIdPath,
    dados: AvaliacaoTmdbEntrada,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> EstadoFilmeTmdbResposta:
    return servico.avaliar(usuario.id, tmdb_id, dados)


@router.delete(
    "/me/filmes/{tmdb_id}/avaliacao",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a nota pessoal de um filme TMDb",
    responses=RESPOSTA_401,
)
def remover_avaliacao_filme_tmdb(
    tmdb_id: TmdbIdPath,
    usuario: UsuarioAtualDep,
    servico: FilmesUsuarioServiceDep,
) -> None:
    servico.remover_avaliacao(usuario.id, tmdb_id)

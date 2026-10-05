from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.dependencias import ComentarioServiceDep, UsuarioAtualDep
from app.schemas.comentario import ComentarioEntrada, ComentarioResposta, PaginaComentariosResposta
from app.schemas.paginacao import Paginacao

router = APIRouter(tags=["Comentários"])

RESPOSTA_401 = {401: {"description": "Token ausente, inválido ou expirado"}}
RESPOSTA_403 = {403: {"description": "Operação permitida apenas para o autor do comentário"}}
RESPOSTA_404 = {404: {"description": "Comentário não encontrado"}}
TmdbIdPath = Annotated[int, Path(gt=0)]
ComentarioIdPath = Annotated[int, Path(gt=0)]


@router.get(
    "/filmes/{tmdb_id}/comentarios",
    response_model=PaginaComentariosResposta,
    summary="Lista os comentários públicos de um filme TMDb",
)
def listar_comentarios(
    tmdb_id: TmdbIdPath,
    paginacao: Annotated[Paginacao, Query()],
    servico: ComentarioServiceDep,
) -> PaginaComentariosResposta:
    return servico.listar(tmdb_id, paginacao)


@router.get(
    "/filmes/{tmdb_id}/comentarios/meu",
    response_model=ComentarioResposta | None,
    summary="Obtém o comentário próprio (se existir) de um filme TMDb",
    responses=RESPOSTA_401,
)
def obter_meu_comentario(
    tmdb_id: TmdbIdPath,
    usuario: UsuarioAtualDep,
    servico: ComentarioServiceDep,
) -> ComentarioResposta | None:
    return servico.obter_meu(usuario.id, tmdb_id)


@router.post(
    "/filmes/{tmdb_id}/comentarios",
    response_model=ComentarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um comentário em um filme TMDb",
    responses=RESPOSTA_401,
)
def criar_comentario(
    tmdb_id: TmdbIdPath,
    dados: ComentarioEntrada,
    usuario: UsuarioAtualDep,
    servico: ComentarioServiceDep,
) -> ComentarioResposta:
    return servico.criar(usuario.id, tmdb_id, dados)


@router.patch(
    "/comentarios/{comentario_id}",
    response_model=ComentarioResposta,
    summary="Edita um comentário próprio",
    responses={**RESPOSTA_401, **RESPOSTA_403, **RESPOSTA_404},
)
def atualizar_comentario(
    comentario_id: ComentarioIdPath,
    dados: ComentarioEntrada,
    usuario: UsuarioAtualDep,
    servico: ComentarioServiceDep,
) -> ComentarioResposta:
    return servico.atualizar(usuario.id, comentario_id, dados)


@router.delete(
    "/comentarios/{comentario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um comentário próprio",
    responses={**RESPOSTA_401, **RESPOSTA_403, **RESPOSTA_404},
)
def remover_comentario(
    comentario_id: ComentarioIdPath,
    usuario: UsuarioAtualDep,
    servico: ComentarioServiceDep,
) -> None:
    servico.remover(usuario.id, comentario_id)

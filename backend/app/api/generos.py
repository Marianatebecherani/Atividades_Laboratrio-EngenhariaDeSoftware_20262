from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencias import AdminDep, SessaoDep
from app.schemas.genero import GeneroEntrada, GeneroResposta
from app.services.genero_service import GeneroService

router = APIRouter(prefix="/generos", tags=["Gêneros"])


def obter_genero_service(sessao: SessaoDep) -> GeneroService:
    return GeneroService(sessao)


GeneroServiceDep = Annotated[GeneroService, Depends(obter_genero_service)]

RESPOSTAS_ADMIN = {
    401: {"description": "Token ausente, inválido ou expirado"},
    403: {"description": "Operação permitida apenas para administradores"},
}


@router.get("", summary="Lista os gêneros em ordem alfabética")
def listar_generos(servico: GeneroServiceDep) -> list[GeneroResposta]:
    return servico.listar()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um gênero (admin)",
    responses={**RESPOSTAS_ADMIN, 409: {"description": "Já existe um gênero com esse nome"}},
)
def criar_genero(dados: GeneroEntrada, _: AdminDep, servico: GeneroServiceDep) -> GeneroResposta:
    return servico.criar(dados)


@router.put(
    "/{genero_id}",
    summary="Renomeia um gênero (admin)",
    responses={
        **RESPOSTAS_ADMIN,
        404: {"description": "Gênero não encontrado"},
        409: {"description": "Já existe um gênero com esse nome"},
    },
)
def atualizar_genero(
    genero_id: int, dados: GeneroEntrada, _: AdminDep, servico: GeneroServiceDep
) -> GeneroResposta:
    return servico.atualizar(genero_id, dados)


@router.delete(
    "/{genero_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um gênero sem obras associadas (admin)",
    responses={
        **RESPOSTAS_ADMIN,
        404: {"description": "Gênero não encontrado"},
        409: {"description": "Gênero associado a obras"},
    },
)
def excluir_genero(genero_id: int, _: AdminDep, servico: GeneroServiceDep) -> None:
    servico.excluir(genero_id)

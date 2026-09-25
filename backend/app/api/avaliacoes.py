from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencias import AdminDep, SessaoDep, UsuarioAtualDep
from app.schemas.avaliacao import AvaliacaoEntrada, AvaliacaoResposta, PaginaAvaliacoes
from app.schemas.paginacao import Paginacao
from app.services.avaliacao_service import AvaliacaoService

router = APIRouter(tags=["Avaliações"])


def obter_avaliacao_service(sessao: SessaoDep) -> AvaliacaoService:
    return AvaliacaoService(sessao)


AvaliacaoServiceDep = Annotated[AvaliacaoService, Depends(obter_avaliacao_service)]

RESPOSTA_401 = {401: {"description": "Token ausente, inválido ou expirado"}}


@router.get(
    "/obras/{obra_id}/avaliacoes",
    summary="Lista as avaliações de uma obra",
    description="Mais recentes primeiro. Inclui o nome de quem avaliou.",
    responses={404: {"description": "Obra não encontrada"}},
)
def listar_avaliacoes(
    obra_id: int, paginacao: Annotated[Paginacao, Query()], servico: AvaliacaoServiceDep
) -> PaginaAvaliacoes:
    avaliacoes, total = servico.listar_da_obra(obra_id, paginacao)
    return PaginaAvaliacoes(
        itens=[AvaliacaoResposta.model_validate(avaliacao) for avaliacao in avaliacoes],
        total=total,
        pagina=paginacao.pagina,
        tamanho=paginacao.tamanho,
    )


@router.put(
    "/obras/{obra_id}/avaliacoes/me",
    summary="Cria ou atualiza a avaliação do usuário para a obra",
    description="Retorna 201 quando a avaliação é criada e 200 quando é atualizada.",
    responses={
        **RESPOSTA_401,
        201: {"description": "Avaliação criada"},
        404: {"description": "Obra não encontrada"},
    },
)
def avaliar(
    obra_id: int,
    dados: AvaliacaoEntrada,
    usuario: UsuarioAtualDep,
    servico: AvaliacaoServiceDep,
    resposta: Response,
) -> AvaliacaoResposta:
    avaliacao, criada = servico.avaliar(usuario, obra_id, dados)
    if criada:
        resposta.status_code = status.HTTP_201_CREATED
    return AvaliacaoResposta.model_validate(avaliacao)


@router.delete(
    "/obras/{obra_id}/avaliacoes/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a avaliação do usuário para a obra",
    responses={**RESPOSTA_401, 404: {"description": "Avaliação não encontrada"}},
)
def remover_minha_avaliacao(
    obra_id: int, usuario: UsuarioAtualDep, servico: AvaliacaoServiceDep
) -> None:
    servico.remover_do_usuario(usuario, obra_id)


@router.delete(
    "/avaliacoes/{avaliacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove qualquer avaliação (moderação, admin)",
    responses={
        **RESPOSTA_401,
        403: {"description": "Operação permitida apenas para administradores"},
        404: {"description": "Avaliação não encontrada"},
    },
)
def moderar_avaliacao(avaliacao_id: int, _: AdminDep, servico: AvaliacaoServiceDep) -> None:
    servico.remover_por_id(avaliacao_id)

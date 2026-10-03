from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencias import AdminDep, SessaoDep
from app.services.avaliacao_service import AvaliacaoService

router = APIRouter(tags=["Avaliações"])


def obter_avaliacao_service(sessao: SessaoDep) -> AvaliacaoService:
    return AvaliacaoService(sessao)


AvaliacaoServiceDep = Annotated[AvaliacaoService, Depends(obter_avaliacao_service)]

RESPOSTA_401 = {401: {"description": "Token ausente, inválido ou expirado"}}


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

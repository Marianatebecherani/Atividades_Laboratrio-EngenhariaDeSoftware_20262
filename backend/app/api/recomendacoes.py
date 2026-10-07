from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.conversores import obra_para_resposta
from app.api.dependencias import SessaoDep, UsuarioAtualDep
from app.schemas.recomendacao import (
    ParametrosRecomendacao,
    RecomendacaoResposta,
    RecomendacoesResposta,
)
from app.services.recomendacao_service import RecomendacaoService

router = APIRouter(prefix="/usuarios/me/recomendacoes", tags=["Recomendações"])


def obter_recomendacao_service(sessao: SessaoDep) -> RecomendacaoService:
    return RecomendacaoService(sessao)


RecomendacaoServiceDep = Annotated[RecomendacaoService, Depends(obter_recomendacao_service)]


@router.get(
    "",
    summary="Recomenda obras para o usuário",
    description=(
        "Estratégias: `generos` (gêneros preferidos, padrão), `similares` (parecidas com as "
        "obras avaliadas com nota 4 ou 5) e `populares` (mais bem avaliadas). Obras que já "
        "estão na lista ou já foram avaliadas pelo usuário não são recomendadas."
    ),
    responses={401: {"description": "Token ausente, inválido ou expirado"}},
)
def recomendar(
    parametros: Annotated[ParametrosRecomendacao, Query()],
    usuario: UsuarioAtualDep,
    servico: RecomendacaoServiceDep,
) -> RecomendacoesResposta:
    resultado = servico.recomendar(usuario, parametros.estrategia, parametros.limite)
    return RecomendacoesResposta(
        estrategia=resultado.estrategia,
        itens=[
            RecomendacaoResposta(
                obra=obra_para_resposta(obra),
                pontuacao=recomendacao.pontuacao,
                motivo=recomendacao.motivo,
            )
            for recomendacao, obra in resultado.itens
        ],
        tempo_ms=resultado.tempo_ms,
    )

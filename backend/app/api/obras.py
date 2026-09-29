from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from app.api.conversores import obra_para_resposta
from app.api.dependencias import AdminDep, SessaoDep, UsuarioOpcionalDep
from app.models import StatusLista
from app.models.poster import TAMANHO_MAXIMO_BYTES
from app.schemas.obra import FiltrosObras, ObraEntrada, ObraResposta, PaginaObras
from app.services.lista_service import ListaService
from app.services.obra_service import ObraService

router = APIRouter(prefix="/obras", tags=["Obras"])


def obter_obra_service(sessao: SessaoDep) -> ObraService:
    return ObraService(sessao)


ObraServiceDep = Annotated[ObraService, Depends(obter_obra_service)]

RESPOSTAS_ADMIN = {
    401: {"description": "Token ausente, inválido ou expirado"},
    403: {"description": "Operação permitida apenas para administradores"},
}
RESPOSTA_404 = {404: {"description": "Obra não encontrada"}}


def status_na_lista(
    sessao: SessaoDep, usuario: UsuarioOpcionalDep, obra_ids: list[int]
) -> dict[int, StatusLista]:
    """Status das obras na lista do usuário autenticado; vazio para visitantes."""
    if usuario is None or not obra_ids:
        return {}
    return ListaService(sessao).status_por_obra(usuario, obra_ids)


DESCRICAO_MEU_STATUS = (
    "Com um token válido, cada obra traz `meu_status` (status na lista do usuário). "
    "Sem token, ou com token inválido, `meu_status` vem nulo."
)


@router.get(
    "",
    summary="Busca obras com filtros, ordenação e paginação",
    description=DESCRICAO_MEU_STATUS,
)
def buscar_obras(
    filtros: Annotated[FiltrosObras, Query()],
    servico: ObraServiceDep,
    sessao: SessaoDep,
    usuario: UsuarioOpcionalDep,
) -> PaginaObras:
    resultados, total = servico.buscar(filtros)
    status_lista = status_na_lista(sessao, usuario, [resultado.obra.id for resultado in resultados])
    return PaginaObras(
        itens=[obra_para_resposta(r, status_lista.get(r.obra.id)) for r in resultados],
        total=total,
        pagina=filtros.pagina,
        tamanho=filtros.tamanho,
    )


@router.get(
    "/{obra_id}",
    summary="Detalha uma obra",
    description=DESCRICAO_MEU_STATUS,
    responses=RESPOSTA_404,
)
def obter_obra(
    obra_id: int, servico: ObraServiceDep, sessao: SessaoDep, usuario: UsuarioOpcionalDep
) -> ObraResposta:
    resultado = servico.obter(obra_id)
    status_lista = status_na_lista(sessao, usuario, [obra_id])
    return obra_para_resposta(resultado, status_lista.get(obra_id))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra uma obra (admin)",
    responses={**RESPOSTAS_ADMIN, 422: {"description": "Dados inválidos ou gêneros inexistentes"}},
)
def criar_obra(dados: ObraEntrada, _: AdminDep, servico: ObraServiceDep) -> ObraResposta:
    return obra_para_resposta(servico.criar(dados))


@router.put(
    "/{obra_id}",
    summary="Atualiza todos os dados de uma obra (admin)",
    responses={**RESPOSTAS_ADMIN, **RESPOSTA_404},
)
def atualizar_obra(
    obra_id: int, dados: ObraEntrada, _: AdminDep, servico: ObraServiceDep
) -> ObraResposta:
    return obra_para_resposta(servico.atualizar(obra_id, dados))


@router.delete(
    "/{obra_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma obra, com pôster, itens de lista e avaliações (admin)",
    responses={**RESPOSTAS_ADMIN, **RESPOSTA_404},
)
def excluir_obra(obra_id: int, _: AdminDep, servico: ObraServiceDep) -> None:
    servico.excluir(obra_id)


@router.get(
    "/{obra_id}/poster",
    summary="Retorna a imagem do pôster",
    response_class=Response,
    responses={
        200: {"content": {"image/png": {}, "image/jpeg": {}, "image/webp": {}}},
        404: {"description": "Obra ou pôster não encontrado"},
    },
)
def obter_poster(obra_id: int, servico: ObraServiceDep) -> Response:
    poster = servico.obter_poster(obra_id)
    return Response(
        content=poster.conteudo,
        media_type=poster.tipo_mime,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.put(
    "/{obra_id}/poster",
    summary="Envia ou substitui o pôster (admin)",
    description="Imagem PNG, JPEG ou WebP com até 2 MB.",
    responses={
        **RESPOSTAS_ADMIN,
        **RESPOSTA_404,
        413: {"description": "Arquivo maior que 2 MB"},
        415: {"description": "Arquivo não é PNG, JPEG ou WebP"},
    },
)
def enviar_poster(
    obra_id: int,
    arquivo: Annotated[UploadFile, File(description="Imagem do pôster")],
    _: AdminDep,
    servico: ObraServiceDep,
) -> ObraResposta:
    # Lê um byte além do limite apenas para detectar arquivos grandes demais.
    conteudo = arquivo.file.read(TAMANHO_MAXIMO_BYTES + 1)
    return obra_para_resposta(servico.definir_poster(obra_id, conteudo))


@router.delete(
    "/{obra_id}/poster",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove o pôster (admin)",
    responses={**RESPOSTAS_ADMIN, 404: {"description": "Obra ou pôster não encontrado"}},
)
def remover_poster(obra_id: int, _: AdminDep, servico: ObraServiceDep) -> None:
    servico.remover_poster(obra_id)

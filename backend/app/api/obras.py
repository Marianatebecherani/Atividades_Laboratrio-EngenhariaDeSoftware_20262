from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from app.api.dependencias import AdminDep, SessaoDep
from app.models.poster import TAMANHO_MAXIMO_BYTES
from app.repositories.obra_repository import ObraComResumo
from app.schemas.genero import GeneroResposta
from app.schemas.obra import FiltrosObras, ObraEntrada, ObraResposta, PaginaObras
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


def para_resposta(resultado: ObraComResumo) -> ObraResposta:
    obra = resultado.obra
    url_poster = None
    if obra.poster is not None:
        # O parâmetro de versão muda quando o pôster é trocado, invalidando o cache do navegador.
        versao = int(obra.poster.atualizado_em.timestamp())
        url_poster = f"/api/v1/obras/{obra.id}/poster?v={versao}"
    return ObraResposta(
        id=obra.id,
        titulo=obra.titulo,
        tipo=obra.tipo,
        ano_lancamento=obra.ano_lancamento,
        sinopse=obra.sinopse,
        classificacao_indicativa=obra.classificacao_indicativa,
        duracao_minutos=obra.duracao_minutos,
        temporadas=obra.temporadas,
        generos=[GeneroResposta.model_validate(genero) for genero in obra.generos],
        media_notas=resultado.media_notas,
        total_avaliacoes=resultado.total_avaliacoes,
        url_poster=url_poster,
    )


@router.get("", summary="Busca obras com filtros, ordenação e paginação")
def buscar_obras(filtros: Annotated[FiltrosObras, Query()], servico: ObraServiceDep) -> PaginaObras:
    resultados, total = servico.buscar(filtros)
    return PaginaObras(
        itens=[para_resposta(resultado) for resultado in resultados],
        total=total,
        pagina=filtros.pagina,
        tamanho=filtros.tamanho,
    )


@router.get("/{obra_id}", summary="Detalha uma obra", responses=RESPOSTA_404)
def obter_obra(obra_id: int, servico: ObraServiceDep) -> ObraResposta:
    return para_resposta(servico.obter(obra_id))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra uma obra (admin)",
    responses={**RESPOSTAS_ADMIN, 422: {"description": "Dados inválidos ou gêneros inexistentes"}},
)
def criar_obra(dados: ObraEntrada, _: AdminDep, servico: ObraServiceDep) -> ObraResposta:
    return para_resposta(servico.criar(dados))


@router.put(
    "/{obra_id}",
    summary="Atualiza todos os dados de uma obra (admin)",
    responses={**RESPOSTAS_ADMIN, **RESPOSTA_404},
)
def atualizar_obra(
    obra_id: int, dados: ObraEntrada, _: AdminDep, servico: ObraServiceDep
) -> ObraResposta:
    return para_resposta(servico.atualizar(obra_id, dados))


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
    return para_resposta(servico.definir_poster(obra_id, conteudo))


@router.delete(
    "/{obra_id}/poster",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove o pôster (admin)",
    responses={**RESPOSTAS_ADMIN, 404: {"description": "Obra ou pôster não encontrado"}},
)
def remover_poster(obra_id: int, _: AdminDep, servico: ObraServiceDep) -> None:
    servico.remover_poster(obra_id)

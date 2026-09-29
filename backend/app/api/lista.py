from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.conversores import obra_para_resposta
from app.api.dependencias import SessaoDep, UsuarioAtualDep
from app.models import ItemLista
from app.repositories.obra_repository import ObraComResumo
from app.schemas.item_lista import (
    FiltrosLista,
    ItemListaEntrada,
    ItemListaResposta,
    PaginaItensLista,
)
from app.services.lista_service import ListaService

router = APIRouter(prefix="/usuarios/me/lista", tags=["Minha lista"])


def obter_lista_service(sessao: SessaoDep) -> ListaService:
    return ListaService(sessao)


ListaServiceDep = Annotated[ListaService, Depends(obter_lista_service)]

RESPOSTA_401 = {401: {"description": "Token ausente, inválido ou expirado"}}


def item_para_resposta(item: ItemLista, obra: ObraComResumo) -> ItemListaResposta:
    return ItemListaResposta(
        obra=obra_para_resposta(obra, item.status),
        status=item.status,
        criado_em=item.criado_em,
        atualizado_em=item.atualizado_em,
    )


@router.get(
    "",
    summary="Lista as obras do usuário, com filtro opcional por status",
    description="Ordenada pela última alteração (mais recentes primeiro).",
    responses=RESPOSTA_401,
)
def listar(
    filtros: Annotated[FiltrosLista, Query()], usuario: UsuarioAtualDep, servico: ListaServiceDep
) -> PaginaItensLista:
    itens, total = servico.listar(usuario, filtros)
    return PaginaItensLista(
        itens=[item_para_resposta(item, obra) for item, obra in itens],
        total=total,
        pagina=filtros.pagina,
        tamanho=filtros.tamanho,
    )


@router.put(
    "/{obra_id}",
    summary="Adiciona a obra à lista ou altera seu status",
    description="Retorna 201 quando a obra é adicionada e 200 quando o status é alterado.",
    responses={
        **RESPOSTA_401,
        201: {"description": "Obra adicionada à lista"},
        404: {"description": "Obra não encontrada"},
    },
)
def definir_status(
    obra_id: int,
    dados: ItemListaEntrada,
    usuario: UsuarioAtualDep,
    servico: ListaServiceDep,
    resposta: Response,
) -> ItemListaResposta:
    item, obra, criado = servico.definir_status(usuario, obra_id, dados.status)
    if criado:
        resposta.status_code = status.HTTP_201_CREATED
    return item_para_resposta(item, obra)


@router.delete(
    "/{obra_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a obra da lista",
    responses={**RESPOSTA_401, 404: {"description": "Obra não está na lista"}},
)
def remover(obra_id: int, usuario: UsuarioAtualDep, servico: ListaServiceDep) -> None:
    servico.remover(usuario, obra_id)

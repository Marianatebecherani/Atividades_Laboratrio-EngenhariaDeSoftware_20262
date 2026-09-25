from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.excecoes import (
    ConflitoDeDados,
    CredenciaisInvalidas,
    ErroDeNegocio,
    OperacaoNaoPermitida,
    RecursoNaoEncontrado,
)

STATUS_POR_ERRO: dict[type[ErroDeNegocio], int] = {
    RecursoNaoEncontrado: status.HTTP_404_NOT_FOUND,
    ConflitoDeDados: status.HTTP_409_CONFLICT,
    CredenciaisInvalidas: status.HTTP_401_UNAUTHORIZED,
    OperacaoNaoPermitida: status.HTTP_403_FORBIDDEN,
}


async def tratar_erro_de_negocio(_: Request, erro: ErroDeNegocio) -> JSONResponse:
    codigo = next(
        (codigo for tipo, codigo in STATUS_POR_ERRO.items() if isinstance(erro, tipo)),
        status.HTTP_400_BAD_REQUEST,
    )
    return JSONResponse(status_code=codigo, content={"detail": erro.mensagem})


def registrar_tratadores(app: FastAPI) -> None:
    app.add_exception_handler(ErroDeNegocio, tratar_erro_de_negocio)

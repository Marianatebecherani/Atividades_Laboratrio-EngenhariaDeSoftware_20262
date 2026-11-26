from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import obter_configuracoes
from app.core.seguranca import ler_usuario_do_token
from app.db.sessao import obter_sessao
from app.models import PapelUsuario, Usuario
from app.services.comentario_service import ComentarioService
from app.services.filmes_usuario_service import FilmesUsuarioService
from app.services.recomendacao_service import RecomendacaoService
from app.services.tmdb_service import TmdbService
from app.services.usuario_service import UsuarioService

esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SessaoDep = Annotated[Session, Depends(obter_sessao)]


def obter_usuario_service(sessao: SessaoDep) -> UsuarioService:
    return UsuarioService(sessao)


UsuarioServiceDep = Annotated[UsuarioService, Depends(obter_usuario_service)]


def obter_usuario_atual(
    token: Annotated[str, Depends(esquema_oauth2)],
    servico: UsuarioServiceDep,
) -> Usuario:
    usuario_id = ler_usuario_do_token(token)
    usuario = servico.obter(usuario_id) if usuario_id is not None else None

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


UsuarioAtualDep = Annotated[Usuario, Depends(obter_usuario_atual)]


def exigir_admin(usuario: UsuarioAtualDep) -> Usuario:
    if usuario.papel != PapelUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação permitida apenas para administradores",
        )

    return usuario


AdminDep = Annotated[Usuario, Depends(exigir_admin)]


def obter_filmes_usuario_service(sessao: SessaoDep) -> FilmesUsuarioService:
    return FilmesUsuarioService(sessao)


FilmesUsuarioServiceDep = Annotated[
    FilmesUsuarioService,
    Depends(obter_filmes_usuario_service),
]


def obter_comentario_service(sessao: SessaoDep) -> ComentarioService:
    return ComentarioService(sessao)


ComentarioServiceDep = Annotated[
    ComentarioService,
    Depends(obter_comentario_service),
]


def obter_tmdb_service(request: Request) -> TmdbService:
    # O cliente compartilhado e o cache são criados no ciclo de vida da API (app/main.py).
    return TmdbService(
        obter_configuracoes().tmdb_api_token,
        cliente=getattr(request.app.state, "cliente_tmdb", None),
        cache=getattr(request.app.state, "cache_tmdb", None),
    )


TmdbServiceDep = Annotated[
    TmdbService,
    Depends(obter_tmdb_service),
]


def obter_recomendacao_service(
    sessao: Annotated[Session, Depends(obter_sessao)],
    tmdb: Annotated[TmdbService, Depends(obter_tmdb_service)],
) -> RecomendacaoService:
    return RecomendacaoService(sessao, tmdb)


RecomendacaoServiceDep = Annotated[
    RecomendacaoService,
    Depends(obter_recomendacao_service),
]

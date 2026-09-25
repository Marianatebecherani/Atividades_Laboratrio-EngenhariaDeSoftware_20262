from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencias import UsuarioServiceDep
from app.core.config import obter_configuracoes
from app.core.seguranca import criar_token_acesso
from app.schemas.usuario import TokenResposta, UsuarioCadastro, UsuarioResposta

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/cadastro",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo usuário",
    responses={409: {"description": "E-mail já cadastrado"}},
)
def cadastrar(dados: UsuarioCadastro, servico: UsuarioServiceDep) -> UsuarioResposta:
    return servico.cadastrar(dados)


@router.post(
    "/login",
    summary="Autentica o usuário e retorna um token JWT",
    description="Informe o e-mail no campo `username` (padrão do formulário OAuth2).",
    responses={401: {"description": "E-mail ou senha incorretos"}},
)
def login(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()], servico: UsuarioServiceDep
) -> TokenResposta:
    usuario = servico.autenticar(formulario.username, formulario.password)
    return TokenResposta(
        access_token=criar_token_acesso(usuario.id),
        expira_em_minutos=obter_configuracoes().jwt_expiracao_minutos,
    )

from fastapi import APIRouter, status

from app.api.dependencias import UsuarioAtualDep, UsuarioServiceDep
from app.schemas.usuario import UsuarioAtualizacao, UsuarioExclusao, UsuarioResposta

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

RESPOSTA_401 = {401: {"description": "Token ausente, inválido ou expirado"}}


@router.get("/me", summary="Retorna o usuário autenticado", responses=RESPOSTA_401)
def obter_perfil(usuario: UsuarioAtualDep) -> UsuarioResposta:
    return usuario


@router.patch(
    "/me",
    summary="Atualiza nome, e-mail ou senha do usuário autenticado",
    description="Para alterar o e-mail ou a senha, informe também `senha_atual`.",
    responses={
        **RESPOSTA_401,
        403: {"description": "Senha atual incorreta"},
        409: {"description": "E-mail já cadastrado"},
    },
)
def atualizar_perfil(
    dados: UsuarioAtualizacao, usuario: UsuarioAtualDep, servico: UsuarioServiceDep
) -> UsuarioResposta:
    return servico.atualizar(usuario, dados)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui a conta do usuário autenticado",
    description="Remove também a lista e as avaliações do usuário. Exige a senha.",
    responses={
        **RESPOSTA_401,
        403: {"description": "Senha incorreta"},
        409: {"description": "Único administrador do sistema"},
    },
)
def excluir_conta(
    dados: UsuarioExclusao, usuario: UsuarioAtualDep, servico: UsuarioServiceDep
) -> None:
    servico.excluir(usuario, dados.senha)

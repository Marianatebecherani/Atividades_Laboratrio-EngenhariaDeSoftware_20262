from sqlalchemy.orm import Session

from app.core.excecoes import ConflitoDeDados, CredenciaisInvalidas, OperacaoNaoPermitida
from app.core.seguranca import gerar_hash_senha, verificar_senha
from app.models import PapelUsuario, Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioAtualizacao, UsuarioCadastro


class UsuarioService:
    """Regras de negócio de cadastro, autenticação e perfil de usuários."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = UsuarioRepository(sessao)

    def cadastrar(self, dados: UsuarioCadastro) -> Usuario:
        self._garantir_email_disponivel(dados.email)
        usuario = self.repositorio.adicionar(
            Usuario(
                nome=dados.nome,
                email=dados.email,
                senha_hash=gerar_hash_senha(dados.senha),
                papel=PapelUsuario.USUARIO,
            )
        )
        self.sessao.commit()
        return usuario

    def autenticar(self, email: str, senha: str) -> Usuario:
        usuario = self.repositorio.obter_por_email(email.strip().lower())
        if not verificar_senha(senha, usuario.senha_hash if usuario else None):
            raise CredenciaisInvalidas("E-mail ou senha incorretos")
        return usuario

    def obter(self, usuario_id: int) -> Usuario | None:
        return self.repositorio.obter_por_id(usuario_id)

    def atualizar(self, usuario: Usuario, dados: UsuarioAtualizacao) -> Usuario:
        if dados.senha_atual is not None and not verificar_senha(
            dados.senha_atual, usuario.senha_hash
        ):
            raise OperacaoNaoPermitida("Senha atual incorreta")

        if dados.nome is not None:
            usuario.nome = dados.nome
        if dados.email is not None and dados.email != usuario.email:
            self._garantir_email_disponivel(dados.email)
            usuario.email = dados.email
        if dados.senha_nova is not None:
            usuario.senha_hash = gerar_hash_senha(dados.senha_nova)

        self.sessao.commit()
        self.sessao.refresh(usuario)
        return usuario

    def excluir(self, usuario: Usuario, senha: str) -> None:
        if not verificar_senha(senha, usuario.senha_hash):
            raise OperacaoNaoPermitida("Senha incorreta")
        if usuario.papel == PapelUsuario.ADMIN and self.repositorio.contar_admins() == 1:
            raise ConflitoDeDados("Não é possível excluir o único administrador do sistema")

        self.repositorio.remover(usuario)
        self.sessao.commit()

    def _garantir_email_disponivel(self, email: str) -> None:
        if self.repositorio.obter_por_email(email):
            raise ConflitoDeDados("E-mail já cadastrado")

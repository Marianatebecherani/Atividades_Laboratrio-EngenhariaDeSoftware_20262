from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PapelUsuario, Usuario


class UsuarioRepository:
    """Acesso aos dados de usuários (padrão Repository)."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def obter_por_id(self, usuario_id: int) -> Usuario | None:
        return self.sessao.get(Usuario, usuario_id)

    def obter_por_email(self, email: str) -> Usuario | None:
        return self.sessao.scalar(select(Usuario).where(Usuario.email == email))

    def contar_admins(self) -> int:
        consulta = select(func.count()).where(Usuario.papel == PapelUsuario.ADMIN)
        return self.sessao.scalar(consulta)

    def adicionar(self, usuario: Usuario) -> Usuario:
        self.sessao.add(usuario)
        self.sessao.flush()
        return usuario

    def remover(self, usuario: Usuario) -> None:
        self.sessao.delete(usuario)
        self.sessao.flush()

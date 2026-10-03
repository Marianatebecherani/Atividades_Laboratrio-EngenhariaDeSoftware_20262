"""Cria o administrador inicial, se ADMIN_EMAIL e ADMIN_SENHA estiverem definidos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Configuracoes, obter_configuracoes
from app.core.seguranca import gerar_hash_senha
from app.db.sessao import SessaoLocal
from app.models import PapelUsuario, Usuario


def semear_admin(sessao: Session, configuracoes: Configuracoes) -> bool:
    if not configuracoes.admin_email or not configuracoes.admin_senha:
        return False
    if sessao.scalar(select(Usuario).where(Usuario.email == configuracoes.admin_email)):
        return False
    sessao.add(
        Usuario(
            nome=configuracoes.admin_nome,
            email=configuracoes.admin_email,
            senha_hash=gerar_hash_senha(configuracoes.admin_senha),
            papel=PapelUsuario.ADMIN,
        )
    )
    return True


def semear(sessao: Session, configuracoes: Configuracoes) -> None:
    criado = semear_admin(sessao, configuracoes)
    sessao.commit()
    if criado:
        print(f"Administrador criado: {configuracoes.admin_email}")
    elif not configuracoes.admin_email or not configuracoes.admin_senha:
        print("Administrador não criado: defina ADMIN_EMAIL e ADMIN_SENHA no .env.")


if __name__ == "__main__":
    with SessaoLocal() as sessao:
        semear(sessao, obter_configuracoes())

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Configuracoes
from app.core.seguranca import verificar_senha
from app.db.seed import semear
from app.models import PapelUsuario, Usuario


def configuracoes(**campos) -> Configuracoes:
    valores = {
        "jwt_segredo": "segredo-de-teste",
        "admin_email": "admin@teste.com",
        "admin_senha": "senha-segura",
    } | campos
    return Configuracoes(**valores)


def test_seed_cria_admin_com_senha_protegida(sessao: Session) -> None:
    semear(sessao, configuracoes())

    admin = sessao.scalar(select(Usuario).where(Usuario.email == "admin@teste.com"))
    assert admin.papel == PapelUsuario.ADMIN
    assert admin.senha_hash != "senha-segura"
    assert verificar_senha("senha-segura", admin.senha_hash)


def test_seed_sem_credenciais_nao_cria_admin(sessao: Session) -> None:
    semear(sessao, configuracoes(admin_email=None, admin_senha=None))

    assert sessao.scalar(select(func.count()).select_from(Usuario)) == 0


def test_seed_pode_ser_executado_novamente_sem_duplicar_admin(sessao: Session) -> None:
    semear(sessao, configuracoes())
    semear(sessao, configuracoes())

    assert sessao.scalar(select(func.count()).select_from(Usuario)) == 1

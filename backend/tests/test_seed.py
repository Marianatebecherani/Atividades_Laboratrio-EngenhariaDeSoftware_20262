from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Configuracoes
from app.core.seguranca import verificar_senha
from app.db.seed import GENEROS, OBRAS, semear
from app.models import Genero, Obra, PapelUsuario, Usuario


def configuracoes_com_admin() -> Configuracoes:
    return Configuracoes(admin_email="admin@teste.com", admin_senha="senha-segura")


def contar(sessao: Session, modelo) -> int:
    return sessao.scalar(select(func.count()).select_from(modelo))


def test_seed_cria_generos_obras_e_admin(sessao: Session) -> None:
    semear(sessao, configuracoes_com_admin())

    assert contar(sessao, Genero) == len(GENEROS)
    assert contar(sessao, Obra) == len(OBRAS)
    admin = sessao.scalar(select(Usuario).where(Usuario.email == "admin@teste.com"))
    assert admin.papel == PapelUsuario.ADMIN
    assert admin.senha_hash != "senha-segura"
    assert verificar_senha("senha-segura", admin.senha_hash)


def test_seed_pode_ser_executado_novamente_sem_duplicar(sessao: Session) -> None:
    semear(sessao, configuracoes_com_admin())
    semear(sessao, configuracoes_com_admin())

    assert contar(sessao, Genero) == len(GENEROS)
    assert contar(sessao, Obra) == len(OBRAS)
    assert contar(sessao, Usuario) == 1


def test_seed_sem_credenciais_nao_cria_admin(sessao: Session) -> None:
    semear(sessao, Configuracoes(admin_email=None, admin_senha=None))

    assert contar(sessao, Usuario) == 0
    assert contar(sessao, Obra) == len(OBRAS)


def test_obras_do_seed_tem_generos_associados(sessao: Session) -> None:
    semear(sessao, configuracoes_com_admin())

    interestelar = sessao.scalar(select(Obra).where(Obra.titulo == "Interestelar"))
    assert {genero.nome for genero in interestelar.generos} == {"Drama", "Ficção Científica"}

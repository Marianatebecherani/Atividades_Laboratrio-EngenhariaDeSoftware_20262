from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core.config import obter_configuracoes
from app.core.seguranca import criar_token_acesso
from app.db.sessao import obter_sessao
from app.main import app
from app.models import PapelUsuario, Usuario

DIRETORIO_BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def engine_teste() -> Iterator[Engine]:
    """Recria o esquema do banco de testes aplicando as migrações do zero."""
    url = obter_configuracoes().test_database_url
    config_alembic = Config(DIRETORIO_BACKEND / "alembic.ini")
    config_alembic.set_main_option("sqlalchemy.url", url)
    command.downgrade(config_alembic, "base")
    command.upgrade(config_alembic, "head")

    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture
def sessao(engine_teste: Engine) -> Iterator[Session]:
    """Sessão isolada: tudo o que o teste gravar é desfeito ao final."""
    with engine_teste.connect() as conexao:
        transacao = conexao.begin()
        sessao = Session(
            bind=conexao, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        yield sessao
        sessao.close()
        transacao.rollback()


@pytest.fixture
def cliente(sessao: Session) -> Iterator[TestClient]:
    app.dependency_overrides[obter_sessao] = lambda: sessao
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


def _cabecalho_para(sessao: Session, papel: PapelUsuario, email: str) -> dict[str, str]:
    usuario = Usuario(nome=papel.value.title(), email=email, senha_hash="-", papel=papel)
    sessao.add(usuario)
    sessao.flush()
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


@pytest.fixture
def cabecalho_admin(sessao: Session) -> dict[str, str]:
    """Cabeçalho de autenticação de um administrador (sem passar pelo login)."""
    return _cabecalho_para(sessao, PapelUsuario.ADMIN, "admin@exemplo.com")


@pytest.fixture
def cabecalho_usuario(sessao: Session) -> dict[str, str]:
    """Cabeçalho de autenticação de um usuário comum (sem passar pelo login)."""
    return _cabecalho_para(sessao, PapelUsuario.USUARIO, "usuario@exemplo.com")

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import obter_configuracoes
from app.db.sessao import obter_sessao
from app.main import app

engine_teste = create_engine(obter_configuracoes().test_database_url, pool_pre_ping=True)
SessaoTeste = sessionmaker(bind=engine_teste, autoflush=False, expire_on_commit=False)


@pytest.fixture
def sessao() -> Iterator[Session]:
    with SessaoTeste() as sessao:
        yield sessao


@pytest.fixture
def cliente(sessao: Session) -> Iterator[TestClient]:
    app.dependency_overrides[obter_sessao] = lambda: sessao
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.sessao import obter_sessao
from app.main import app


class SessaoIndisponivel:
    """Simula uma sessão cujo banco não responde."""

    def execute(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("conexão recusada"))


def test_saude_retorna_ok_com_banco_disponivel(cliente: TestClient) -> None:
    resposta = cliente.get("/api/v1/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_saude_retorna_503_com_banco_indisponivel(cliente: TestClient) -> None:
    app.dependency_overrides[obter_sessao] = lambda: SessaoIndisponivel()

    resposta = cliente.get("/api/v1/saude")

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "Banco de dados indisponível"}

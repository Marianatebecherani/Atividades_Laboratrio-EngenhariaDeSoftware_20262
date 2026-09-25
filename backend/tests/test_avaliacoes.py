import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Obra, TipoObra


@pytest.fixture
def obra_id(sessao: Session) -> int:
    obra = Obra(titulo="Filme", tipo=TipoObra.FILME, ano_lancamento=2000, duracao_minutos=100)
    sessao.add(obra)
    sessao.flush()
    return obra.id


def url(obra_id: int, sufixo: str = "") -> str:
    return f"/api/v1/obras/{obra_id}/avaliacoes{sufixo}"


def avaliar(cliente: TestClient, cabecalho: dict, obra_id: int, **dados):
    return cliente.put(url(obra_id, "/me"), json=dados, headers=cabecalho)


def test_avaliar_exige_autenticacao(cliente: TestClient, obra_id: int) -> None:
    assert cliente.put(url(obra_id, "/me"), json={"nota": 5}).status_code == 401


def test_criar_retorna_201_e_editar_retorna_200(
    cliente: TestClient, cabecalho_usuario: dict, obra_id: int
) -> None:
    criada = avaliar(cliente, cabecalho_usuario, obra_id, nota=4, comentario="  Muito bom.  ")
    editada = avaliar(cliente, cabecalho_usuario, obra_id, nota=5, comentario="")

    assert criada.status_code == 201
    assert criada.json()["comentario"] == "Muito bom."
    assert criada.json()["usuario"]["nome"] == "Usuario"
    assert editada.status_code == 200
    assert editada.json()["id"] == criada.json()["id"]
    assert editada.json()["nota"] == 5
    assert editada.json()["comentario"] is None


@pytest.mark.parametrize(
    "dados",
    [{"nota": 0}, {"nota": 6}, {"nota": 4.5}, {}, {"nota": 3, "comentario": "x" * 2001}],
)
def test_avaliacao_invalida_retorna_422(
    cliente: TestClient, cabecalho_usuario: dict, obra_id: int, dados: dict
) -> None:
    assert avaliar(cliente, cabecalho_usuario, obra_id, **dados).status_code == 422


def test_avaliar_obra_inexistente_retorna_404(cliente: TestClient, cabecalho_usuario: dict) -> None:
    assert avaliar(cliente, cabecalho_usuario, 999, nota=5).status_code == 404
    assert cliente.get(url(999)).status_code == 404


def test_listagem_publica_e_media_da_obra(
    cliente: TestClient, cabecalho_usuario: dict, cabecalho_admin: dict, obra_id: int
) -> None:
    avaliar(cliente, cabecalho_usuario, obra_id, nota=4, comentario="Bom")
    avaliar(cliente, cabecalho_admin, obra_id, nota=5)

    listagem = cliente.get(url(obra_id))
    obra = cliente.get(f"/api/v1/obras/{obra_id}").json()

    assert listagem.status_code == 200
    assert listagem.json()["total"] == 2
    assert {a["usuario"]["nome"] for a in listagem.json()["itens"]} == {"Usuario", "Admin"}
    assert obra["media_notas"] == 4.5
    assert obra["total_avaliacoes"] == 2


def test_media_arredondada_com_uma_casa(
    cliente: TestClient,
    cabecalho_usuario: dict,
    cabecalho_admin: dict,
    sessao: Session,
    obra_id: int,
) -> None:
    from app.models import Avaliacao, Usuario

    terceiro = Usuario(nome="Terceiro", email="terceiro@exemplo.com", senha_hash="-")
    sessao.add(terceiro)
    sessao.flush()
    sessao.add(Avaliacao(usuario_id=terceiro.id, obra_id=obra_id, nota=4))
    avaliar(cliente, cabecalho_usuario, obra_id, nota=5)
    avaliar(cliente, cabecalho_admin, obra_id, nota=5)

    assert cliente.get(f"/api/v1/obras/{obra_id}").json()["media_notas"] == 4.7


def test_remover_minha_avaliacao(
    cliente: TestClient, cabecalho_usuario: dict, obra_id: int
) -> None:
    avaliar(cliente, cabecalho_usuario, obra_id, nota=3)

    remocao = cliente.delete(url(obra_id, "/me"), headers=cabecalho_usuario)
    repetida = cliente.delete(url(obra_id, "/me"), headers=cabecalho_usuario)

    assert remocao.status_code == 204
    assert repetida.status_code == 404
    assert cliente.get(url(obra_id)).json()["total"] == 0


def test_admin_modera_avaliacao_de_outro_usuario(
    cliente: TestClient, cabecalho_usuario: dict, cabecalho_admin: dict, obra_id: int
) -> None:
    avaliacao_id = avaliar(
        cliente, cabecalho_usuario, obra_id, nota=1, comentario="Ofensivo"
    ).json()["id"]

    moderacao = cliente.delete(f"/api/v1/avaliacoes/{avaliacao_id}", headers=cabecalho_admin)

    assert moderacao.status_code == 204
    assert cliente.get(url(obra_id)).json()["total"] == 0
    assert (
        cliente.delete(f"/api/v1/avaliacoes/{avaliacao_id}", headers=cabecalho_admin).status_code
        == 404
    )


def test_usuario_comum_nao_modera(
    cliente: TestClient, cabecalho_usuario: dict, obra_id: int
) -> None:
    avaliacao_id = avaliar(cliente, cabecalho_usuario, obra_id, nota=4).json()["id"]

    resposta = cliente.delete(f"/api/v1/avaliacoes/{avaliacao_id}", headers=cabecalho_usuario)

    assert resposta.status_code == 403

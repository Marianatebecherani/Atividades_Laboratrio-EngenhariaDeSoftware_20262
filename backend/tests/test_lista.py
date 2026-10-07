import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Obra, TipoObra

URL = "/api/v1/usuarios/me/lista"


@pytest.fixture
def obras(sessao: Session) -> list[int]:
    lista = [
        Obra(titulo=titulo, tipo=TipoObra.FILME, ano_lancamento=2000, duracao_minutos=100)
        for titulo in ("Filme A", "Filme B", "Filme C")
    ]
    sessao.add_all(lista)
    sessao.flush()
    return [obra.id for obra in lista]


def definir(cliente: TestClient, cabecalho: dict, obra_id: int, status: str):
    return cliente.put(f"{URL}/{obra_id}", json={"status": status}, headers=cabecalho)


def test_lista_exige_autenticacao(cliente: TestClient) -> None:
    assert cliente.get(URL).status_code == 401
    assert cliente.put(f"{URL}/1", json={"status": "assistido"}).status_code == 401


def test_adicionar_retorna_201_e_alterar_retorna_200(
    cliente: TestClient, cabecalho_usuario: dict, obras: list[int]
) -> None:
    adicionado = definir(cliente, cabecalho_usuario, obras[0], "quero_assistir")
    alterado = definir(cliente, cabecalho_usuario, obras[0], "assistindo")

    assert adicionado.status_code == 201
    assert alterado.status_code == 200
    assert alterado.json()["status"] == "assistindo"
    assert alterado.json()["obra"]["titulo"] == "Filme A"
    assert alterado.json()["obra"]["meu_status"] == "assistindo"
    assert cliente.get(URL, headers=cabecalho_usuario).json()["total"] == 1


def test_filtrar_lista_por_status(
    cliente: TestClient, cabecalho_usuario: dict, obras: list[int]
) -> None:
    definir(cliente, cabecalho_usuario, obras[0], "assistido")
    definir(cliente, cabecalho_usuario, obras[1], "quero_assistir")
    definir(cliente, cabecalho_usuario, obras[2], "assistido")

    assistidos = cliente.get(URL, params={"status": "assistido"}, headers=cabecalho_usuario)

    assert assistidos.status_code == 200
    assert assistidos.json()["total"] == 2
    assert {item["obra"]["titulo"] for item in assistidos.json()["itens"]} == {"Filme A", "Filme C"}


def test_lista_e_individual_por_usuario(
    cliente: TestClient, cabecalho_usuario: dict, cabecalho_admin: dict, obras: list[int]
) -> None:
    definir(cliente, cabecalho_usuario, obras[0], "assistido")

    assert cliente.get(URL, headers=cabecalho_admin).json()["total"] == 0


def test_remover_da_lista(cliente: TestClient, cabecalho_usuario: dict, obras: list[int]) -> None:
    definir(cliente, cabecalho_usuario, obras[0], "assistido")

    remocao = cliente.delete(f"{URL}/{obras[0]}", headers=cabecalho_usuario)
    remocao_repetida = cliente.delete(f"{URL}/{obras[0]}", headers=cabecalho_usuario)

    assert remocao.status_code == 204
    assert remocao_repetida.status_code == 404
    assert cliente.get(URL, headers=cabecalho_usuario).json()["total"] == 0


def test_obra_inexistente_ou_status_invalido(cliente: TestClient, cabecalho_usuario: dict) -> None:
    assert definir(cliente, cabecalho_usuario, 999, "assistido").status_code == 404
    assert (
        cliente.put(f"{URL}/999", json={"status": "visto"}, headers=cabecalho_usuario).status_code
        == 422
    )


def test_meu_status_na_busca_e_no_detalhe_de_obras(
    cliente: TestClient, cabecalho_usuario: dict, obras: list[int]
) -> None:
    definir(cliente, cabecalho_usuario, obras[1], "assistindo")

    busca = cliente.get(
        "/api/v1/obras", params={"ordenar_por": "titulo"}, headers=cabecalho_usuario
    )
    detalhe = cliente.get(f"/api/v1/obras/{obras[1]}", headers=cabecalho_usuario)

    assert [obra["meu_status"] for obra in busca.json()["itens"]] == [None, "assistindo", None]
    assert detalhe.json()["meu_status"] == "assistindo"


def test_meu_status_e_nulo_sem_token_ou_com_token_invalido(
    cliente: TestClient, cabecalho_usuario: dict, obras: list[int]
) -> None:
    definir(cliente, cabecalho_usuario, obras[0], "assistido")

    anonimo = cliente.get(f"/api/v1/obras/{obras[0]}")
    token_invalido = cliente.get(
        f"/api/v1/obras/{obras[0]}", headers={"Authorization": "Bearer invalido"}
    )

    assert anonimo.status_code == 200
    assert anonimo.json()["meu_status"] is None
    assert token_invalido.status_code == 200
    assert token_invalido.json()["meu_status"] is None

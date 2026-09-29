import pytest
from fastapi.testclient import TestClient

URL = "/api/v1/generos"


def criar(cliente: TestClient, cabecalho: dict, nome: str) -> dict:
    resposta = cliente.post(URL, json={"nome": nome}, headers=cabecalho)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_listagem_e_publica_e_ordenada_em_portugues(
    cliente: TestClient, cabecalho_admin: dict
) -> None:
    for nome in ("Aventura", "Ação", "Drama", "Ficção científica"):
        criar(cliente, cabecalho_admin, nome)

    resposta = cliente.get(URL)

    assert resposta.status_code == 200
    assert [g["nome"] for g in resposta.json()] == [
        "Ação",
        "Aventura",
        "Drama",
        "Ficção científica",
    ]


def test_admin_cria_renomeia_e_exclui_genero(cliente: TestClient, cabecalho_admin: dict) -> None:
    genero = criar(cliente, cabecalho_admin, "  Suspense  ")
    assert genero["nome"] == "Suspense"

    renomeado = cliente.put(
        f"{URL}/{genero['id']}", json={"nome": "Thriller"}, headers=cabecalho_admin
    )
    assert renomeado.status_code == 200
    assert renomeado.json() == {"id": genero["id"], "nome": "Thriller"}

    assert cliente.delete(f"{URL}/{genero['id']}", headers=cabecalho_admin).status_code == 204
    assert cliente.get(URL).json() == []


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [("post", ""), ("put", "/1"), ("delete", "/1")],
)
def test_usuario_comum_nao_altera_generos(
    cliente: TestClient, cabecalho_usuario: dict, metodo: str, caminho: str
) -> None:
    kwargs = {"json": {"nome": "Drama"}} if metodo != "delete" else {}

    resposta = getattr(cliente, metodo)(f"{URL}{caminho}", headers=cabecalho_usuario, **kwargs)

    assert resposta.status_code == 403


def test_alterar_genero_sem_token_retorna_401(cliente: TestClient) -> None:
    assert cliente.post(URL, json={"nome": "Drama"}).status_code == 401


def test_nome_repetido_ignorando_maiusculas_retorna_409(
    cliente: TestClient, cabecalho_admin: dict
) -> None:
    criar(cliente, cabecalho_admin, "Drama")
    outro = criar(cliente, cabecalho_admin, "Terror")

    duplicado = cliente.post(URL, json={"nome": "DRAMA"}, headers=cabecalho_admin)
    renomear_para_existente = cliente.put(
        f"{URL}/{outro['id']}", json={"nome": "drama"}, headers=cabecalho_admin
    )

    assert duplicado.status_code == 409
    assert renomear_para_existente.status_code == 409


def test_excluir_genero_em_uso_retorna_409(cliente: TestClient, cabecalho_admin: dict) -> None:
    genero = criar(cliente, cabecalho_admin, "Drama")
    cliente.post(
        "/api/v1/obras",
        json={
            "titulo": "Filme",
            "tipo": "filme",
            "ano_lancamento": 2000,
            "duracao_minutos": 100,
            "generos_ids": [genero["id"]],
        },
        headers=cabecalho_admin,
    )

    resposta = cliente.delete(f"{URL}/{genero['id']}", headers=cabecalho_admin)

    assert resposta.status_code == 409
    assert "1 obra" in resposta.json()["detail"]


def test_genero_inexistente_retorna_404(cliente: TestClient, cabecalho_admin: dict) -> None:
    assert cliente.put(f"{URL}/999", json={"nome": "X"}, headers=cabecalho_admin).status_code == 404
    assert cliente.delete(f"{URL}/999", headers=cabecalho_admin).status_code == 404

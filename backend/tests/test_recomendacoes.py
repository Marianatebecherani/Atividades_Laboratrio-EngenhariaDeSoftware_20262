import httpx
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencias import obter_tmdb_service
from app.main import app
from app.services.tmdb_service import TmdbService


def filme_detalhado(tmdb_id: int, genero_id: int) -> dict:
    return {
        "id": tmdb_id,
        "title": f"Filme {tmdb_id}",
        "original_title": f"Movie {tmdb_id}",
        "overview": "Sinopse de teste",
        "release_date": "2024-01-01",
        "poster_path": None,
        "backdrop_path": None,
        "original_language": "en",
        "vote_average": 8.0,
        "vote_count": 100,
        "popularity": 50.0,
        "genres": [{"id": genero_id, "name": "Ação"}],
        "credits": {"cast": [], "crew": []},
    }


def filme_discover(tmdb_id: int, genero_id: int) -> dict:
    return {
        "id": tmdb_id,
        "title": f"Recomendado {tmdb_id}",
        "original_title": f"Recommended {tmdb_id}",
        "overview": "Sinopse de recomendação",
        "release_date": "2024-01-01",
        "poster_path": None,
        "backdrop_path": None,
        "original_language": "en",
        "vote_average": 8.5,
        "vote_count": 200,
        "popularity": 80.0,
        "genre_ids": [genero_id],
    }


def configurar_tmdb(
    cliente: TestClient,
    filmes: dict[int, int],
    recomendacoes: list[dict],
) -> None:
    def responder(requisicao: httpx.Request) -> httpx.Response:
        if requisicao.url.path.startswith("/3/movie/"):
            tmdb_id = int(requisicao.url.path.split("/")[-1])
            genero_id = filmes[tmdb_id]
            return httpx.Response(
                200,
                json=filme_detalhado(tmdb_id, genero_id),
            )

        if requisicao.url.path == "/3/discover/movie":
            return httpx.Response(
                200,
                json={
                    "page": 1,
                    "total_pages": 1,
                    "total_results": len(recomendacoes),
                    "results": recomendacoes,
                },
            )

        return httpx.Response(404)

    app.dependency_overrides[obter_tmdb_service] = lambda: TmdbService(
        SecretStr("token-de-teste"),
        httpx.MockTransport(responder),
    )


def test_recomendacoes_consideram_avaliacoes_e_excluem_filmes_avaliados(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    cliente.put(
        "/api/v1/usuarios/me/filmes/100/lista",
        json={"status": "assistido"},
        headers=cabecalho_usuario,
    )
    cliente.put(
        "/api/v1/usuarios/me/filmes/100/avaliacao",
        json={"nota": 5},
        headers=cabecalho_usuario,
    )

    configurar_tmdb(
        cliente,
        {100: 28},
        [
            filme_discover(100, 28),
            filme_discover(200, 28),
            filme_discover(300, 28),
        ],
    )

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 2

    ids = [item["tmdb_id"] for item in resposta.json()["itens"]]
    assert 100 not in ids
    assert set(ids) == {200, 300}


def test_recomendacoes_excluem_filmes_assistidos(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    cliente.put(
        "/api/v1/usuarios/me/filmes/100/lista",
        json={"status": "assistido"},
        headers=cabecalho_usuario,
    )
    cliente.put(
        "/api/v1/usuarios/me/filmes/101/avaliacao",
        json={"nota": 5},
        headers=cabecalho_usuario,
    )

    configurar_tmdb(
        cliente,
        {101: 28},
        [
            filme_discover(100, 28),
            filme_discover(200, 28),
        ],
    )

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    ids = [item["tmdb_id"] for item in resposta.json()["itens"]]
    assert 100 not in ids
    assert 200 in ids


def test_usuario_sem_avaliacoes_recebe_lista_vazia(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    assert resposta.json() == {"itens": [], "total": 0}


def test_recomendacoes_respeitam_limite(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    cliente.put(
        "/api/v1/usuarios/me/filmes/100/avaliacao",
        json={"nota": 5},
        headers=cabecalho_usuario,
    )

    configurar_tmdb(
        cliente,
        {100: 28},
        [
            filme_discover(200, 28),
            filme_discover(201, 28),
            filme_discover(202, 28),
        ],
    )

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes?limite=2",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 2
    assert len(resposta.json()["itens"]) == 2


def test_recomendacoes_exigem_autenticacao(cliente: TestClient) -> None:
    resposta = cliente.get("/api/v1/usuarios/me/recomendacoes")

    assert resposta.status_code == 401


def test_recomendacoes_rejeitam_limite_invalido(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes?limite=100",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 422

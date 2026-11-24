from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencias import obter_tmdb_service
from app.main import app
from app.services.tmdb_service import TmdbService

GENEROS_TMDB = [{"id": 28, "name": "Ação"}, {"id": 18, "name": "Drama"}]


@pytest.fixture(autouse=True)
def limpar_cache_de_generos() -> Iterator[None]:
    """O cache de gêneros é da classe; zerá-lo evita que um teste interfira em outro."""
    TmdbService._cache_generos = None
    TmdbService._cache_generos_expira_em = 0
    yield
    TmdbService._cache_generos = None
    TmdbService._cache_generos_expira_em = 0


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


def pagina_tmdb(resultados: list[dict]) -> dict:
    return {
        "page": 1,
        "total_pages": 1,
        "total_results": len(resultados),
        "results": resultados,
    }


def configurar_tmdb(
    cliente: TestClient,
    filmes: dict[int, int],
    recomendacoes: list[dict],
    populares: list[dict] | None = None,
    similares: dict[int, list[dict]] | None = None,
    generos_disponiveis: bool = True,
) -> None:
    def responder(requisicao: httpx.Request) -> httpx.Response:
        if requisicao.url.path == "/3/genre/movie/list":
            if not generos_disponiveis:
                return httpx.Response(503)
            return httpx.Response(200, json={"genres": GENEROS_TMDB})

        if requisicao.url.path == "/3/movie/popular":
            return httpx.Response(200, json=pagina_tmdb(populares or []))

        if requisicao.url.path.startswith("/3/movie/"):
            tmdb_id = int(requisicao.url.path.split("/")[-1])
            genero_id = filmes[tmdb_id]
            dados = filme_detalhado(tmdb_id, genero_id)

            if "recommendations" in requisicao.url.params.get("append_to_response", ""):
                dados["recommendations"] = pagina_tmdb((similares or {}).get(tmdb_id, []))

            return httpx.Response(200, json=dados)

        if requisicao.url.path == "/3/discover/movie":
            return httpx.Response(200, json=pagina_tmdb(recomendacoes))

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


def test_usuario_sem_avaliacoes_recebe_filmes_populares(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    configurar_tmdb(cliente, {}, [], populares=[filme_discover(400, 28)])

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    assert resposta.json()["estrategia"] == "populares"
    assert [item["tmdb_id"] for item in resposta.json()["itens"]] == [400]


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


def avaliar(cliente: TestClient, cabecalho: dict[str, str], tmdb_id: int, nota: int) -> None:
    resposta = cliente.put(
        f"/api/v1/usuarios/me/filmes/{tmdb_id}/avaliacao",
        json={"nota": nota},
        headers=cabecalho,
    )
    assert resposta.status_code == 200


def test_recomendacoes_rejeitam_estrategia_invalida(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes?estrategia=aleatoria",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 422


def test_perfil_e_a_estrategia_padrao_e_explica_o_motivo_pelos_generos(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    avaliar(cliente, cabecalho_usuario, 100, 5)
    configurar_tmdb(cliente, {100: 28}, [filme_discover(200, 28)])

    resposta = cliente.get("/api/v1/usuarios/me/recomendacoes", headers=cabecalho_usuario)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["estrategia"] == "perfil"
    assert [item["tmdb_id"] for item in corpo["itens"]] == [200]
    assert corpo["itens"][0]["motivo"] == "Porque você gosta de Ação"


def test_perfil_usa_motivo_generico_quando_o_tmdb_nao_informa_os_generos(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    avaliar(cliente, cabecalho_usuario, 100, 5)
    configurar_tmdb(cliente, {100: 28}, [filme_discover(200, 28)], generos_disponiveis=False)

    resposta = cliente.get("/api/v1/usuarios/me/recomendacoes", headers=cabecalho_usuario)

    assert resposta.status_code == 200
    assert resposta.json()["itens"][0]["motivo"] == "Combina com os gêneros que você avalia bem"


def test_perfil_sem_afinidade_positiva_usa_populares(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    avaliar(cliente, cabecalho_usuario, 100, 1)
    configurar_tmdb(
        cliente, {100: 28}, [filme_discover(200, 28)], populares=[filme_discover(400, 18)]
    )

    resposta = cliente.get("/api/v1/usuarios/me/recomendacoes", headers=cabecalho_usuario)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["estrategia"] == "populares"
    assert [item["tmdb_id"] for item in corpo["itens"]] == [400]
    assert corpo["itens"][0]["motivo"] == "Em alta no TMDb"


def test_similares_priorizam_filmes_indicados_pelos_mais_bem_avaliados(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    avaliar(cliente, cabecalho_usuario, 100, 5)
    avaliar(cliente, cabecalho_usuario, 101, 4)
    avaliar(cliente, cabecalho_usuario, 102, 2)
    configurar_tmdb(
        cliente,
        {100: 28, 101: 18, 102: 28},
        [],
        similares={
            100: [filme_discover(300, 28), filme_discover(301, 28)],
            101: [filme_discover(100, 28), filme_discover(301, 18), filme_discover(302, 18)],
            102: [filme_discover(303, 28)],
        },
    )

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes?estrategia=similares",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["estrategia"] == "similares"
    # 301 foi indicado pelas duas bases; 100 já foi avaliado; 102 (nota 2) não é base.
    assert [item["tmdb_id"] for item in corpo["itens"]] == [301, 300, 302]
    motivos = {item["tmdb_id"]: item["motivo"] for item in corpo["itens"]}
    assert motivos == {
        301: "Parecido com Filme 100",
        300: "Parecido com Filme 100",
        302: "Parecido com Filme 101",
    }


def test_similares_sem_filmes_com_nota_alta_usa_populares(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    avaliar(cliente, cabecalho_usuario, 100, 3)
    configurar_tmdb(cliente, {100: 28}, [], populares=[filme_discover(400, 18)])

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes?estrategia=similares",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    assert resposta.json()["estrategia"] == "populares"


def test_populares_excluem_filmes_avaliados_e_assistidos(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
) -> None:
    avaliar(cliente, cabecalho_usuario, 100, 4)
    cliente.put(
        "/api/v1/usuarios/me/filmes/101/lista",
        json={"status": "assistido"},
        headers=cabecalho_usuario,
    )
    configurar_tmdb(
        cliente,
        {},
        [],
        populares=[filme_discover(100, 28), filme_discover(101, 28), filme_discover(102, 18)],
    )

    resposta = cliente.get(
        "/api/v1/usuarios/me/recomendacoes?estrategia=populares&limite=5",
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["estrategia"] == "populares"
    assert [item["tmdb_id"] for item in corpo["itens"]] == [102]
    assert corpo["itens"][0]["motivo"] == "Em alta no TMDb"

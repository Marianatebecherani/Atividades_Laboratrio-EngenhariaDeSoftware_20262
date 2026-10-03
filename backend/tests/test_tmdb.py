from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.filmes import obter_tmdb_service
from app.main import app
from app.services.tmdb_service import TmdbService

FILME_TMDB = {
    "id": 27205,
    "title": "A Origem",
    "original_title": "Inception",
    "overview": "Um ladrão invade sonhos para roubar segredos.",
    "release_date": "2010-07-15",
    "poster_path": "/poster.jpg",
    "backdrop_path": "/backdrop.jpg",
    "original_language": "en",
    "vote_average": 8.4,
    "vote_count": 35000,
    "popularity": 52.5,
    "genres": [{"id": 28, "name": "Ação"}],
    "credits": {
        "cast": [
            {"id": 1, "name": "Ator Teste", "character": "Herói", "profile_path": "/ator.jpg"}
        ],
        "crew": [
            {
                "id": 2,
                "name": "Diretora Teste",
                "department": "Directing",
                "job": "Director",
                "profile_path": None,
            },
            {
                "id": 3,
                "name": "Roteirista Teste",
                "department": "Writing",
                "job": "Writer",
                "profile_path": None,
            },
        ],
    },
}


@pytest.fixture
def cliente_tmdb() -> Iterator[TestClient]:
    overrides_anteriores = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    TmdbService._cache_generos = None
    TmdbService._cache_generos_expira_em = 0
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
    app.dependency_overrides.update(overrides_anteriores)
    TmdbService._cache_generos = None
    TmdbService._cache_generos_expira_em = 0


def configurar_service(cliente: TestClient, service: TmdbService) -> None:
    app.dependency_overrides[obter_tmdb_service] = lambda: service


def test_buscar_filmes_envia_auth_idioma_e_preserva_tmdb_id(
    cliente_tmdb: TestClient,
) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 2, "total_pages": 4, "total_results": 31, "results": [FILME_TMDB]},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/buscar", params={"query": "Batman", "page": 2})

    assert resposta.status_code == 200
    assert resposta.json()["resultados"][0]["tmdb_id"] == 27205
    assert resposta.json()["resultados"][0]["poster_url"] == (
        "https://image.tmdb.org/t/p/w500/poster.jpg"
    )
    assert requisicoes[0].url.path == "/3/search/movie"
    assert dict(requisicoes[0].url.params) == {
        "query": "Batman",
        "language": "pt-BR",
        "page": "2",
    }
    assert requisicoes[0].headers["Authorization"] == "Bearer token-de-teste"
    assert requisicoes[0].headers["Accept"] == "application/json"
    assert "token-de-teste" not in resposta.text


def test_detalhes_busca_por_tmdb_id(cliente_tmdb: TestClient) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(200, json=FILME_TMDB)

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/27205")

    assert resposta.status_code == 200
    assert resposta.json()["tmdb_id"] == 27205
    assert resposta.json()["data_lancamento"] == "2010-07-15"
    assert requisicoes[0].url.path == "/3/movie/27205"
    assert requisicoes[0].url.params["language"] == "pt-BR"
    assert requisicoes[0].url.params["append_to_response"] == "credits"
    assert resposta.json()["diretor"] == "Diretora Teste"
    assert resposta.json()["elenco"][0]["nome"] == "Ator Teste"
    assert resposta.json()["equipe_principal"][1]["funcao"] == "Writer"


@pytest.mark.parametrize(
    ("rota", "caminho_tmdb"),
    [
        ("populares", "/3/movie/popular"),
        ("top-rated", "/3/movie/top_rated"),
        ("now-playing", "/3/movie/now_playing"),
        ("upcoming", "/3/movie/upcoming"),
    ],
)
def test_listas_tmdb_preservam_paginacao_e_categoria(
    cliente_tmdb: TestClient, rota: str, caminho_tmdb: str
) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 2, "total_pages": 3, "total_results": 41, "results": [FILME_TMDB]},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get(f"/api/v1/filmes/{rota}", params={"page": 2})

    assert resposta.status_code == 200
    assert resposta.json()["pagina"] == 2
    assert resposta.json()["total_paginas"] == 3
    assert resposta.json()["total_resultados"] == 41
    assert requisicoes[0].url.path == caminho_tmdb
    assert requisicoes[0].url.params["page"] == "2"
    assert requisicoes[0].url.params["language"] == "pt-BR"


def test_discover_mapeia_filtros_para_parametros_oficiais(cliente_tmdb: TestClient) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 1, "total_pages": 1, "total_results": 1, "results": [FILME_TMDB]},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get(
        "/api/v1/filmes/discover",
        params={
            "genre_id": 28,
            "year": 2025,
            "release_date_gte": "2025-01-01",
            "release_date_lte": "2025-12-31",
            "vote_average_gte": 7.5,
            "language": "pt-BR",
            "page": 3,
        },
    )

    assert resposta.status_code == 200
    assert requisicoes[0].url.path == "/3/discover/movie"
    assert dict(requisicoes[0].url.params) == {
        "language": "pt-BR",
        "page": "3",
        "with_genres": "28",
        "year": "2025",
        "release_date.gte": "2025-01-01",
        "release_date.lte": "2025-12-31",
        "vote_average.gte": "7.5",
        "sort_by": "popularity.desc",
    }


def test_discover_combina_filtros_com_paginacao_e_idioma(cliente_tmdb: TestClient) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 2, "total_pages": 4, "total_results": 65, "results": [FILME_TMDB]},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get(
        "/api/v1/filmes/discover",
        params={
            "genre_ids": "28,12",
            "genre_operator": "OR",
            "year": 2024,
            "release_date_from": "2024-01-01",
            "release_date_to": "2024-12-31",
            "min_rating": 7,
            "max_rating": 9.5,
            "language": "en-US",
            "sort_by": "vote_average.desc",
            "page": 2,
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["pagina"] == 2
    assert resposta.json()["total_paginas"] == 4
    assert resposta.json()["total_resultados"] == 65
    assert dict(requisicoes[0].url.params) == {
        "language": "en-US",
        "page": "2",
        "sort_by": "vote_average.desc",
        "with_genres": "28|12",
        "year": "2024",
        "release_date.gte": "2024-01-01",
        "release_date.lte": "2024-12-31",
        "vote_average.gte": "7.0",
        "vote_average.lte": "9.5",
    }


def test_discover_sem_filtros_usa_defaults_tmdb(cliente_tmdb: TestClient) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 1, "total_pages": 1, "total_results": 0, "results": []},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/discover")

    assert resposta.status_code == 200
    assert dict(requisicoes[0].url.params) == {
        "language": "pt-BR",
        "page": "1",
        "sort_by": "popularity.desc",
    }


@pytest.mark.parametrize(
    "params",
    [
        {"min_rating": 8, "max_rating": 7},
        {"sort_by": "id.desc"},
        {"page": 0},
        {"language": "not_a_language"},
        {"genre_ids": "28,invalid"},
    ],
)
def test_discover_valida_intervalos_e_valores_allowlisted(
    cliente_tmdb: TestClient, params: dict
) -> None:
    resposta = cliente_tmdb.get("/api/v1/filmes/discover", params=params)

    assert resposta.status_code == 422


@pytest.mark.parametrize(
    ("operador", "with_genres"),
    [("AND", "28,12"), ("OR", "28|12")],
)
def test_discover_multiplos_generos_usa_logica_tmdb(
    cliente_tmdb: TestClient, operador: str, with_genres: str
) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 1, "total_pages": 1, "total_results": 0, "results": []},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get(
        "/api/v1/filmes/discover",
        params={"genre_ids": "28,12", "genre_operator": operador},
    )

    assert resposta.status_code == 200
    assert requisicoes[0].url.params["with_genres"] == with_genres


def test_discover_mapeia_nota_maxima_e_sort_allowlisted(cliente_tmdb: TestClient) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"page": 1, "total_pages": 1, "total_results": 0, "results": []},
        )

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get(
        "/api/v1/filmes/discover",
        params={"min_rating": 7, "max_rating": 9.5, "sort_by": "vote_average.desc"},
    )

    assert resposta.status_code == 200
    assert requisicoes[0].url.params["vote_average.gte"] == "7.0"
    assert requisicoes[0].url.params["vote_average.lte"] == "9.5"
    assert requisicoes[0].url.params["sort_by"] == "vote_average.desc"


@pytest.mark.parametrize(
    "params",
    [
        {"genre_id": 0},
        {"year": 2101},
        {"page": 0},
        {"min_rating": -1},
        {"max_rating": 10.1},
        {"min_rating": 8, "max_rating": 7},
        {"sort_by": "id.desc"},
        {"genre_ids": "28,not-an-id"},
        {"genre_id": 28, "genre_ids": "12"},
    ],
)
def test_discover_rejeita_parametros_invalidos(cliente_tmdb: TestClient, params: dict) -> None:
    resposta = cliente_tmdb.get("/api/v1/filmes/discover", params=params)

    assert resposta.status_code == 422


def test_discover_rejeita_intervalo_de_datas_invertido(cliente_tmdb: TestClient) -> None:
    resposta = cliente_tmdb.get(
        "/api/v1/filmes/discover",
        params={"release_date_gte": "2025-12-31", "release_date_lte": "2025-01-01"},
    )

    assert resposta.status_code == 422


def test_generos_tmdb_tem_cache_e_nao_colide_com_generos_locais(
    cliente_tmdb: TestClient,
) -> None:
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(200, json={"genres": [{"id": 28, "name": "Ação"}]})

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(responder)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/generos")
    segunda_resposta = cliente_tmdb.get("/api/v1/filmes/generos")

    assert resposta.status_code == 200
    assert resposta.json() == [{"id": 28, "nome": "Ação"}]
    assert segunda_resposta.status_code == 200
    assert len(requisicoes) == 1
    assert requisicoes[0].url.path == "/3/genre/movie/list"
    assert requisicoes[0].url.params["language"] == "pt-BR"


def test_token_ausente_retorna_erro_de_configuracao(cliente_tmdb: TestClient) -> None:
    configurar_service(cliente_tmdb, TmdbService(None))

    resposta = cliente_tmdb.get("/api/v1/filmes/buscar", params={"query": "Batman"})

    assert resposta.status_code == 503
    assert resposta.json() == {
        "detail": "A integração com o TMDb não está configurada no servidor."
    }


@pytest.mark.parametrize("codigo", [401, 403])
def test_erro_de_autenticacao_externa_nao_expoe_resposta(
    cliente_tmdb: TestClient, codigo: int
) -> None:
    configurar_service(
        cliente_tmdb,
        TmdbService(
            SecretStr("token-de-teste"),
            httpx.MockTransport(
                lambda _: httpx.Response(codigo, json={"error": "mensagem confidencial"})
            ),
        ),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/27205")

    assert resposta.status_code == 502
    assert resposta.json() == {"detail": "A autenticação do serviço TMDb falhou."}
    assert "confidencial" not in resposta.text


def test_filme_inexistente_retorna_404(cliente_tmdb: TestClient) -> None:
    configurar_service(
        cliente_tmdb,
        TmdbService(
            SecretStr("token-de-teste"),
            httpx.MockTransport(lambda _: httpx.Response(404, json={"status_message": "privado"})),
        ),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/999999999")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Filme não encontrado no TMDb."}


def test_limite_de_requisicoes_retorna_429(cliente_tmdb: TestClient) -> None:
    configurar_service(
        cliente_tmdb,
        TmdbService(
            SecretStr("token-de-teste"),
            httpx.MockTransport(lambda _: httpx.Response(429)),
        ),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/buscar", params={"query": "Batman"})

    assert resposta.status_code == 429
    assert resposta.json() == {"detail": "O TMDb limitou temporariamente as consultas."}


def test_timeout_retorna_504(cliente_tmdb: TestClient) -> None:
    def expirar(requisicao: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout interno")

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(expirar)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/buscar", params={"query": "Batman"})

    assert resposta.status_code == 504
    assert resposta.json() == {"detail": "O TMDb demorou demais para responder."}


def test_erro_de_conexao_retorna_502(cliente_tmdb: TestClient) -> None:
    def falhar(requisicao: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("detalhe da rede", request=requisicao)

    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(falhar)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/buscar", params={"query": "Batman"})

    assert resposta.status_code == 502
    assert resposta.json() == {"detail": "Não foi possível conectar ao TMDb."}
    assert "detalhe da rede" not in resposta.text


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, content=b"nao e json"),
        httpx.Response(200, json={"page": 1, "results": [FILME_TMDB]}),
        httpx.Response(500, json={"detail": "mensagem interna"}),
    ],
    ids=["json-invalido", "estrutura-invalida", "erro-externo"],
)
def test_resposta_invalida_ou_erro_externo_retorna_502(
    cliente_tmdb: TestClient, response: httpx.Response
) -> None:
    configurar_service(
        cliente_tmdb,
        TmdbService(SecretStr("token-de-teste"), httpx.MockTransport(lambda _: response)),
    )

    resposta = cliente_tmdb.get("/api/v1/filmes/buscar", params={"query": "Batman"})

    assert resposta.status_code == 502
    assert resposta.json()["detail"] in {
        "O TMDb não conseguiu atender à consulta.",
        "O TMDb retornou uma resposta inválida.",
    }
    assert "mensagem interna" not in resposta.text

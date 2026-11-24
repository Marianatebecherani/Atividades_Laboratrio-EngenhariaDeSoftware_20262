import asyncio
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencias import obter_tmdb_service
from app.core.excecoes import ErroTmdb
from app.main import app
from app.services.cache_tmdb import CacheTmdb
from app.services.tmdb_service import TMDB_BASE_URL, TmdbService

TOKEN = SecretStr("token-de-teste")


def filme(tmdb_id: int) -> dict:
    return {"id": tmdb_id, "title": f"Filme {tmdb_id}", "original_title": f"Movie {tmdb_id}"}


def responder_com_filme(requisicoes: list[httpx.Request]):
    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(200, json=filme(int(requisicao.url.path.split("/")[-1])))

    return responder


def test_cache_devolve_o_item_dentro_da_validade() -> None:
    cache = CacheTmdb()
    cache.guardar("chave", {"valor": 1}, validade_segundos=60)

    assert cache.obter("chave") == {"valor": 1}


def test_cache_descarta_o_item_vencido() -> None:
    cache = CacheTmdb()
    cache.guardar("chave", {"valor": 1}, validade_segundos=0)

    assert cache.obter("chave") is None
    assert len(cache) == 0


def test_cache_respeita_o_limite_descartando_os_itens_mais_antigos() -> None:
    cache = CacheTmdb(max_itens=2)
    for numero in range(3):
        cache.guardar(numero, {"valor": numero}, validade_segundos=60)

    assert len(cache) == 2
    assert cache.obter(0) is None
    assert cache.obter(2) == {"valor": 2}


def test_service_reaproveita_a_resposta_guardada_no_cache() -> None:
    requisicoes: list[httpx.Request] = []
    servico = TmdbService(
        TOKEN, httpx.MockTransport(responder_com_filme(requisicoes)), cache=CacheTmdb()
    )

    async def cenario() -> list[int]:
        filmes = [await servico.obter_filme(603), await servico.obter_filme(603)]
        filmes.append(await servico.obter_filme(604))
        return [item.tmdb_id for item in filmes]

    assert asyncio.run(cenario()) == [603, 603, 604]
    assert [requisicao.url.path for requisicao in requisicoes] == ["/3/movie/603", "/3/movie/604"]


def test_service_nao_guarda_erros_no_cache() -> None:
    respostas = iter([httpx.Response(500), httpx.Response(200, json=filme(603))])
    servico = TmdbService(TOKEN, httpx.MockTransport(lambda _: next(respostas)), cache=CacheTmdb())

    async def cenario() -> int:
        with pytest.raises(ErroTmdb):
            await servico.obter_filme(603)
        return (await servico.obter_filme(603)).tmdb_id

    assert asyncio.run(cenario()) == 603


def test_service_envia_o_token_pelo_cliente_compartilhado() -> None:
    requisicoes: list[httpx.Request] = []

    async def cenario() -> None:
        async with httpx.AsyncClient(
            base_url=TMDB_BASE_URL, transport=httpx.MockTransport(responder_com_filme(requisicoes))
        ) as cliente:
            servico = TmdbService(TOKEN, cliente=cliente)
            await servico.obter_filme(603)
            await servico.obter_filme(604)

    asyncio.run(cenario())

    assert len(requisicoes) == 2
    assert {requisicao.headers["Authorization"] for requisicao in requisicoes} == {
        "Bearer token-de-teste"
    }


def test_api_cria_e_fecha_o_cliente_e_o_cache_compartilhados() -> None:
    with TestClient(app):
        cliente_tmdb = app.state.cliente_tmdb
        servico = obter_tmdb_service(SimpleNamespace(app=app))

        assert isinstance(cliente_tmdb, httpx.AsyncClient)
        assert isinstance(app.state.cache_tmdb, CacheTmdb)
        assert servico._cliente is cliente_tmdb
        assert servico._cache is app.state.cache_tmdb

    assert cliente_tmdb.is_closed

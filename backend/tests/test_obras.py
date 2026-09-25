from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Avaliacao, Usuario

URL = "/api/v1/obras"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 32
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 32


def dados_filme(**campos) -> dict:
    return {
        "titulo": "Filme de Teste",
        "tipo": "filme",
        "ano_lancamento": 2010,
        "classificacao_indicativa": 14,
        "duracao_minutos": 120,
        "generos_ids": [],
    } | campos


@pytest.fixture
def generos(cliente: TestClient, cabecalho_admin: dict) -> dict[str, int]:
    nomes = ("Drama", "Policial", "Comédia")
    return {
        nome: cliente.post("/api/v1/generos", json={"nome": nome}, headers=cabecalho_admin).json()[
            "id"
        ]
        for nome in nomes
    }


def criar_obra(cliente: TestClient, cabecalho: dict, **campos) -> dict:
    resposta = cliente.post(URL, json=dados_filme(**campos), headers=cabecalho)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def avaliar(sessao: Session, obra_id: int, *notas: int) -> None:
    for indice, nota in enumerate(notas):
        usuario = Usuario(
            nome="Avaliador", email=f"avaliador{obra_id}-{indice}@exemplo.com", senha_hash="-"
        )
        sessao.add(usuario)
        sessao.flush()
        sessao.add(Avaliacao(usuario_id=usuario.id, obra_id=obra_id, nota=nota))
    sessao.flush()


def titulos(resposta) -> list[str]:
    return [obra["titulo"] for obra in resposta.json()["itens"]]


# Cadastro, atualização e exclusão


def test_admin_cadastra_filme_com_generos(
    cliente: TestClient, cabecalho_admin: dict, generos: dict
) -> None:
    obra = criar_obra(
        cliente,
        cabecalho_admin,
        generos_ids=[generos["Drama"], generos["Policial"], generos["Drama"]],
        sinopse="   ",
    )

    assert obra["tipo"] == "filme"
    assert {g["nome"] for g in obra["generos"]} == {"Drama", "Policial"}
    assert obra["sinopse"] is None
    assert obra["media_notas"] is None
    assert obra["total_avaliacoes"] == 0
    assert obra["url_poster"] is None


def test_admin_cadastra_serie_sem_classificacao(cliente: TestClient, cabecalho_admin: dict) -> None:
    obra = criar_obra(
        cliente,
        cabecalho_admin,
        tipo="serie",
        duracao_minutos=None,
        temporadas=3,
        classificacao_indicativa=None,
    )

    assert obra["temporadas"] == 3
    assert obra["classificacao_indicativa"] is None


@pytest.mark.parametrize(
    "campos",
    [
        pytest.param({"duracao_minutos": None}, id="filme-sem-duracao"),
        pytest.param({"tipo": "serie"}, id="serie-com-duracao-e-sem-temporadas"),
        pytest.param({"ano_lancamento": 1887}, id="ano-antigo-demais"),
        pytest.param({"ano_lancamento": date.today().year + 6}, id="ano-futuro-demais"),
        pytest.param({"classificacao_indicativa": 13}, id="classificacao-invalida"),
        pytest.param({"titulo": "  "}, id="titulo-vazio"),
        pytest.param({"generos_ids": [999]}, id="genero-inexistente"),
    ],
)
def test_cadastro_com_dados_invalidos_retorna_422(
    cliente: TestClient, cabecalho_admin: dict, campos: dict
) -> None:
    resposta = cliente.post(URL, json=dados_filme(**campos), headers=cabecalho_admin)

    assert resposta.status_code == 422


def test_usuario_comum_nao_cadastra_obra(cliente: TestClient, cabecalho_usuario: dict) -> None:
    assert cliente.post(URL, json=dados_filme(), headers=cabecalho_usuario).status_code == 403


def test_admin_atualiza_obra(cliente: TestClient, cabecalho_admin: dict, generos: dict) -> None:
    obra = criar_obra(cliente, cabecalho_admin, generos_ids=[generos["Drama"]])

    resposta = cliente.put(
        f"{URL}/{obra['id']}",
        json=dados_filme(titulo="Novo Título", generos_ids=[generos["Comédia"]]),
        headers=cabecalho_admin,
    )

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Novo Título"
    assert [g["nome"] for g in resposta.json()["generos"]] == ["Comédia"]


def test_admin_exclui_obra(cliente: TestClient, cabecalho_admin: dict) -> None:
    obra = criar_obra(cliente, cabecalho_admin)

    assert cliente.delete(f"{URL}/{obra['id']}", headers=cabecalho_admin).status_code == 204
    assert cliente.get(f"{URL}/{obra['id']}").status_code == 404


def test_obra_inexistente_retorna_404(cliente: TestClient, cabecalho_admin: dict) -> None:
    assert cliente.get(f"{URL}/999").status_code == 404
    assert cliente.put(f"{URL}/999", json=dados_filme(), headers=cabecalho_admin).status_code == 404
    assert cliente.delete(f"{URL}/999", headers=cabecalho_admin).status_code == 404


# Busca, filtros, ordenação e paginação


@pytest.fixture
def catalogo(cliente: TestClient, cabecalho_admin: dict, generos: dict, sessao: Session) -> dict:
    obras = {
        "Ação Total": dict(ano_lancamento=1995, generos_ids=[generos["Policial"]]),
        "Beleza": dict(ano_lancamento=2005, generos_ids=[generos["Drama"]]),
        "Comédia 100% Boa": dict(
            ano_lancamento=2015, generos_ids=[generos["Comédia"]], classificacao_indicativa=0
        ),
        "Drama e Crime": dict(
            ano_lancamento=2020, generos_ids=[generos["Drama"], generos["Policial"]]
        ),
    }
    ids = {
        titulo: criar_obra(cliente, cabecalho_admin, titulo=titulo, **c)["id"]
        for titulo, c in obras.items()
    }
    avaliar(sessao, ids["Beleza"], 5, 4)
    avaliar(sessao, ids["Drama e Crime"], 3)
    return ids


def test_busca_padrao_ordena_por_media_com_sem_avaliacao_no_fim(
    cliente: TestClient, catalogo: dict
) -> None:
    resposta = cliente.get(URL)

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["total"] == 4
    assert titulos(resposta)[:2] == ["Beleza", "Drama e Crime"]
    assert corpo["itens"][0]["media_notas"] == 4.5
    assert corpo["itens"][0]["total_avaliacoes"] == 2


def test_busca_por_texto_ignora_maiusculas_e_trata_curingas(
    cliente: TestClient, catalogo: dict
) -> None:
    assert titulos(cliente.get(URL, params={"texto": "DRAMA"})) == ["Drama e Crime"]
    assert titulos(cliente.get(URL, params={"texto": "100%"})) == ["Comédia 100% Boa"]
    assert cliente.get(URL, params={"texto": "_"}).json()["total"] == 0


def test_filtro_por_generos_retorna_obras_com_qualquer_um(
    cliente: TestClient, catalogo: dict, generos: dict
) -> None:
    resposta = cliente.get(
        URL, params={"generos": [generos["Comédia"], generos["Policial"]], "ordenar_por": "titulo"}
    )

    assert titulos(resposta) == ["Ação Total", "Comédia 100% Boa", "Drama e Crime"]


def test_filtros_por_ano_nota_e_classificacao(cliente: TestClient, catalogo: dict) -> None:
    por_ano = cliente.get(URL, params={"ano_de": 2000, "ano_ate": 2015, "ordenar_por": "titulo"})
    por_nota = cliente.get(URL, params={"nota_minima": 4})
    por_classificacao = cliente.get(URL, params={"classificacoes": [0]})

    assert titulos(por_ano) == ["Beleza", "Comédia 100% Boa"]
    assert titulos(por_nota) == ["Beleza"]
    assert titulos(por_classificacao) == ["Comédia 100% Boa"]


def test_ordenacao_por_titulo_e_ano(cliente: TestClient, catalogo: dict) -> None:
    por_titulo = cliente.get(URL, params={"ordenar_por": "titulo"})
    por_ano_crescente = cliente.get(URL, params={"ordenar_por": "ano_lancamento", "direcao": "asc"})

    assert titulos(por_titulo) == ["Ação Total", "Beleza", "Comédia 100% Boa", "Drama e Crime"]
    assert titulos(por_ano_crescente)[0] == "Ação Total"


def test_paginacao(cliente: TestClient, catalogo: dict) -> None:
    pagina_2 = cliente.get(URL, params={"ordenar_por": "titulo", "tamanho": 3, "pagina": 2}).json()

    assert pagina_2["total"] == 4
    assert pagina_2["pagina"] == 2
    assert [obra["titulo"] for obra in pagina_2["itens"]] == ["Drama e Crime"]


@pytest.mark.parametrize("params", [{"tamanho": 101}, {"pagina": 0}, {"nota_minima": 6}])
def test_parametros_de_busca_invalidos_retornam_422(cliente: TestClient, params: dict) -> None:
    assert cliente.get(URL, params=params).status_code == 422


# Pôster


@pytest.mark.parametrize(
    ("conteudo", "tipo_mime"),
    [(PNG, "image/png"), (JPEG, "image/jpeg"), (WEBP, "image/webp")],
)
def test_admin_envia_e_baixa_poster(
    cliente: TestClient, cabecalho_admin: dict, conteudo: bytes, tipo_mime: str
) -> None:
    obra = criar_obra(cliente, cabecalho_admin)

    envio = cliente.put(
        f"{URL}/{obra['id']}/poster",
        files={"arquivo": ("qualquer-nome.bin", conteudo, "application/octet-stream")},
        headers=cabecalho_admin,
    )
    url_poster = envio.json()["url_poster"]
    download = cliente.get(url_poster)

    assert envio.status_code == 200
    assert url_poster.startswith(f"/api/v1/obras/{obra['id']}/poster?v=")
    assert download.status_code == 200
    assert download.content == conteudo
    assert download.headers["content-type"] == tipo_mime


def test_enviar_novo_poster_substitui_o_anterior(
    cliente: TestClient, cabecalho_admin: dict
) -> None:
    obra = criar_obra(cliente, cabecalho_admin)
    for conteudo in (PNG, JPEG):
        cliente.put(
            f"{URL}/{obra['id']}/poster",
            files={"arquivo": ("poster", conteudo)},
            headers=cabecalho_admin,
        )

    assert cliente.get(f"{URL}/{obra['id']}/poster").content == JPEG


def test_poster_que_nao_e_imagem_retorna_415(cliente: TestClient, cabecalho_admin: dict) -> None:
    obra = criar_obra(cliente, cabecalho_admin)

    resposta = cliente.put(
        f"{URL}/{obra['id']}/poster",
        files={"arquivo": ("falso.png", b"GIF89a conteudo", "image/png")},
        headers=cabecalho_admin,
    )

    assert resposta.status_code == 415


def test_poster_maior_que_2mb_retorna_413(cliente: TestClient, cabecalho_admin: dict) -> None:
    obra = criar_obra(cliente, cabecalho_admin)
    grande = PNG + b"\x00" * (2 * 1024 * 1024)

    resposta = cliente.put(
        f"{URL}/{obra['id']}/poster", files={"arquivo": ("g.png", grande)}, headers=cabecalho_admin
    )

    assert resposta.status_code == 413


def test_admin_remove_poster(cliente: TestClient, cabecalho_admin: dict) -> None:
    obra = criar_obra(cliente, cabecalho_admin)
    cliente.put(
        f"{URL}/{obra['id']}/poster", files={"arquivo": ("p", PNG)}, headers=cabecalho_admin
    )

    remocao = cliente.delete(f"{URL}/{obra['id']}/poster", headers=cabecalho_admin)

    assert remocao.status_code == 204
    assert cliente.get(f"{URL}/{obra['id']}/poster").status_code == 404
    assert cliente.get(f"{URL}/{obra['id']}").json()["url_poster"] is None


def test_usuario_comum_nao_envia_poster(
    cliente: TestClient, cabecalho_admin: dict, cabecalho_usuario: dict
) -> None:
    obra = criar_obra(cliente, cabecalho_admin)

    resposta = cliente.put(
        f"{URL}/{obra['id']}/poster", files={"arquivo": ("p", PNG)}, headers=cabecalho_usuario
    )

    assert resposta.status_code == 403

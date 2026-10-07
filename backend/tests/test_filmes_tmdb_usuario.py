from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Avaliacao, ItemLista, Usuario


def test_lista_e_avaliacao_tmdb_guardam_apenas_estado_do_usuario(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    tmdb_id = 27205

    resposta_lista = cliente.put(
        f"/api/v1/usuarios/me/filmes/{tmdb_id}/lista",
        json={"status": "assistido"},
        headers=cabecalho_usuario,
    )
    resposta_avaliacao = cliente.put(
        f"/api/v1/usuarios/me/filmes/{tmdb_id}/avaliacao",
        json={"nota": 5, "comentario": "Minha nota pessoal"},
        headers=cabecalho_usuario,
    )

    assert resposta_lista.status_code == 200
    assert resposta_avaliacao.status_code == 200
    assert resposta_avaliacao.json()["tmdb_id"] == tmdb_id
    assert resposta_avaliacao.json()["nota_pessoal"] == 5
    assert resposta_avaliacao.json()["comentario"] == "Minha nota pessoal"
    assert "nota_tmdb" not in resposta_avaliacao.json()


def test_estado_tmdb_e_atualizado_sem_criar_linhas_duplicadas(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
    sessao: Session,
) -> None:
    tmdb_id = 550
    url_lista = f"/api/v1/usuarios/me/filmes/{tmdb_id}/lista"
    url_avaliacao = f"/api/v1/usuarios/me/filmes/{tmdb_id}/avaliacao"

    cliente.put(url_lista, json={"status": "assistindo"}, headers=cabecalho_usuario)
    cliente.put(url_lista, json={"status": "assistido"}, headers=cabecalho_usuario)
    cliente.put(url_avaliacao, json={"nota": 3}, headers=cabecalho_usuario)
    cliente.put(url_avaliacao, json={"nota": 4}, headers=cabecalho_usuario)

    estado = cliente.get(f"/api/v1/usuarios/me/filmes/{tmdb_id}", headers=cabecalho_usuario).json()
    usuario_id = sessao.scalar(select(Usuario.id).where(Usuario.email == "usuario@exemplo.com"))

    assert estado["status"] == "assistido"
    assert estado["nota_pessoal"] == 4
    assert (
        sessao.scalar(
            select(func.count()).where(
                ItemLista.usuario_id == usuario_id, ItemLista.tmdb_id == tmdb_id
            )
        )
        == 1
    )
    assert (
        sessao.scalar(
            select(func.count()).where(
                Avaliacao.usuario_id == usuario_id, Avaliacao.tmdb_id == tmdb_id
            )
        )
        == 1
    )


def test_favoritos_tmdb_tem_post_get_delete_e_idempotencia(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    tmdb_id = 157336
    url = f"/api/v1/filmes/{tmdb_id}/favoritar"

    primeiro = cliente.post(url, headers=cabecalho_usuario)
    segundo = cliente.post(url, headers=cabecalho_usuario)
    lista = cliente.get("/api/v1/usuarios/me/favoritos", headers=cabecalho_usuario)
    estado = cliente.get(f"/api/v1/usuarios/me/filmes/{tmdb_id}", headers=cabecalho_usuario)
    removido = cliente.delete(url, headers=cabecalho_usuario)

    assert primeiro.status_code == 201
    assert primeiro.json()["tmdb_id"] == tmdb_id
    assert segundo.status_code == 200
    assert lista.status_code == 200
    assert lista.json()["total"] == 1
    assert lista.json()["itens"][0]["tmdb_id"] == tmdb_id
    assert estado.json()["favorito"] is True
    assert removido.status_code == 204
    estado_final = cliente.get(f"/api/v1/usuarios/me/filmes/{tmdb_id}", headers=cabecalho_usuario)
    assert estado_final.json()["favorito"] is False


def test_lista_paginada_agrega_status_avaliacao_e_favorito(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    tmdb_id = 550
    cliente.put(
        f"/api/v1/usuarios/me/filmes/{tmdb_id}/lista",
        json={"status": "assistido"},
        headers=cabecalho_usuario,
    )
    cliente.put(
        f"/api/v1/usuarios/me/filmes/{tmdb_id}/avaliacao",
        json={"nota": 5},
        headers=cabecalho_usuario,
    )
    cliente.post(f"/api/v1/filmes/{tmdb_id}/favoritar", headers=cabecalho_usuario)

    resposta = cliente.get(
        "/api/v1/usuarios/me/filmes?pagina=1&tamanho=10", headers=cabecalho_usuario
    )

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1
    assert resposta.json()["itens"][0] == {
        "tmdb_id": tmdb_id,
        "status": "assistido",
        "nota_pessoal": 5,
        "comentario": None,
        "favorito": True,
        "atualizado_em": resposta.json()["itens"][0]["atualizado_em"],
    }


def test_rotas_de_dados_tmdb_exigem_autenticacao(cliente: TestClient) -> None:
    assert cliente.get("/api/v1/usuarios/me/favoritos").status_code == 401
    assert cliente.get("/api/v1/usuarios/me/filmes/27205").status_code == 401
    assert (
        cliente.put(
            "/api/v1/usuarios/me/filmes/27205/lista", json={"status": "assistido"}
        ).status_code
        == 401
    )
    assert cliente.post("/api/v1/filmes/27205/favoritar").status_code == 401

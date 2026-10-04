from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.seguranca import criar_token_acesso
from app.models import Comentario, PapelUsuario, Usuario

TMDB_ID = 157336


def _cabecalho_outro_usuario(sessao: Session) -> dict[str, str]:
    usuario = Usuario(
        nome="Outro Usuário",
        email="outro@exemplo.com",
        senha_hash="-",
        papel=PapelUsuario.USUARIO,
    )
    sessao.add(usuario)
    sessao.flush()
    token = criar_token_acesso(usuario.id)
    return {"Authorization": "Bearer " + token}


def test_criar_comentario_autenticado(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    resposta = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Um dos melhores filmes de ficção científica."},
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["tmdb_id"] == TMDB_ID
    assert corpo["conteudo"] == "Um dos melhores filmes de ficção científica."
    assert corpo["usuario"]["nome"] == "Usuario"
    assert "email" not in corpo["usuario"]
    assert "senha_hash" not in corpo["usuario"]


def test_impede_criacao_sem_autenticacao(cliente: TestClient) -> None:
    resposta = cliente.post(f"/api/v1/filmes/{TMDB_ID}/comentarios", json={"conteudo": "Sem login"})
    assert resposta.status_code == 401


def test_impede_comentario_vazio(cliente: TestClient, cabecalho_usuario: dict[str, str]) -> None:
    resposta = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "   "},
        headers=cabecalho_usuario,
    )
    assert resposta.status_code == 422


def test_impede_comentario_acima_do_tamanho_maximo(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    resposta = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "a" * 2001},
        headers=cabecalho_usuario,
    )
    assert resposta.status_code == 422


def test_conteudo_e_normalizado_com_trim(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    resposta = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "  Gostei bastante  "},
        headers=cabecalho_usuario,
    )
    assert resposta.status_code == 201
    assert resposta.json()["conteudo"] == "Gostei bastante"


def test_lista_comentarios_de_um_filme(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Primeiro comentário"},
        headers=cabecalho_usuario,
    )

    resposta = cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 1
    assert corpo["itens"][0]["conteudo"] == "Primeiro comentário"


def test_lista_comentarios_sem_autenticacao_e_permitida(cliente: TestClient) -> None:
    resposta = cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios")
    assert resposta.status_code == 200


def test_separa_comentarios_por_filme(
    cliente: TestClient, cabecalho_usuario: dict[str, str]
) -> None:
    outro_tmdb_id = 550
    cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Comentário do filme A"},
        headers=cabecalho_usuario,
    )
    cliente.post(
        f"/api/v1/filmes/{outro_tmdb_id}/comentarios",
        json={"conteudo": "Comentário do filme B"},
        headers=cabecalho_usuario,
    )

    comentarios_a = cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios").json()["itens"]
    comentarios_b = cliente.get(f"/api/v1/filmes/{outro_tmdb_id}/comentarios").json()["itens"]

    assert len(comentarios_a) == 1
    assert len(comentarios_b) == 1
    assert comentarios_a[0]["conteudo"] == "Comentário do filme A"
    assert comentarios_b[0]["conteudo"] == "Comentário do filme B"


def test_pagina_comentarios(cliente: TestClient, cabecalho_usuario: dict[str, str]) -> None:
    for indice in range(3):
        cliente.post(
            f"/api/v1/filmes/{TMDB_ID}/comentarios",
            json={"conteudo": f"Comentário {indice}"},
            headers=cabecalho_usuario,
        )

    pagina_1 = cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios?pagina=1&tamanho=2").json()
    pagina_2 = cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios?pagina=2&tamanho=2").json()

    assert pagina_1["total"] == 3
    assert len(pagina_1["itens"]) == 2
    assert len(pagina_2["itens"]) == 1


def test_ordena_por_mais_recente(cliente: TestClient, cabecalho_usuario: dict[str, str]) -> None:
    cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Mais antigo"},
        headers=cabecalho_usuario,
    )
    cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Mais recente"},
        headers=cabecalho_usuario,
    )

    itens = cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios").json()["itens"]

    assert itens[0]["conteudo"] == "Mais recente"
    assert itens[1]["conteudo"] == "Mais antigo"


def test_edita_proprio_comentario(cliente: TestClient, cabecalho_usuario: dict[str, str]) -> None:
    criado = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Texto original"},
        headers=cabecalho_usuario,
    ).json()

    resposta = cliente.patch(
        f"/api/v1/comentarios/{criado['id']}",
        json={"conteudo": "Texto atualizado"},
        headers=cabecalho_usuario,
    )

    assert resposta.status_code == 200
    assert resposta.json()["conteudo"] == "Texto atualizado"


def test_impede_edicao_de_comentario_de_outro_usuario(
    cliente: TestClient, cabecalho_usuario: dict[str, str], sessao: Session
) -> None:
    criado = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Comentário do dono"},
        headers=cabecalho_usuario,
    ).json()
    cabecalho_outro = _cabecalho_outro_usuario(sessao)

    resposta = cliente.patch(
        f"/api/v1/comentarios/{criado['id']}",
        json={"conteudo": "Tentando editar"},
        headers=cabecalho_outro,
    )

    assert resposta.status_code == 403


def test_exclui_proprio_comentario(
    cliente: TestClient, cabecalho_usuario: dict[str, str], sessao: Session
) -> None:
    criado = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Para remover"},
        headers=cabecalho_usuario,
    ).json()

    resposta = cliente.delete(f"/api/v1/comentarios/{criado['id']}", headers=cabecalho_usuario)

    assert resposta.status_code == 204
    assert cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios").json()["total"] == 0
    # Exclusão lógica: o registro continua no banco para uma futura moderação.
    condicao = (Comentario.id == criado["id"]) & Comentario.removido_em.is_not(None)
    assert sessao.scalar(select(func.count()).where(condicao)) == 1


def test_impede_exclusao_de_comentario_de_outro_usuario(
    cliente: TestClient, cabecalho_usuario: dict[str, str], sessao: Session
) -> None:
    criado = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Comentário do dono"},
        headers=cabecalho_usuario,
    ).json()
    cabecalho_outro = _cabecalho_outro_usuario(sessao)

    resposta = cliente.delete(f"/api/v1/comentarios/{criado['id']}", headers=cabecalho_outro)

    assert resposta.status_code == 403
    assert cliente.get(f"/api/v1/filmes/{TMDB_ID}/comentarios").json()["total"] == 1


def test_comentario_associado_ao_usuario_correto(
    cliente: TestClient, cabecalho_usuario: dict[str, str], sessao: Session
) -> None:
    criado = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Verificando autor"},
        headers=cabecalho_usuario,
    ).json()

    usuario_id = sessao.scalar(select(Usuario.id).where(Usuario.email == "usuario@exemplo.com"))
    assert criado["usuario"]["id"] == usuario_id


def test_nao_permite_cliente_definir_autor_do_comentario(
    cliente: TestClient, cabecalho_usuario: dict[str, str], sessao: Session
) -> None:
    outro_usuario_id = sessao.scalar(select(Usuario.id)) or 0
    resposta = cliente.post(
        f"/api/v1/filmes/{TMDB_ID}/comentarios",
        json={"conteudo": "Tentando falsificar autor", "usuario_id": outro_usuario_id + 999},
        headers=cabecalho_usuario,
    )

    usuario_id = sessao.scalar(select(Usuario.id).where(Usuario.email == "usuario@exemplo.com"))
    assert resposta.status_code == 201
    assert resposta.json()["usuario"]["id"] == usuario_id

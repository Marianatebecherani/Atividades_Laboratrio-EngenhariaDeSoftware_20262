from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Avaliacao, Usuario


def test_admin_pode_moderar_avaliacao_pessoal_tmdb(
    cliente: TestClient,
    cabecalho_usuario: dict[str, str],
    cabecalho_admin: dict[str, str],
    sessao: Session,
) -> None:
    tmdb_id = 27205
    resposta = cliente.put(
        f"/api/v1/usuarios/me/filmes/{tmdb_id}/avaliacao",
        json={"nota": 4, "comentario": "Minha avaliação"},
        headers=cabecalho_usuario,
    )
    assert resposta.status_code == 200

    usuario_id = sessao.scalar(select(Usuario.id).where(Usuario.email == "usuario@exemplo.com"))
    avaliacao = sessao.scalar(
        select(Avaliacao).where(Avaliacao.usuario_id == usuario_id, Avaliacao.tmdb_id == tmdb_id)
    )
    url = f"/api/v1/avaliacoes/{avaliacao.id}"

    assert cliente.delete(url, headers=cabecalho_usuario).status_code == 403
    assert cliente.delete(url, headers=cabecalho_admin).status_code == 204
    assert sessao.scalar(select(func.count()).select_from(Avaliacao)) == 0

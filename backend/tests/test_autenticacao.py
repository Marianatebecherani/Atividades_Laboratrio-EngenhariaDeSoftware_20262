from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import obter_configuracoes
from app.core.seguranca import gerar_hash_senha
from app.models import PapelUsuario, Usuario

CADASTRO = {"nome": "Ana", "email": "ana@exemplo.com", "senha": "senha-forte"}


def cadastrar(cliente: TestClient, **campos) -> dict:
    resposta = cliente.post("/api/v1/auth/cadastro", json=CADASTRO | campos)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def fazer_login(cliente: TestClient, email: str, senha: str):
    return cliente.post("/api/v1/auth/login", data={"username": email, "password": senha})


def cabecalho(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def token_de(cliente: TestClient, email: str = "ana@exemplo.com", senha: str = "senha-forte"):
    return fazer_login(cliente, email, senha).json()["access_token"]


@pytest.fixture
def token(cliente: TestClient) -> str:
    cadastrar(cliente)
    return token_de(cliente)


# Cadastro


def test_cadastro_cria_usuario_comum_sem_expor_senha(cliente: TestClient, sessao: Session) -> None:
    corpo = cadastrar(cliente, email="Ana@Exemplo.com", nome="  Ana  ")

    assert corpo["email"] == "ana@exemplo.com"
    assert corpo["nome"] == "Ana"
    assert corpo["papel"] == "usuario"
    assert "senha" not in corpo and "senha_hash" not in corpo
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == "ana@exemplo.com"))
    assert usuario.senha_hash != "senha-forte"


def test_cadastro_com_email_existente_retorna_409(cliente: TestClient) -> None:
    cadastrar(cliente)

    resposta = cliente.post("/api/v1/auth/cadastro", json=CADASTRO | {"email": "ANA@exemplo.com"})

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "E-mail já cadastrado"


@pytest.mark.parametrize(
    "campos",
    [
        pytest.param({"senha": "1234567"}, id="senha-curta"),
        pytest.param({"email": "nao-e-email"}, id="email-invalido"),
        pytest.param({"nome": ""}, id="nome-vazio"),
    ],
)
def test_cadastro_com_dados_invalidos_retorna_422(cliente: TestClient, campos: dict) -> None:
    resposta = cliente.post("/api/v1/auth/cadastro", json=CADASTRO | campos)

    assert resposta.status_code == 422


# Login e token


def test_login_retorna_token_bearer(cliente: TestClient) -> None:
    cadastrar(cliente)

    resposta = fazer_login(cliente, "ANA@exemplo.com", "senha-forte")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["expira_em_minutos"] == 60
    assert corpo["access_token"]


@pytest.mark.parametrize(
    ("email", "senha"),
    [("ana@exemplo.com", "senha-errada"), ("ninguem@exemplo.com", "senha-forte")],
)
def test_login_com_credenciais_invalidas_retorna_401(
    cliente: TestClient, email: str, senha: str
) -> None:
    cadastrar(cliente)

    resposta = fazer_login(cliente, email, senha)

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha incorretos"


def test_perfil_exige_token(cliente: TestClient) -> None:
    assert cliente.get("/api/v1/usuarios/me").status_code == 401


def test_token_expirado_ou_adulterado_e_recusado(cliente: TestClient) -> None:
    usuario_id = cadastrar(cliente)["id"]
    configuracoes = obter_configuracoes()
    expirado = jwt.encode(
        {"sub": str(usuario_id), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        configuracoes.jwt_segredo,
        algorithm=configuracoes.jwt_algoritmo,
    )
    assinatura_falsa = jwt.encode(
        {"sub": str(usuario_id), "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "outro-segredo-qualquer-com-tamanho-suficiente",
        algorithm="HS256",
    )

    for token in (expirado, assinatura_falsa, "nao-e-um-jwt"):
        resposta = cliente.get("/api/v1/usuarios/me", headers=cabecalho(token))
        assert resposta.status_code == 401


# Perfil


def test_obter_perfil_do_usuario_autenticado(cliente: TestClient, token: str) -> None:
    resposta = cliente.get("/api/v1/usuarios/me", headers=cabecalho(token))

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "ana@exemplo.com"


def test_atualizar_nome_nao_exige_senha(cliente: TestClient, token: str) -> None:
    resposta = cliente.patch(
        "/api/v1/usuarios/me", json={"nome": "Ana Maria"}, headers=cabecalho(token)
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Ana Maria"


def test_trocar_senha_exige_senha_atual(cliente: TestClient, token: str) -> None:
    sem_senha = cliente.patch(
        "/api/v1/usuarios/me", json={"senha_nova": "nova-senha-123"}, headers=cabecalho(token)
    )
    senha_errada = cliente.patch(
        "/api/v1/usuarios/me",
        json={"senha_nova": "nova-senha-123", "senha_atual": "errada"},
        headers=cabecalho(token),
    )

    assert sem_senha.status_code == 422
    assert senha_errada.status_code == 403


def test_trocar_senha_permite_login_somente_com_a_nova(cliente: TestClient, token: str) -> None:
    resposta = cliente.patch(
        "/api/v1/usuarios/me",
        json={"senha_nova": "nova-senha-123", "senha_atual": "senha-forte"},
        headers=cabecalho(token),
    )

    assert resposta.status_code == 200
    assert fazer_login(cliente, "ana@exemplo.com", "senha-forte").status_code == 401
    assert fazer_login(cliente, "ana@exemplo.com", "nova-senha-123").status_code == 200


def test_trocar_email_para_um_ja_usado_retorna_409(cliente: TestClient, token: str) -> None:
    cadastrar(cliente, email="bia@exemplo.com")

    resposta = cliente.patch(
        "/api/v1/usuarios/me",
        json={"email": "bia@exemplo.com", "senha_atual": "senha-forte"},
        headers=cabecalho(token),
    )

    assert resposta.status_code == 409


def test_excluir_conta_exige_senha_correta(cliente: TestClient, token: str) -> None:
    resposta = cliente.request(
        "DELETE", "/api/v1/usuarios/me", json={"senha": "errada"}, headers=cabecalho(token)
    )

    assert resposta.status_code == 403


def test_excluir_conta_remove_usuario_e_invalida_token(cliente: TestClient, token: str) -> None:
    resposta = cliente.request(
        "DELETE", "/api/v1/usuarios/me", json={"senha": "senha-forte"}, headers=cabecalho(token)
    )

    assert resposta.status_code == 204
    assert cliente.get("/api/v1/usuarios/me", headers=cabecalho(token)).status_code == 401
    assert fazer_login(cliente, "ana@exemplo.com", "senha-forte").status_code == 401


def test_unico_admin_nao_pode_excluir_a_propria_conta(cliente: TestClient, sessao: Session) -> None:
    sessao.add(
        Usuario(
            nome="Admin",
            email="admin@exemplo.com",
            senha_hash=gerar_hash_senha("senha-admin"),
            papel=PapelUsuario.ADMIN,
        )
    )
    sessao.flush()
    token = token_de(cliente, "admin@exemplo.com", "senha-admin")

    resposta = cliente.request(
        "DELETE", "/api/v1/usuarios/me", json={"senha": "senha-admin"}, headers=cabecalho(token)
    )

    assert resposta.status_code == 409

"""Recomendações (padrão Strategy).

Catálogo de teste (gêneros entre parênteses):
    A (Drama, Policial)   B (Drama)   C (Policial)   D (Comédia)   E (Terror)   F (Drama, Policial)
"""

import random

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.models import Avaliacao, Genero, Obra, TipoObra, Usuario, obras_generos
from app.recomendacoes.base import EstrategiaRecomendacao, NomeEstrategia
from app.recomendacoes.estrategias import ESTRATEGIAS

URL = "/api/v1/usuarios/me/recomendacoes"
LIMITE_DESEMPENHO_MS = 800


@pytest.fixture
def catalogo(sessao: Session) -> dict[str, int]:
    generos = {nome: Genero(nome=nome) for nome in ("Drama", "Policial", "Comédia", "Terror")}
    composicao = {
        "A": ("Drama", "Policial"),
        "B": ("Drama",),
        "C": ("Policial",),
        "D": ("Comédia",),
        "E": ("Terror",),
        "F": ("Drama", "Policial"),
    }
    obras = {
        titulo: Obra(
            titulo=titulo,
            tipo=TipoObra.FILME,
            ano_lancamento=2000 + indice,
            duracao_minutos=100,
            generos=[generos[nome] for nome in nomes],
        )
        for indice, (titulo, nomes) in enumerate(composicao.items())
    }
    sessao.add_all(obras.values())
    sessao.flush()
    return {titulo: obra.id for titulo, obra in obras.items()}


def avaliar(cliente: TestClient, cabecalho: dict, obra_id: int, nota: int) -> None:
    resposta = cliente.put(
        f"/api/v1/obras/{obra_id}/avaliacoes/me", json={"nota": nota}, headers=cabecalho
    )
    assert resposta.status_code in (200, 201), resposta.text


def recomendar(cliente: TestClient, cabecalho: dict, **params) -> dict:
    resposta = cliente.get(URL, params=params, headers=cabecalho)
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


def titulos(resultado: dict) -> list[str]:
    return [item["obra"]["titulo"] for item in resultado["itens"]]


def test_recomendacoes_exigem_autenticacao(cliente: TestClient) -> None:
    assert cliente.get(URL).status_code == 401


def test_estrategias_implementam_a_mesma_interface() -> None:
    assert set(ESTRATEGIAS) == set(NomeEstrategia)
    for nome, estrategia in ESTRATEGIAS.items():
        assert issubclass(estrategia, EstrategiaRecomendacao)
        assert estrategia.nome == nome


def test_por_generos_prioriza_generos_bem_avaliados(
    cliente: TestClient, cabecalho_usuario: dict, catalogo: dict
) -> None:
    avaliar(cliente, cabecalho_usuario, catalogo["A"], 5)  # Drama +2, Policial +2
    avaliar(cliente, cabecalho_usuario, catalogo["E"], 1)  # Terror -2

    resultado = recomendar(cliente, cabecalho_usuario, estrategia="generos")

    assert resultado["estrategia"] == "generos"
    assert titulos(resultado) == ["F", "B", "C"]
    assert resultado["itens"][0]["pontuacao"] == 1.0
    assert resultado["itens"][0]["motivo"] == "Porque você gosta de Drama e Policial"
    assert resultado["itens"][1]["pontuacao"] == 0.5


def test_por_generos_considera_obras_assistidas_sem_nota(
    cliente: TestClient, cabecalho_usuario: dict, catalogo: dict
) -> None:
    cliente.put(
        f"/api/v1/usuarios/me/lista/{catalogo['A']}",
        json={"status": "assistido"},
        headers=cabecalho_usuario,
    )  # Drama +1, Policial +1

    resultado = recomendar(cliente, cabecalho_usuario)

    assert resultado["estrategia"] == "generos"
    assert titulos(resultado) == ["F", "B", "C"]


def test_por_generos_sem_generos_em_comum_usa_populares(
    cliente: TestClient, cabecalho_usuario: dict, catalogo: dict
) -> None:
    # D é a única comédia: não há outra obra do gênero para recomendar.
    avaliar(cliente, cabecalho_usuario, catalogo["D"], 5)

    resultado = recomendar(cliente, cabecalho_usuario, estrategia="generos")

    assert resultado["estrategia"] == "populares"
    assert "D" not in titulos(resultado)


def test_por_similaridade_usa_obras_com_nota_alta(
    cliente: TestClient, cabecalho_usuario: dict, catalogo: dict
) -> None:
    avaliar(cliente, cabecalho_usuario, catalogo["A"], 5)

    resultado = recomendar(cliente, cabecalho_usuario, estrategia="similares")

    assert resultado["estrategia"] == "similares"
    assert titulos(resultado) == ["F", "B", "C"]
    assert resultado["itens"][0]["motivo"] == "Parecido com A"
    assert resultado["itens"][0]["pontuacao"] == 1.0


def test_populares_ordena_por_media_e_depois_pelas_mais_recentes(
    cliente: TestClient, cabecalho_usuario: dict, cabecalho_admin: dict, catalogo: dict
) -> None:
    avaliar(cliente, cabecalho_admin, catalogo["D"], 5)
    avaliar(cliente, cabecalho_admin, catalogo["B"], 3)

    resultado = recomendar(cliente, cabecalho_usuario, estrategia="populares", limite=4)

    assert titulos(resultado) == ["D", "B", "F", "E"]
    assert (
        resultado["itens"][0]["motivo"]
        == "Bem avaliado pela comunidade (média 5.0 em 1 avaliações)"
    )
    assert resultado["itens"][2]["motivo"] == "Destaque do catálogo"


@pytest.mark.parametrize("estrategia", [None, "generos", "similares"])
def test_sem_historico_usa_populares(
    cliente: TestClient, cabecalho_usuario: dict, catalogo: dict, estrategia: str | None
) -> None:
    params = {"estrategia": estrategia} if estrategia else {}

    resultado = recomendar(cliente, cabecalho_usuario, **params)

    assert resultado["estrategia"] == "populares"
    assert len(resultado["itens"]) == 6


def test_nao_recomenda_obras_da_lista_nem_ja_avaliadas(
    cliente: TestClient, cabecalho_usuario: dict, catalogo: dict
) -> None:
    avaliar(cliente, cabecalho_usuario, catalogo["A"], 5)
    cliente.put(
        f"/api/v1/usuarios/me/lista/{catalogo['F']}",
        json={"status": "quero_assistir"},
        headers=cabecalho_usuario,
    )

    for estrategia in NomeEstrategia:
        resultado = recomendar(cliente, cabecalho_usuario, estrategia=estrategia.value)
        assert not {"A", "F"} & set(titulos(resultado)), estrategia


def test_limite_de_itens(cliente: TestClient, cabecalho_usuario: dict, catalogo: dict) -> None:
    assert len(recomendar(cliente, cabecalho_usuario, limite=2)["itens"]) == 2
    assert cliente.get(URL, params={"limite": 51}, headers=cabecalho_usuario).status_code == 422
    assert (
        cliente.get(URL, params={"estrategia": "outra"}, headers=cabecalho_usuario).status_code
        == 422
    )


def test_recomendacoes_em_menos_de_800_ms(
    cliente: TestClient, cabecalho_usuario: dict, sessao: Session
) -> None:
    """RNF: recomendações calculadas em menos de 800 ms (1000 obras, 5000 avaliações)."""
    aleatorio = random.Random(42)
    genero_ids = [
        sessao.scalar(insert(Genero).values(nome=f"Gênero {i}").returning(Genero.id))
        for i in range(20)
    ]
    obra_ids = list(
        sessao.scalars(
            insert(Obra).returning(Obra.id),
            [
                {
                    "titulo": f"Obra {i}",
                    "tipo": TipoObra.FILME,
                    "ano_lancamento": 1950 + i % 75,
                    "duracao_minutos": 90 + i % 60,
                }
                for i in range(1000)
            ],
        )
    )
    sessao.execute(
        insert(obras_generos),
        [
            {"obra_id": obra, "genero_id": genero}
            for obra in obra_ids
            for genero in aleatorio.sample(genero_ids, 3)
        ],
    )
    usuario_ids = list(
        sessao.scalars(
            insert(Usuario).returning(Usuario.id),
            [
                {"nome": f"U{i}", "email": f"u{i}@exemplo.com", "senha_hash": "-"}
                for i in range(100)
            ],
        )
    )
    sessao.execute(
        insert(Avaliacao),
        [
            {"usuario_id": usuario, "obra_id": obra, "nota": aleatorio.randint(1, 5)}
            for usuario in usuario_ids
            for obra in aleatorio.sample(obra_ids, 50)
        ],
    )
    for obra in aleatorio.sample(obra_ids, 20):
        avaliar(cliente, cabecalho_usuario, obra, aleatorio.randint(1, 5))

    for estrategia in NomeEstrategia:
        resultado = recomendar(cliente, cabecalho_usuario, estrategia=estrategia.value, limite=20)
        assert resultado["estrategia"] == estrategia.value
        assert len(resultado["itens"]) == 20
        assert resultado["tempo_ms"] < LIMITE_DESEMPENHO_MS, (estrategia, resultado["tempo_ms"])

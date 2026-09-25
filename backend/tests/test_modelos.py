"""Verifica as regras de integridade garantidas pelo próprio banco de dados."""

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Avaliacao,
    Genero,
    ItemLista,
    Obra,
    PapelUsuario,
    Poster,
    StatusLista,
    TipoObra,
    Usuario,
    obras_generos,
)


def criar_usuario(sessao: Session, email: str = "ana@exemplo.com") -> Usuario:
    usuario = Usuario(nome="Ana", email=email, senha_hash="hash")
    sessao.add(usuario)
    sessao.flush()
    return usuario


def criar_filme(sessao: Session, **campos) -> Obra:
    dados = {
        "titulo": "Filme de Teste",
        "tipo": TipoObra.FILME,
        "ano_lancamento": 2020,
        "classificacao_indicativa": 12,
        "duracao_minutos": 120,
    } | campos
    obra = Obra(**dados)
    sessao.add(obra)
    sessao.flush()
    return obra


def test_usuario_novo_recebe_papel_usuario_e_datas(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    sessao.refresh(usuario)

    assert usuario.papel == PapelUsuario.USUARIO
    assert usuario.criado_em is not None
    assert usuario.atualizado_em is not None


def test_email_de_usuario_e_unico(sessao: Session) -> None:
    criar_usuario(sessao)

    with pytest.raises(IntegrityError):
        criar_usuario(sessao)


def test_filme_sem_sinopse_e_aceito(sessao: Session) -> None:
    obra = criar_filme(sessao, sinopse=None)

    assert obra.id is not None


def test_obra_sem_classificacao_indicativa_e_aceita(sessao: Session) -> None:
    obra = criar_filme(sessao, classificacao_indicativa=None)

    assert obra.id is not None


def test_serie_com_temporadas_e_aceita(sessao: Session) -> None:
    obra = criar_filme(sessao, tipo=TipoObra.SERIE, duracao_minutos=None, temporadas=3)

    assert obra.id is not None


@pytest.mark.parametrize(
    "campos",
    [
        pytest.param({"duracao_minutos": None}, id="filme-sem-duracao"),
        pytest.param({"temporadas": 2}, id="filme-com-temporadas"),
        pytest.param(
            {"tipo": TipoObra.SERIE, "duracao_minutos": None, "temporadas": None},
            id="serie-sem-temporadas",
        ),
        pytest.param({"ano_lancamento": 1887}, id="ano-antes-de-1888"),
        pytest.param({"classificacao_indicativa": 13}, id="classificacao-invalida"),
        pytest.param({"duracao_minutos": 0}, id="duracao-zero"),
    ],
)
def test_obra_invalida_e_recusada(sessao: Session, campos: dict) -> None:
    with pytest.raises(IntegrityError):
        criar_filme(sessao, **campos)


@pytest.mark.parametrize("nota", [0, 6])
def test_nota_fora_de_1_a_5_e_recusada(sessao: Session, nota: int) -> None:
    usuario = criar_usuario(sessao)
    obra = criar_filme(sessao)
    sessao.add(Avaliacao(usuario_id=usuario.id, obra_id=obra.id, nota=nota))

    with pytest.raises(IntegrityError):
        sessao.flush()


def test_usuario_avalia_cada_obra_uma_unica_vez(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    obra = criar_filme(sessao)
    sessao.add(Avaliacao(usuario_id=usuario.id, obra_id=obra.id, nota=4))
    sessao.flush()
    sessao.add(Avaliacao(usuario_id=usuario.id, obra_id=obra.id, nota=5))

    with pytest.raises(IntegrityError):
        sessao.flush()


def test_obra_aparece_uma_unica_vez_na_lista_do_usuario(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    obra = criar_filme(sessao)
    sessao.add(ItemLista(usuario_id=usuario.id, obra_id=obra.id, status=StatusLista.ASSISTINDO))
    sessao.flush()
    sessao.add(ItemLista(usuario_id=usuario.id, obra_id=obra.id, status=StatusLista.ASSISTIDO))

    with pytest.raises(IntegrityError):
        sessao.flush()


def test_obra_pode_ter_varios_generos(sessao: Session) -> None:
    drama, crime = Genero(nome="Drama"), Genero(nome="Crime")
    obra = criar_filme(sessao, generos=[drama, crime])

    assert {genero.nome for genero in obra.generos} == {"Drama", "Crime"}


def test_excluir_genero_em_uso_e_bloqueado(sessao: Session) -> None:
    genero = Genero(nome="Terror")
    criar_filme(sessao, generos=[genero])

    with pytest.raises(IntegrityError):
        sessao.execute(delete(Genero).where(Genero.id == genero.id))


def test_excluir_obra_remove_dependentes(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    obra = criar_filme(sessao, generos=[Genero(nome="Drama")])
    obra_id = obra.id
    sessao.add_all(
        [
            Poster(obra_id=obra_id, conteudo=b"img", tipo_mime="image/png", tamanho_bytes=3),
            ItemLista(usuario_id=usuario.id, obra_id=obra_id, status=StatusLista.ASSISTIDO),
            Avaliacao(usuario_id=usuario.id, obra_id=obra_id, nota=5),
        ]
    )
    sessao.flush()

    sessao.delete(obra)
    sessao.flush()

    for tabela in (Poster, ItemLista, Avaliacao):
        assert sessao.scalar(select(func.count()).where(tabela.obra_id == obra_id)) == 0
    total_generos_da_obra = sessao.scalar(
        select(func.count()).where(obras_generos.c.obra_id == obra_id)
    )
    assert total_generos_da_obra == 0


@pytest.mark.parametrize(
    "campos",
    [
        pytest.param({"tipo_mime": "image/gif"}, id="formato-nao-permitido"),
        pytest.param({"tamanho_bytes": 2 * 1024 * 1024 + 1}, id="acima-de-2mb"),
    ],
)
def test_poster_invalido_e_recusado(sessao: Session, campos: dict) -> None:
    obra = criar_filme(sessao)
    dados = {"conteudo": b"img", "tipo_mime": "image/png", "tamanho_bytes": 3} | campos
    sessao.add(Poster(obra_id=obra.id, **dados))

    with pytest.raises(IntegrityError):
        sessao.flush()

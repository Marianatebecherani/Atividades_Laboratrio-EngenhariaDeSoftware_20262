import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Avaliacao, ItemLista, PapelUsuario, StatusLista, Usuario


def criar_usuario(sessao: Session, email: str = "ana@exemplo.com") -> Usuario:
    usuario = Usuario(nome="Ana", email=email, senha_hash="hash")
    sessao.add(usuario)
    sessao.flush()
    return usuario


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


def test_filme_tmdb_aparece_uma_unica_vez_na_lista_do_usuario(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    sessao.add(ItemLista(usuario_id=usuario.id, tmdb_id=27205, status=StatusLista.ASSISTINDO))
    sessao.flush()
    sessao.add(ItemLista(usuario_id=usuario.id, tmdb_id=27205, status=StatusLista.ASSISTIDO))

    with pytest.raises(IntegrityError):
        sessao.flush()


def test_avaliacao_tmdb_aparece_uma_unica_vez_por_usuario(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    sessao.add(Avaliacao(usuario_id=usuario.id, tmdb_id=27205, nota=4))
    sessao.flush()
    sessao.add(Avaliacao(usuario_id=usuario.id, tmdb_id=27205, nota=5))

    with pytest.raises(IntegrityError):
        sessao.flush()


def test_nota_fora_de_1_a_5_e_recusada(sessao: Session) -> None:
    usuario = criar_usuario(sessao)
    sessao.add(Avaliacao(usuario_id=usuario.id, tmdb_id=27205, nota=6))

    with pytest.raises(IntegrityError):
        sessao.flush()


def test_lista_e_avaliacoes_tmdb_nao_referenciam_obras_locais(sessao: Session) -> None:
    assert "obra_id" not in ItemLista.__table__.columns
    assert "obra_id" not in Avaliacao.__table__.columns
    assert {"obras", "generos", "posters"}.isdisjoint(Base.metadata.tables)

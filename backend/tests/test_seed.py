from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Configuracoes, obter_configuracoes
from app.core.seguranca import verificar_senha
from app.db.seed import GENEROS_BASE, converter_classificacao, ler_filmes, semear
from app.models import Genero, Obra, PapelUsuario, Poster, TipoObra, Usuario
from app.models.obra import ANO_LANCAMENTO_MINIMO, CLASSIFICACOES_INDICATIVAS

CSV_EXEMPLO = """﻿indice;titulo;ano;duracao_min;classificacao;sinopse;generos
1;Filme Um;1994;142;16;"Sinopse com ponto e vírgula; dentro de aspas.";Drama|Crime
2;Filme Dois;1952;143;Not Rated;;Drama|Biografia
3;Filme Três;1995;81;Livre;Uma animação.;
"""


@pytest.fixture
def diretorio_seed(tmp_path: Path) -> Path:
    (tmp_path / "filmes.csv").write_text(CSV_EXEMPLO, encoding="utf-8")
    (tmp_path / "posters").mkdir()
    (tmp_path / "posters" / "filme_001.png").write_bytes(b"png-1")
    (tmp_path / "posters" / "filme_002.png").write_bytes(b"png-22")
    return tmp_path


def configuracoes(diretorio: Path, **campos) -> Configuracoes:
    dados = {"admin_email": "admin@teste.com", "admin_senha": "senha-segura"} | campos
    return Configuracoes(seed_diretorio=diretorio, **dados)


def contar(sessao: Session, modelo) -> int:
    return sessao.scalar(select(func.count()).select_from(modelo))


def buscar_obra(sessao: Session, titulo: str) -> Obra:
    return sessao.scalar(select(Obra).where(Obra.titulo == titulo))


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [("Livre", 0), ("livre", 0), ("Not Rated", None), ("14", 14), (" 18 ", 18)],
)
def test_converter_classificacao(valor: str, esperado: int | None) -> None:
    assert converter_classificacao(valor) == esperado


def test_ler_filmes_interpreta_o_csv(diretorio_seed: Path) -> None:
    um, dois, tres = ler_filmes(diretorio_seed)

    assert um.sinopse == "Sinopse com ponto e vírgula; dentro de aspas."
    assert um.generos == ("Drama", "Crime")
    assert dois.classificacao_indicativa is None
    assert dois.sinopse is None
    assert tres.classificacao_indicativa == 0
    assert tres.generos == ()


def test_seed_cria_filmes_com_posteres_e_generos(sessao: Session, diretorio_seed: Path) -> None:
    semear(sessao, configuracoes(diretorio_seed))

    assert contar(sessao, Obra) == 3
    filme_um = buscar_obra(sessao, "Filme Um")
    assert filme_um.tipo == TipoObra.FILME
    assert filme_um.duracao_minutos == 142
    assert {genero.nome for genero in filme_um.generos} == {"Drama", "Crime"}
    assert filme_um.poster.tipo_mime == "image/png"
    assert filme_um.poster.conteudo == b"png-1"
    assert filme_um.poster.tamanho_bytes == 5
    assert buscar_obra(sessao, "Filme Três").poster is None


def test_seed_cria_generos_base_e_os_novos_do_csv(sessao: Session, diretorio_seed: Path) -> None:
    semear(sessao, configuracoes(diretorio_seed))

    nomes = set(sessao.scalars(select(Genero.nome)))
    assert nomes == set(GENEROS_BASE) | {"Biografia"}


def test_seed_cria_admin_com_senha_protegida(sessao: Session, diretorio_seed: Path) -> None:
    semear(sessao, configuracoes(diretorio_seed))

    admin = sessao.scalar(select(Usuario).where(Usuario.email == "admin@teste.com"))
    assert admin.papel == PapelUsuario.ADMIN
    assert admin.senha_hash != "senha-segura"
    assert verificar_senha("senha-segura", admin.senha_hash)


def test_seed_sem_credenciais_nao_cria_admin(sessao: Session, diretorio_seed: Path) -> None:
    semear(sessao, configuracoes(diretorio_seed, admin_email=None, admin_senha=None))

    assert contar(sessao, Usuario) == 0
    assert contar(sessao, Obra) == 3


def test_seed_pode_ser_executado_novamente_sem_duplicar(
    sessao: Session, diretorio_seed: Path
) -> None:
    semear(sessao, configuracoes(diretorio_seed))
    semear(sessao, configuracoes(diretorio_seed))

    assert contar(sessao, Obra) == 3
    assert contar(sessao, Poster) == 2
    assert contar(sessao, Genero) == len(GENEROS_BASE) + 1
    assert contar(sessao, Usuario) == 1


def test_dados_reais_do_seed_respeitam_as_regras_do_banco() -> None:
    """Valida o filmes.csv do repositório sem gravar no banco."""
    diretorio = obter_configuracoes().seed_diretorio
    filmes = ler_filmes(diretorio)

    assert len(filmes) == 100
    assert len({filme.titulo for filme in filmes}) == len(filmes)
    for filme in filmes:
        assert filme.ano_lancamento >= ANO_LANCAMENTO_MINIMO, filme.titulo
        assert filme.duracao_minutos > 0, filme.titulo
        assert filme.classificacao_indicativa in (*CLASSIFICACOES_INDICATIVAS, None), filme.titulo
        poster = diretorio / "posters" / f"filme_{filme.indice:03d}.png"
        assert poster.exists(), poster.name
        assert poster.stat().st_size <= 2 * 1024 * 1024, poster.name

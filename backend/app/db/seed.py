"""Popula o banco com o administrador, os gêneros e os filmes de exemplo.

Os filmes são lidos de `filmes.csv` e os pôsteres da pasta `posters/`, ambos no diretório
definido em SEED_DIRETORIO (padrão: database/seed na raiz do repositório).

Pode ser executado várias vezes: registros já existentes são mantidos sem alteração.

Uso (a partir de backend/): uv run python -m app.db.seed
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Configuracoes, obter_configuracoes
from app.core.seguranca import gerar_hash_senha
from app.db.sessao import SessaoLocal
from app.models import Genero, Obra, PapelUsuario, Poster, TipoObra, Usuario

# Gêneros sempre disponíveis (os mesmos do filtro do frontend).
# Gêneros adicionais citados no CSV também são criados.
GENEROS_BASE = (
    "Ação",
    "Animação",
    "Aventura",
    "Comédia",
    "Crime",
    "Drama",
    "Fantasia",
    "Ficção Científica",
    "Mistério",
    "Romance",
    "Terror",
)

ARQUIVO_FILMES = "filmes.csv"
PASTA_POSTERS = "posters"
SEPARADOR_GENEROS = "|"
TIPOS_MIME_POR_EXTENSAO = {".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp"}
CLASSIFICACOES_TEXTUAIS = {"livre": 0, "not rated": None}


@dataclass(frozen=True)
class FilmeCsv:
    indice: int
    titulo: str
    ano_lancamento: int
    duracao_minutos: int
    classificacao_indicativa: int | None
    sinopse: str | None
    generos: tuple[str, ...]


def converter_classificacao(valor: str) -> int | None:
    """Converte "Livre" em 0, "Not Rated" em nulo e números no próprio valor."""
    texto = valor.strip()
    if texto.lower() in CLASSIFICACOES_TEXTUAIS:
        return CLASSIFICACOES_TEXTUAIS[texto.lower()]
    return int(texto)


def ler_filmes(diretorio: Path) -> list[FilmeCsv]:
    """Lê o filmes.csv (UTF-8, separado por ponto e vírgula). A coluna `generos` é opcional."""
    with (diretorio / ARQUIVO_FILMES).open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=";"))

    filmes = []
    for linha in linhas:
        generos = linha.get("generos") or ""
        filmes.append(
            FilmeCsv(
                indice=int(linha["indice"]),
                titulo=linha["titulo"].strip(),
                ano_lancamento=int(linha["ano"]),
                duracao_minutos=int(linha["duracao_min"]),
                classificacao_indicativa=converter_classificacao(linha["classificacao"]),
                sinopse=linha["sinopse"].strip() or None,
                generos=tuple(
                    nome.strip() for nome in generos.split(SEPARADOR_GENEROS) if nome.strip()
                ),
            )
        )
    return filmes


def ler_poster(diretorio: Path, indice: int) -> Poster | None:
    """Procura o pôster `filme_<indice com 3 dígitos>` em um dos formatos aceitos."""
    for extensao, tipo_mime in TIPOS_MIME_POR_EXTENSAO.items():
        caminho = diretorio / PASTA_POSTERS / f"filme_{indice:03d}{extensao}"
        if caminho.exists():
            conteudo = caminho.read_bytes()
            return Poster(conteudo=conteudo, tipo_mime=tipo_mime, tamanho_bytes=len(conteudo))
    return None


def semear_generos(sessao: Session, filmes: list[FilmeCsv]) -> dict[str, Genero]:
    existentes = {genero.nome: genero for genero in sessao.scalars(select(Genero))}
    nomes = list(GENEROS_BASE) + [nome for filme in filmes for nome in filme.generos]
    for nome in nomes:
        if nome not in existentes:
            existentes[nome] = Genero(nome=nome)
            sessao.add(existentes[nome])
    return existentes


def semear_filmes(
    sessao: Session, filmes: list[FilmeCsv], generos: dict[str, Genero], diretorio: Path
) -> tuple[int, list[str]]:
    """Cadastra os filmes ainda inexistentes. Retorna a quantidade criada e os sem pôster."""
    titulos_existentes = set(sessao.scalars(select(Obra.titulo)))
    novos, sem_poster = 0, []
    for filme in filmes:
        if filme.titulo in titulos_existentes:
            continue
        poster = ler_poster(diretorio, filme.indice)
        if poster is None:
            sem_poster.append(filme.titulo)
        sessao.add(
            Obra(
                titulo=filme.titulo,
                tipo=TipoObra.FILME,
                ano_lancamento=filme.ano_lancamento,
                duracao_minutos=filme.duracao_minutos,
                classificacao_indicativa=filme.classificacao_indicativa,
                sinopse=filme.sinopse,
                generos=[generos[nome] for nome in filme.generos],
                poster=poster,
            )
        )
        novos += 1
    return novos, sem_poster


def semear_admin(sessao: Session, configuracoes: Configuracoes) -> bool:
    if not configuracoes.admin_email or not configuracoes.admin_senha:
        return False
    if sessao.scalar(select(Usuario).where(Usuario.email == configuracoes.admin_email)):
        return False
    sessao.add(
        Usuario(
            nome=configuracoes.admin_nome,
            email=configuracoes.admin_email,
            senha_hash=gerar_hash_senha(configuracoes.admin_senha),
            papel=PapelUsuario.ADMIN,
        )
    )
    return True


def semear(sessao: Session, configuracoes: Configuracoes) -> None:
    diretorio = configuracoes.seed_diretorio
    filmes = ler_filmes(diretorio)
    generos = semear_generos(sessao, filmes)
    novos_filmes, sem_poster = semear_filmes(sessao, filmes, generos, diretorio)
    admin_criado = semear_admin(sessao, configuracoes)
    sessao.commit()

    print(f"Gêneros: {len(generos)} | Filmes novos: {novos_filmes} de {len(filmes)}")
    if sem_poster:
        print(f"Filmes sem pôster: {', '.join(sem_poster)}")
    if admin_criado:
        print(f"Administrador criado: {configuracoes.admin_email}")
    elif not configuracoes.admin_email or not configuracoes.admin_senha:
        print("Administrador não criado: defina ADMIN_EMAIL e ADMIN_SENHA no .env.")


if __name__ == "__main__":
    with SessaoLocal() as sessao:
        semear(sessao, obter_configuracoes())

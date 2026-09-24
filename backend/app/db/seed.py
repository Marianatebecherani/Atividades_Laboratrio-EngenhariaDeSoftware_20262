"""Popula o banco com o administrador, os gêneros e as obras de exemplo.

Pode ser executado várias vezes: registros já existentes são mantidos sem alteração.

Uso (a partir de backend/): uv run python -m app.db.seed
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Configuracoes, obter_configuracoes
from app.core.seguranca import gerar_hash_senha
from app.db.sessao import SessaoLocal
from app.models import Genero, Obra, PapelUsuario, TipoObra, Usuario

GENEROS = (
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


@dataclass(frozen=True)
class ObraExemplo:
    titulo: str
    tipo: TipoObra
    ano_lancamento: int
    classificacao_indicativa: int
    generos: tuple[str, ...]
    sinopse: str | None = None
    duracao_minutos: int | None = None
    temporadas: int | None = None


def filme(titulo, ano, classificacao, minutos, generos, sinopse=None) -> ObraExemplo:
    return ObraExemplo(titulo, TipoObra.FILME, ano, classificacao, generos, sinopse, minutos)


def serie(titulo, ano, classificacao, temporadas, generos, sinopse=None) -> ObraExemplo:
    return ObraExemplo(
        titulo, TipoObra.SERIE, ano, classificacao, generos, sinopse, temporadas=temporadas
    )


OBRAS = (
    filme(
        "Interestelar",
        2014,
        10,
        169,
        ("Drama", "Ficção Científica"),
        "Um grupo de astronautas atravessa um buraco de minhoca em busca de um novo planeta "
        "que possa abrigar a humanidade.",
    ),
    filme(
        "O Poderoso Chefão",
        1972,
        16,
        175,
        ("Drama", "Crime"),
        "O patriarca de uma família mafiosa transfere o controle do império ao filho relutante.",
    ),
    filme(
        "O Senhor dos Anéis",
        2001,
        12,
        178,
        ("Aventura", "Fantasia"),
        "Um hobbit parte em uma jornada para destruir um anel capaz de dominar a Terra-média.",
    ),
    filme(
        "Matrix",
        1999,
        14,
        136,
        ("Ação", "Ficção Científica"),
        "Um hacker descobre que a realidade é uma simulação e se une à resistência contra as "
        "máquinas.",
    ),
    filme(
        "Forrest Gump",
        1994,
        12,
        142,
        ("Drama", "Romance"),
        "Um homem de bom coração atravessa décadas da história americana sem perder a "
        "esperança de reencontrar seu grande amor.",
    ),
    filme(
        "Invocação do Mal",
        2013,
        16,
        112,
        ("Terror", "Mistério"),
        "Investigadores paranormais ajudam uma família aterrorizada por uma presença sombria.",
    ),
    filme("O Exorcista", 1973, 18, 122, ("Terror",)),
    filme("Batman", 1989, 14, 126, ("Ação", "Crime")),
    filme("Clube da Luta", 1999, 18, 139, ("Drama", "Crime")),
    filme("Toy Story", 1995, 0, 81, ("Animação", "Comédia")),
    filme("O Iluminado", 1980, 18, 146, ("Terror", "Drama")),
    filme("A Origem", 2010, 14, 148, ("Ação", "Ficção Científica")),
    filme("Os Bons Companheiros", 1990, 18, 146, ("Crime", "Drama")),
    filme("Pulp Fiction", 1994, 18, 154, ("Crime", "Drama")),
    filme("Gladiador", 2000, 16, 155, ("Ação", "Drama")),
    filme("De Volta para o Futuro", 1985, 10, 116, ("Aventura", "Ficção Científica", "Comédia")),
    filme("Superbad", 2007, 16, 113, ("Comédia",)),
    serie(
        "Breaking Bad",
        2008,
        16,
        5,
        ("Drama", "Crime"),
        "Um professor de química com câncer terminal passa a produzir drogas para garantir o "
        "futuro da família.",
    ),
    serie(
        "Stranger Things",
        2016,
        16,
        5,
        ("Ficção Científica", "Terror", "Drama"),
        "O desaparecimento de um garoto revela experimentos secretos e forças sobrenaturais em "
        "uma pequena cidade.",
    ),
    serie("Dark", 2017, 16, 3, ("Ficção Científica", "Mistério")),
    serie("The Office", 2005, 12, 9, ("Comédia",)),
    serie("Game of Thrones", 2011, 16, 8, ("Fantasia", "Drama", "Aventura")),
)


def semear_generos(sessao: Session) -> dict[str, Genero]:
    existentes = {genero.nome: genero for genero in sessao.scalars(select(Genero))}
    for nome in GENEROS:
        if nome not in existentes:
            existentes[nome] = Genero(nome=nome)
            sessao.add(existentes[nome])
    return existentes


def semear_obras(sessao: Session, generos: dict[str, Genero]) -> int:
    titulos_existentes = set(sessao.scalars(select(Obra.titulo)))
    novas = 0
    for exemplo in OBRAS:
        if exemplo.titulo in titulos_existentes:
            continue
        sessao.add(
            Obra(
                titulo=exemplo.titulo,
                tipo=exemplo.tipo,
                ano_lancamento=exemplo.ano_lancamento,
                classificacao_indicativa=exemplo.classificacao_indicativa,
                sinopse=exemplo.sinopse,
                duracao_minutos=exemplo.duracao_minutos,
                temporadas=exemplo.temporadas,
                generos=[generos[nome] for nome in exemplo.generos],
            )
        )
        novas += 1
    return novas


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
    generos = semear_generos(sessao)
    novas_obras = semear_obras(sessao, generos)
    admin_criado = semear_admin(sessao, configuracoes)
    sessao.commit()

    print(f"Gêneros: {len(generos)} | Obras novas: {novas_obras}")
    if admin_criado:
        print(f"Administrador criado: {configuracoes.admin_email}")
    elif not configuracoes.admin_email or not configuracoes.admin_senha:
        print("Administrador não criado: defina ADMIN_EMAIL e ADMIN_SENHA no .env.")


if __name__ == "__main__":
    with SessaoLocal() as sessao:
        semear(sessao, obter_configuracoes())

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.excecoes import ConflitoDeDados, RecursoNaoEncontrado
from app.models import Genero
from app.repositories.genero_repository import GeneroRepository
from app.schemas.genero import GeneroEntrada


class GeneroService:
    """Regras de negócio do cadastro de gêneros."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = GeneroRepository(sessao)

    def listar(self) -> Sequence[Genero]:
        return self.repositorio.listar()

    def obter(self, genero_id: int) -> Genero:
        genero = self.repositorio.obter_por_id(genero_id)
        if genero is None:
            raise RecursoNaoEncontrado("Gênero não encontrado")
        return genero

    def criar(self, dados: GeneroEntrada) -> Genero:
        self._garantir_nome_disponivel(dados.nome)
        genero = self.repositorio.adicionar(Genero(nome=dados.nome))
        self.sessao.commit()
        return genero

    def atualizar(self, genero_id: int, dados: GeneroEntrada) -> Genero:
        genero = self.obter(genero_id)
        self._garantir_nome_disponivel(dados.nome, ignorar_id=genero.id)
        genero.nome = dados.nome
        self.sessao.commit()
        return genero

    def excluir(self, genero_id: int) -> None:
        genero = self.obter(genero_id)
        total_obras = self.repositorio.contar_obras(genero.id)
        if total_obras:
            raise ConflitoDeDados(
                f"O gênero está associado a {total_obras} obra(s) e não pode ser excluído"
            )
        self.repositorio.remover(genero)
        self.sessao.commit()

    def _garantir_nome_disponivel(self, nome: str, ignorar_id: int | None = None) -> None:
        existente = self.repositorio.obter_por_nome(nome)
        if existente is not None and existente.id != ignorar_id:
            raise ConflitoDeDados("Já existe um gênero com esse nome")

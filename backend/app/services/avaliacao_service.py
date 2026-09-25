from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.excecoes import RecursoNaoEncontrado
from app.models import Avaliacao, Usuario
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.obra_repository import ObraRepository
from app.schemas.avaliacao import AvaliacaoEntrada
from app.schemas.paginacao import Paginacao


class AvaliacaoService:
    """Regras de negócio de notas e comentários: uma avaliação por usuário e obra."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = AvaliacaoRepository(sessao)
        self.obras = ObraRepository(sessao)

    def listar_da_obra(self, obra_id: int, paginacao: Paginacao) -> tuple[Sequence[Avaliacao], int]:
        self._garantir_obra(obra_id)
        return self.repositorio.listar_da_obra(obra_id, paginacao)

    def avaliar(
        self, usuario: Usuario, obra_id: int, dados: AvaliacaoEntrada
    ) -> tuple[Avaliacao, bool]:
        """Cria a avaliação do usuário ou atualiza a existente. Indica se foi criada."""
        self._garantir_obra(obra_id)
        avaliacao = self.repositorio.obter_do_usuario(usuario.id, obra_id)
        criada = avaliacao is None
        if criada:
            avaliacao = self.repositorio.adicionar(
                Avaliacao(usuario_id=usuario.id, obra_id=obra_id, nota=dados.nota)
            )
        avaliacao.nota = dados.nota
        avaliacao.comentario = dados.comentario
        self.sessao.commit()
        self.sessao.refresh(avaliacao)
        return avaliacao, criada

    def remover_do_usuario(self, usuario: Usuario, obra_id: int) -> None:
        avaliacao = self.repositorio.obter_do_usuario(usuario.id, obra_id)
        if avaliacao is None:
            raise RecursoNaoEncontrado("Você não avaliou esta obra")
        self.repositorio.remover(avaliacao)
        self.sessao.commit()

    def remover_por_id(self, avaliacao_id: int) -> None:
        """Remoção feita pela moderação (admin)."""
        avaliacao = self.repositorio.obter_por_id(avaliacao_id)
        if avaliacao is None:
            raise RecursoNaoEncontrado("Avaliação não encontrada")
        self.repositorio.remover(avaliacao)
        self.sessao.commit()

    def _garantir_obra(self, obra_id: int) -> None:
        if self.obras.obter_por_id(obra_id) is None:
            raise RecursoNaoEncontrado("Obra não encontrada")

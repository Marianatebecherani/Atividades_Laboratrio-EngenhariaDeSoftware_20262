from sqlalchemy.orm import Session

from app.core.excecoes import RecursoNaoEncontrado
from app.repositories.avaliacao_repository import AvaliacaoRepository


class AvaliacaoService:
    """Moderação administrativa de avaliações pessoais TMDb."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = AvaliacaoRepository(sessao)

    def remover_por_id(self, avaliacao_id: int) -> None:
        """Remoção feita pela moderação (admin)."""
        avaliacao = self.repositorio.obter_por_id(avaliacao_id)
        if avaliacao is None:
            raise RecursoNaoEncontrado("Avaliação não encontrada")
        self.repositorio.remover(avaliacao)
        self.sessao.commit()

from sqlalchemy.orm import Session

from app.core.excecoes import (
    ArquivoMuitoGrande,
    DadosInvalidos,
    RecursoNaoEncontrado,
    TipoDeArquivoNaoSuportado,
)
from app.models import Genero, Obra, Poster
from app.models.poster import TAMANHO_MAXIMO_BYTES
from app.repositories.genero_repository import GeneroRepository
from app.repositories.obra_repository import ObraComResumo, ObraRepository
from app.schemas.obra import FiltrosObras, ObraEntrada


def detectar_tipo_imagem(conteudo: bytes) -> str | None:
    """Identifica PNG, JPEG ou WebP pela assinatura do arquivo, sem confiar no nome enviado."""
    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if conteudo.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return "image/webp"
    return None


class ObraService:
    """Regras de negócio do catálogo de obras e de seus pôsteres."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.repositorio = ObraRepository(sessao)
        self.generos = GeneroRepository(sessao)

    def buscar(self, filtros: FiltrosObras) -> tuple[list[ObraComResumo], int]:
        return self.repositorio.buscar(filtros)

    def obter(self, obra_id: int) -> ObraComResumo:
        resultado = self.repositorio.obter_com_resumo(obra_id)
        if resultado is None:
            raise RecursoNaoEncontrado("Obra não encontrada")
        return resultado

    def criar(self, dados: ObraEntrada) -> ObraComResumo:
        obra = Obra(generos=self._obter_generos(dados.generos_ids))
        self._preencher(obra, dados)
        self.repositorio.adicionar(obra)
        self.sessao.commit()
        return self.obter(obra.id)

    def atualizar(self, obra_id: int, dados: ObraEntrada) -> ObraComResumo:
        obra = self._obter_obra(obra_id)
        obra.generos = self._obter_generos(dados.generos_ids)
        self._preencher(obra, dados)
        self.sessao.commit()
        return self.obter(obra.id)

    def excluir(self, obra_id: int) -> None:
        self.repositorio.remover(self._obter_obra(obra_id))
        self.sessao.commit()

    def definir_poster(self, obra_id: int, conteudo: bytes) -> ObraComResumo:
        obra = self._obter_obra(obra_id)
        if len(conteudo) > TAMANHO_MAXIMO_BYTES:
            raise ArquivoMuitoGrande("O pôster deve ter no máximo 2 MB")
        tipo_mime = detectar_tipo_imagem(conteudo)
        if tipo_mime is None:
            raise TipoDeArquivoNaoSuportado("Envie uma imagem PNG, JPEG ou WebP")

        if obra.poster is None:
            obra.poster = Poster(
                conteudo=conteudo, tipo_mime=tipo_mime, tamanho_bytes=len(conteudo)
            )
        else:
            obra.poster.conteudo = conteudo
            obra.poster.tipo_mime = tipo_mime
            obra.poster.tamanho_bytes = len(conteudo)
        self.sessao.commit()
        return self.obter(obra.id)

    def obter_poster(self, obra_id: int) -> Poster:
        poster = self.repositorio.obter_poster(obra_id)
        if poster is None:
            raise RecursoNaoEncontrado("Pôster não encontrado")
        return poster

    def remover_poster(self, obra_id: int) -> None:
        self.repositorio.remover(self.obter_poster(obra_id))
        self.sessao.commit()

    def _obter_obra(self, obra_id: int) -> Obra:
        obra = self.repositorio.obter_por_id(obra_id)
        if obra is None:
            raise RecursoNaoEncontrado("Obra não encontrada")
        return obra

    def _obter_generos(self, ids: list[int]) -> list[Genero]:
        generos = self.generos.obter_por_ids(ids)
        inexistentes = sorted(set(ids) - {genero.id for genero in generos})
        if inexistentes:
            raise DadosInvalidos(f"Gêneros inexistentes: {inexistentes}")
        return list(generos)

    @staticmethod
    def _preencher(obra: Obra, dados: ObraEntrada) -> None:
        obra.titulo = dados.titulo
        obra.tipo = dados.tipo
        obra.ano_lancamento = dados.ano_lancamento
        obra.sinopse = dados.sinopse
        obra.classificacao_indicativa = dados.classificacao_indicativa
        obra.duracao_minutos = dados.duracao_minutos
        obra.temporadas = dados.temporadas

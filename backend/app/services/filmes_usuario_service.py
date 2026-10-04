from datetime import datetime

from sqlalchemy.orm import Session

from app.core.excecoes import RecursoNaoEncontrado
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.comentario_repository import ComentarioRepository
from app.repositories.favorito_repository import FavoritoRepository
from app.repositories.item_lista_repository import ItemListaRepository
from app.schemas.item_lista import ItemListaEntrada
from app.schemas.paginacao import Paginacao
from app.schemas.tmdb import (
    AvaliacaoTmdbEntrada,
    EstadoFilmeTmdbResposta,
    FavoritoTmdbResposta,
    PaginaEstadoFilmesTmdbResposta,
    PaginaFavoritosTmdbResposta,
)


class FilmesUsuarioService:
    """Estado pessoal de filmes TMDb, sem armazenar metadados do catálogo externo."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao
        self.lista = ItemListaRepository(sessao)
        self.avaliacoes = AvaliacaoRepository(sessao)
        self.favoritos = FavoritoRepository(sessao)
        self.comentarios = ComentarioRepository(sessao)

    def obter_estado(self, usuario_id: int, tmdb_id: int) -> EstadoFilmeTmdbResposta:
        item = self.lista.obter_por_tmdb_id(usuario_id, tmdb_id)
        avaliacao = self.avaliacoes.obter_tmdb(usuario_id, tmdb_id)
        favorito = self.favoritos.obter(usuario_id, tmdb_id)
        # O comentário público (com nota) tornou-se a fonte principal da "minha nota";
        # a avaliação privada permanece como retrocompatibilidade.
        comentario = self.comentarios.obter_por_usuario_e_filme(usuario_id, tmdb_id)
        nota_pessoal = comentario.nota if comentario and comentario.nota is not None else None
        if nota_pessoal is None and avaliacao is not None:
            nota_pessoal = avaliacao.nota
        texto_comentario = comentario.conteudo if comentario else None
        if texto_comentario is None and avaliacao is not None:
            texto_comentario = avaliacao.comentario
        datas = [
            data
            for data in (
                item.atualizado_em if item else None,
                avaliacao.atualizado_em if avaliacao else None,
                comentario.atualizado_em if comentario else None,
                favorito.criado_em if favorito else None,
            )
            if data is not None
        ]
        return EstadoFilmeTmdbResposta(
            tmdb_id=tmdb_id,
            status=item.status if item else None,
            nota_pessoal=nota_pessoal,
            comentario=texto_comentario,
            favorito=favorito is not None,
            atualizado_em=max(datas) if datas else None,
        )

    def listar_filmes(
        self, usuario_id: int, paginacao: Paginacao
    ) -> PaginaEstadoFilmesTmdbResposta:
        estados: dict[int, EstadoFilmeTmdbResposta] = {}
        for item in self.lista.listar_tmdb(usuario_id):
            estados[item.tmdb_id] = EstadoFilmeTmdbResposta(
                tmdb_id=item.tmdb_id,
                status=item.status,
                atualizado_em=item.atualizado_em,
            )
        for avaliacao in self.avaliacoes.listar_tmdb(usuario_id):
            estado = estados.setdefault(
                avaliacao.tmdb_id,
                EstadoFilmeTmdbResposta(tmdb_id=avaliacao.tmdb_id),
            )
            estado.nota_pessoal = avaliacao.nota
            estado.comentario = avaliacao.comentario
            if estado.atualizado_em is None or avaliacao.atualizado_em > estado.atualizado_em:
                estado.atualizado_em = avaliacao.atualizado_em
        # Um comentário por filme (o mais recente), na ordem já retornada pelo repositório.
        tmdb_ids_com_comentario: set[int] = set()
        for comentario in self.comentarios.listar_por_usuario(usuario_id):
            if comentario.tmdb_id in tmdb_ids_com_comentario:
                continue
            tmdb_ids_com_comentario.add(comentario.tmdb_id)
            estado = estados.setdefault(
                comentario.tmdb_id,
                EstadoFilmeTmdbResposta(tmdb_id=comentario.tmdb_id),
            )
            if comentario.nota is not None:
                estado.nota_pessoal = comentario.nota
            estado.comentario = comentario.conteudo
            if estado.atualizado_em is None or comentario.atualizado_em > estado.atualizado_em:
                estado.atualizado_em = comentario.atualizado_em
        for favorito in self.favoritos.listar_todos(usuario_id):
            estado = estados.setdefault(
                favorito.tmdb_id,
                EstadoFilmeTmdbResposta(tmdb_id=favorito.tmdb_id),
            )
            estado.favorito = True
            if estado.atualizado_em is None or favorito.criado_em > estado.atualizado_em:
                estado.atualizado_em = favorito.criado_em

        itens = sorted(
            estados.values(),
            key=lambda estado: estado.atualizado_em.timestamp() if estado.atualizado_em else 0,
            reverse=True,
        )
        total = len(itens)
        itens = itens[paginacao.deslocamento : paginacao.deslocamento + paginacao.tamanho]
        return PaginaEstadoFilmesTmdbResposta(
            itens=itens,
            total=total,
            pagina=paginacao.pagina,
            tamanho=paginacao.tamanho,
        )

    def definir_status(
        self, usuario_id: int, tmdb_id: int, dados: ItemListaEntrada
    ) -> EstadoFilmeTmdbResposta:
        self.lista.salvar_tmdb(usuario_id, tmdb_id, dados.status)
        self.sessao.commit()
        return self.obter_estado(usuario_id, tmdb_id)

    def remover_da_lista(self, usuario_id: int, tmdb_id: int) -> None:
        if not self.lista.remover_tmdb(usuario_id, tmdb_id):
            raise RecursoNaoEncontrado("Filme não está na sua lista TMDb")
        self.sessao.commit()

    def avaliar(
        self, usuario_id: int, tmdb_id: int, dados: AvaliacaoTmdbEntrada
    ) -> EstadoFilmeTmdbResposta:
        self.avaliacoes.salvar_tmdb(usuario_id, tmdb_id, dados.nota, dados.comentario)
        self.sessao.commit()
        return self.obter_estado(usuario_id, tmdb_id)

    def remover_avaliacao(self, usuario_id: int, tmdb_id: int) -> None:
        if not self.avaliacoes.remover_tmdb(usuario_id, tmdb_id):
            raise RecursoNaoEncontrado("Você ainda não avaliou este filme TMDb")
        self.sessao.commit()

    def favoritar(self, usuario_id: int, tmdb_id: int) -> tuple[datetime, bool]:
        favorito = self.favoritos.obter(usuario_id, tmdb_id)
        if favorito is not None:
            return favorito.criado_em, False
        favorito = self.favoritos.adicionar(usuario_id, tmdb_id)
        self.sessao.commit()
        return favorito.criado_em, True

    def desfavoritar(self, usuario_id: int, tmdb_id: int) -> None:
        favorito = self.favoritos.obter(usuario_id, tmdb_id)
        if favorito is None:
            raise RecursoNaoEncontrado("Filme não está nos seus favoritos")
        self.favoritos.remover(favorito)
        self.sessao.commit()

    def listar_favoritos(
        self, usuario_id: int, paginacao: Paginacao
    ) -> PaginaFavoritosTmdbResposta:
        favoritos, total = self.favoritos.listar(
            usuario_id, paginacao.deslocamento, paginacao.tamanho
        )
        return PaginaFavoritosTmdbResposta(
            itens=[
                FavoritoTmdbResposta(tmdb_id=item.tmdb_id, criado_em=item.criado_em)
                for item in favoritos
            ],
            total=total,
            pagina=paginacao.pagina,
            tamanho=paginacao.tamanho,
        )

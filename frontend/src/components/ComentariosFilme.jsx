import { useEffect, useState } from "react";

import {
  atualizarComentario,
  criarComentarioFilme,
  listarComentariosFilme,
  removerComentario,
} from "../api";

const TAMANHO_PAGINA = 20;

function formatarDataHora(valor) {
  return new Date(valor).toLocaleString("pt-BR");
}

function ComentariosFilme({ tmdbId, token, usuarioAtual }) {
  const [itens, setItens] = useState([]);
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [novoConteudo, setNovoConteudo] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [edicaoId, setEdicaoId] = useState(null);
  const [edicaoConteudo, setEdicaoConteudo] = useState("");

  const carregar = (numeroPagina = pagina) => {
    setCarregando(true);
    setErro("");
    listarComentariosFilme(tmdbId, numeroPagina, TAMANHO_PAGINA)
      .then((resposta) => {
        setItens(resposta.itens);
        setTotal(resposta.total);
        setPagina(resposta.pagina);
      })
      .catch((error) => setErro(error.message))
      .finally(() => setCarregando(false));
  };

  useEffect(() => {
    carregar(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tmdbId]);

  const publicarComentario = async (event) => {
    event.preventDefault();
    if (!novoConteudo.trim()) return;
    setEnviando(true);
    setErro("");
    try {
      await criarComentarioFilme(tmdbId, novoConteudo, token);
      setNovoConteudo("");
      carregar(1);
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  };

  const iniciarEdicao = (comentario) => {
    setEdicaoId(comentario.id);
    setEdicaoConteudo(comentario.conteudo);
  };

  const cancelarEdicao = () => {
    setEdicaoId(null);
    setEdicaoConteudo("");
  };

  const salvarEdicao = async (event) => {
    event.preventDefault();
    if (!edicaoConteudo.trim()) return;
    setEnviando(true);
    setErro("");
    try {
      await atualizarComentario(edicaoId, edicaoConteudo, token);
      cancelarEdicao();
      carregar(pagina);
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  };

  const excluirComentario = async (comentarioId) => {
    setEnviando(true);
    setErro("");
    try {
      await removerComentario(comentarioId, token);
      carregar(itens.length === 1 && pagina > 1 ? pagina - 1 : pagina);
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  };

  const totalPaginas = Math.max(1, Math.ceil(total / TAMANHO_PAGINA));

  return (
    <section className="comentarios-secao" aria-label="Comentários">
      <h4>Comentários {total > 0 && `(${total})`}</h4>

      {erro && <p className="tmdb-error" role="alert">{erro}</p>}

      {token && (
        <form className="comentarios-form" onSubmit={publicarComentario}>
          <textarea
            value={novoConteudo}
            onChange={(event) => setNovoConteudo(event.target.value)}
            placeholder="Escreva seu comentário..."
            maxLength={2000}
            disabled={enviando}
          />
          <button type="submit" disabled={enviando || !novoConteudo.trim()}>
            Comentar
          </button>
        </form>
      )}

      {carregando && <p role="status">Carregando comentários...</p>}

      {!carregando && itens.length === 0 && <p>Ainda não há comentários nesta obra.</p>}

      <ul className="comentarios-lista">
        {itens.map((comentario) => {
          const souAutor = usuarioAtual?.id === comentario.usuario.id;
          const emEdicao = edicaoId === comentario.id;
          return (
            <li className="comentarios-item" key={comentario.id}>
              <div className="comentarios-cabecalho">
                <strong>{comentario.usuario.nome}</strong>
                <span>{formatarDataHora(comentario.criado_em)}</span>
              </div>

              {emEdicao ? (
                <form className="comentarios-form" onSubmit={salvarEdicao}>
                  <textarea
                    value={edicaoConteudo}
                    onChange={(event) => setEdicaoConteudo(event.target.value)}
                    maxLength={2000}
                    disabled={enviando}
                  />
                  <div className="comentarios-acoes">
                    <button type="submit" disabled={enviando || !edicaoConteudo.trim()}>
                      Salvar
                    </button>
                    <button type="button" onClick={cancelarEdicao} disabled={enviando}>
                      Cancelar
                    </button>
                  </div>
                </form>
              ) : (
                <p>{comentario.conteudo}</p>
              )}

              {souAutor && !emEdicao && (
                <div className="comentarios-acoes">
                  <button type="button" onClick={() => iniciarEdicao(comentario)}>
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => excluirComentario(comentario.id)}
                    disabled={enviando}
                  >
                    Excluir
                  </button>
                </div>
              )}
            </li>
          );
        })}
      </ul>

      {totalPaginas > 1 && (
        <nav className="comentarios-paginacao" aria-label="Paginação dos comentários">
          <button
            type="button"
            disabled={pagina <= 1 || carregando}
            onClick={() => carregar(pagina - 1)}
          >
            Anterior
          </button>
          <span>Página {pagina} de {totalPaginas}</span>
          <button
            type="button"
            disabled={pagina >= totalPaginas || carregando}
            onClick={() => carregar(pagina + 1)}
          >
            Próxima
          </button>
        </nav>
      )}
    </section>
  );
}

export default ComentariosFilme;

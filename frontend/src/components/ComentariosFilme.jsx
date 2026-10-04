import { useEffect, useState } from "react";

import { atualizarComentario, listarComentariosFilme, removerComentario } from "../api";

const TAMANHO_PAGINA = 20;

function formatarDataHora(valor) {
  return new Date(valor).toLocaleString("pt-BR");
}

function nota(valor) {
  return valor == null ? null : `⭐ ${valor} / 5`;
}

function ComentariosFilme({
  tmdbId,
  token,
  usuarioAtual,
  comentarioProprioId,
  aoAlterarComentarioProprio,
  atualizarSinal,
}) {
  const [itens, setItens] = useState([]);
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [edicaoId, setEdicaoId] = useState(null);
  const [edicaoConteudo, setEdicaoConteudo] = useState("");
  const [edicaoNota, setEdicaoNota] = useState("");

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
  }, [tmdbId, atualizarSinal]);

  const iniciarEdicao = (comentario) => {
    setEdicaoId(comentario.id);
    setEdicaoConteudo(comentario.conteudo);
    setEdicaoNota(comentario.nota == null ? "" : String(comentario.nota));
  };

  const cancelarEdicao = () => {
    setEdicaoId(null);
    setEdicaoConteudo("");
    setEdicaoNota("");
  };

  const salvarEdicao = async (event) => {
    event.preventDefault();
    if (!edicaoConteudo.trim()) return;
    setEnviando(true);
    setErro("");
    try {
      const atualizado = await atualizarComentario(
        edicaoId,
        edicaoConteudo,
        edicaoNota ? Number(edicaoNota) : null,
        token,
      );
      cancelarEdicao();
      carregar(pagina);
      if (edicaoId === comentarioProprioId) aoAlterarComentarioProprio?.(atualizado);
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
      if (comentarioId === comentarioProprioId) aoAlterarComentarioProprio?.(null);
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

      {carregando && <p role="status">Carregando comentários...</p>}

      {!carregando && itens.length === 0 && (
        <p>Ainda não há comentários nesta obra. Seja o primeiro a avaliar!</p>
      )}

      <ul className="comentarios-lista">
        {itens.map((comentario) => {
          const souAutor = usuarioAtual?.id === comentario.usuario.id;
          const emEdicao = edicaoId === comentario.id;
          return (
            <li className="comentarios-item" key={comentario.id}>
              <div className="comentarios-cabecalho">
                <strong>{comentario.usuario.nome}</strong>
                {nota(comentario.nota) && (
                  <span className="comentarios-nota">{nota(comentario.nota)}</span>
                )}
                <span>{formatarDataHora(comentario.criado_em)}</span>
              </div>

              {emEdicao ? (
                <form className="comentarios-form" onSubmit={salvarEdicao}>
                  <label>
                    Nota
                    <select
                      value={edicaoNota}
                      onChange={(event) => setEdicaoNota(event.target.value)}
                    >
                      <option value="">Sem nota</option>
                      {[1, 2, 3, 4, 5].map((valor) => (
                        <option key={valor} value={valor}>{valor} / 5</option>
                      ))}
                    </select>
                  </label>
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

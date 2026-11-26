import { useEffect, useState } from "react";

import {
  atualizarComentario,
  criarComentarioFilme,
  definirStatusFilmeTmdb,
  desfavoritarFilmeTmdb,
  favoritarFilmeTmdb,
  obterEstadoFilmeTmdb,
  obterFilmeTmdb,
  obterMeuComentarioFilme,
  removerStatusFilmeTmdb,
} from "../api";
import ComentariosFilme from "./ComentariosFilme";

function formatarData(valor) {
  if (!valor) return "Data de lançamento indisponível";
  return new Date(`${valor}T00:00:00`).toLocaleDateString("pt-BR");
}

function nota(valor) {
  return valor == null ? "Sem nota" : `⭐ ${valor.toFixed(1)}`;
}

function FilmeDetalhe({ tmdbId, token, usuario, modal = false }) {
  const [filme, setFilme] = useState(null);
  const [estadoUsuario, setEstadoUsuario] = useState(null);
  const [meuComentario, setMeuComentario] = useState(null);
  const [notaPessoal, setNotaPessoal] = useState("");
  const [comentarioPessoal, setComentarioPessoal] = useState("");
  const [atualizarComentarios, setAtualizarComentarios] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [erroAcao, setErroAcao] = useState("");

  useEffect(() => {
    let ativo = true;
    setCarregando(true);
    setErro("");
    setErroAcao("");
    Promise.all([
      obterFilmeTmdb(tmdbId),
      obterEstadoFilmeTmdb(tmdbId, token).catch(() => null),
      token ? obterMeuComentarioFilme(tmdbId, token).catch(() => null) : Promise.resolve(null),
    ])
      .then(([filmeResposta, estado, comentario]) => {
        if (!ativo) return;
        setFilme(filmeResposta);
        setEstadoUsuario(estado);
        setMeuComentario(comentario);
        setNotaPessoal(comentario?.nota == null ? "" : String(comentario.nota));
        setComentarioPessoal(comentario?.conteudo || "");
      })
      .catch((error) => {
        if (ativo) setErro(error.message);
      })
      .finally(() => {
        if (ativo) setCarregando(false);
      });
    return () => {
      ativo = false;
    };
  }, [tmdbId, token]);

  const atualizarEstadoUsuario = async () => {
    setEstadoUsuario(await obterEstadoFilmeTmdb(tmdbId, token));
  };

  const alterarStatus = async (status) => {
    setSalvando(true);
    setErroAcao("");
    try {
      if (status) {
        await definirStatusFilmeTmdb(tmdbId, status, token);
      } else {
        await removerStatusFilmeTmdb(tmdbId, token);
      }
      await atualizarEstadoUsuario();
    } catch (error) {
      setErroAcao(error.message);
    } finally {
      setSalvando(false);
    }
  };

  const salvarAvaliacao = async (event) => {
    event.preventDefault();
    if (!notaPessoal || !comentarioPessoal.trim()) return;
    setSalvando(true);
    setErroAcao("");
    try {
      const notaNumerica = Number(notaPessoal);
      const publicado = meuComentario
        ? await atualizarComentario(meuComentario.id, comentarioPessoal, notaNumerica, token)
        : await criarComentarioFilme(tmdbId, comentarioPessoal, notaNumerica, token);
      setMeuComentario(publicado);
      await atualizarEstadoUsuario();
      setAtualizarComentarios((valor) => valor + 1);
      
      window.dispatchEvent(new Event("recomendacoes:atualizar"));
    } catch (error) {
      setErroAcao(error.message);
    } finally {
      setSalvando(false);
    }
  };

  const alternarFavorito = async () => {
    setSalvando(true);
    setErroAcao("");
    try {
      if (estadoUsuario?.favorito) {
        await desfavoritarFilmeTmdb(tmdbId, token);
      } else {
        await favoritarFilmeTmdb(tmdbId, token);
      }
      await atualizarEstadoUsuario();
    } catch (error) {
      setErroAcao(error.message);
    } finally {
      setSalvando(false);
    }
  };

  const handleAlterarComentarioProprio = (comentario) => {
    setMeuComentario(comentario);
    setNotaPessoal(comentario?.nota == null ? "" : String(comentario.nota));
    setComentarioPessoal(comentario?.conteudo || "");
    atualizarEstadoUsuario();
  };

  if (carregando) {
    return <p role="status">Carregando detalhes...</p>;
  }

  if (erro || !filme) {
    return <p className="tmdb-error" role="alert">{erro || "Filme não encontrado."}</p>;
  }

  const comentarios = (
    <ComentariosFilme
      tmdbId={tmdbId}
      token={token}
      usuarioAtual={usuario}
      comentarioProprioId={meuComentario?.id}
      aoAlterarComentarioProprio={handleAlterarComentarioProprio}
      atualizarSinal={atualizarComentarios}
      modal={modal}
    />
  );

  return (
    <article className="tmdb-detail">
      {filme.backdrop_url && <img className="tmdb-detail-backdrop" src={filme.backdrop_url} alt="" />}
      <div className="tmdb-detail-body">
        {modal ? (
          <div className="tmdb-modal-poster">
            {filme.poster_url ? (
              <img
                className="tmdb-detail-poster"
                src={filme.poster_url}
                alt={`Pôster de ${filme.titulo}`}
              />
            ) : (
              <div className="tmdb-detail-poster tmdb-detail-poster-placeholder">Sem pôster</div>
            )}
          </div>
        ) : filme.poster_url && (
          <img
            className="tmdb-detail-poster"
            src={filme.poster_url}
            alt={`Pôster de ${filme.titulo}`}
          />
        )}
        <div className={modal ? "tmdb-modal-scroll" : undefined}>
        <div className={modal ? "tmdb-detail-content" : undefined}>
          <h3>{filme.titulo}</h3>
          {filme.titulo_original !== filme.titulo && (
            <p className="tmdb-original-title">{filme.titulo_original}</p>
          )}
          {modal ? (
            <div className="tmdb-detail-meta">
              <span>{formatarData(filme.data_lancamento)}</span>
              <span className="tmdb-modal-rating-badge">{nota(filme.nota_tmdb)}</span>
            </div>
          ) : (
            <p>{formatarData(filme.data_lancamento)} · {nota(filme.nota_tmdb)}</p>
          )}
          {modal && <h4 className="tmdb-detail-section-title">Sinopse</h4>}
          <p className={modal ? "tmdb-detail-synopsis" : undefined}>{filme.sinopse || "Sinopse não disponível."}</p>
          {filme.diretor && (modal ? (
            <section className="tmdb-modal-credits">
              <h4>Direção</h4>
              <p>{filme.diretor}</p>
            </section>
          ) : (
            <p><strong>Direção:</strong> {filme.diretor}</p>
          ))}
          {filme.elenco?.length > 0 && (modal ? (
            <section className="tmdb-modal-cast" aria-label="Elenco">
              <h4>Elenco</h4>
              <ul tabIndex={0} aria-label="Lista do elenco">
                {filme.elenco.map((pessoa) => (
                  <li key={pessoa.tmdb_id}>
                    {pessoa.perfil_url ? (
                      <img src={pessoa.perfil_url} alt="" loading="lazy" />
                    ) : (
                      <span className="tmdb-modal-cast-placeholder" aria-hidden="true">★</span>
                    )}
                    <span title={pessoa.nome}>{pessoa.nome}</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : (
            <p>
              <strong>Elenco:</strong> {filme.elenco.map((pessoa) => pessoa.nome).join(", ")}
            </p>
          ))}
          {filme.equipe_principal?.length > 0 && (modal ? (
            <section className="tmdb-modal-credits">
              <h4>Equipe</h4>
              <ul className="tmdb-modal-crew">
                {filme.equipe_principal.map((pessoa, index) => (
                  <li key={`${pessoa.tmdb_id}-${pessoa.funcao}-${index}`}>
                    <strong>{pessoa.nome}</strong> <span>({pessoa.funcao})</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : (
            <p>
              <strong>Equipe:</strong>{" "}
              {filme.equipe_principal
                .map((pessoa) => `${pessoa.nome} (${pessoa.funcao})`)
                .join(", ")}
            </p>
          ))}
          <div className="tmdb-user-actions">
            {modal ? (
              <div className="tmdb-modal-action-group">
                <span>Minha lista</span>
                <div className="tmdb-modal-status-buttons" role="group" aria-label="Status na minha lista">
                  {[
                    ["", "Não está na lista"],
                    ["quero_assistir", "Quero assistir"],
                    ["assistindo", "Assistindo"],
                    ["assistido", "Assistido"],
                  ].map(([valor, rotulo]) => (
                    <button
                      key={valor}
                      type="button"
                      aria-label={rotulo}
                      aria-pressed={(estadoUsuario?.status || "") === valor}
                      onClick={() => alterarStatus(valor)}
                      disabled={salvando}
                    >
                      {rotulo}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <label>
                Minha lista
                <select
                  value={estadoUsuario?.status || ""}
                  onChange={(event) => alterarStatus(event.target.value)}
                  disabled={salvando}
                >
                  <option value="">Não está na lista</option>
                  <option value="quero_assistir">Quero assistir</option>
                  <option value="assistindo">Assistindo</option>
                  <option value="assistido">Assistido</option>
                </select>
              </label>
            )}
            <button
              className={modal ? "tmdb-modal-favorite" : undefined}
              type="button"
              onClick={alternarFavorito}
              disabled={salvando}
              aria-pressed={modal ? Boolean(estadoUsuario?.favorito) : undefined}
            >
              {modal && <span aria-hidden="true">{estadoUsuario?.favorito ? "♥ " : "♡ "}</span>}
              {estadoUsuario?.favorito ? "Remover dos favoritos" : "Favoritar"}
            </button>
            {token && (
              <form className={modal ? "tmdb-modal-review-form" : undefined} onSubmit={salvarAvaliacao}>
                {modal ? (
                  <div className="tmdb-modal-action-group">
                    <span className="tmdb-modal-rating-title">Avaliação do filme</span>
                    <div className="tmdb-modal-rating-buttons" role="group" aria-label="Minha nota">
                      <div className="tmdb-modal-rating-options">
                        {["1", "2", "3", "4", "5"].map((valor) => (
                          <button
                            key={valor}
                            type="button"
                            aria-label={`${valor} / 5`}
                            aria-pressed={notaPessoal === valor}
                            onClick={() => setNotaPessoal(valor)}
                            disabled={salvando || Boolean(meuComentario)}
                          >
                            <span>{valor}</span>
                            <span className="tmdb-modal-rating-icon" aria-hidden="true">
                              ★
                            </span>
                          </button>
                        ))}
                      </div>
                      <div className="tmdb-modal-rating-footer">
                        <span>
                          {meuComentario
                            ? "Para alterar sua nota, edite seu comentário."
                            : "Selecione uma nota de 1 a 5"}
                        </span>
                        <button
                          className="tmdb-modal-rating-clear"
                          type="button"
                          aria-label="Sem nota"
                          aria-pressed={notaPessoal === ""}
                          onClick={() => setNotaPessoal("")}
                          disabled={salvando || Boolean(meuComentario)}
                        >
                          Sem nota
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <label>
                    Minha nota
                    <select
                      value={notaPessoal}
                      onChange={(event) => setNotaPessoal(event.target.value)}
                    >
                      <option value="">Sem nota</option>
                      {[1, 2, 3, 4, 5].map((valor) => (
                        <option key={valor} value={valor}>{valor} / 5</option>
                      ))}
                    </select>
                  </label>
                )}
                {(!modal || !meuComentario) && (
                  <>
                    <textarea
                      value={comentarioPessoal}
                      onChange={(event) => setComentarioPessoal(event.target.value)}
                      placeholder="Comentário público"
                      aria-label="Comentário público"
                      maxLength={2000}
                    />
                    <button
                      type="submit"
                      disabled={salvando || !notaPessoal || !comentarioPessoal.trim()}
                    >
                      {meuComentario ? "Atualizar meu comentário" : "Publicar meu comentário"}
                    </button>
                  </>
                )}
              </form>
            )}
          </div>
          {erroAcao && <p className="tmdb-error" role="alert">{erroAcao}</p>}
        </div>
        {modal && comentarios}
        </div>
      </div>
      {!modal && comentarios}
    </article>
  );
}

export default FilmeDetalhe;

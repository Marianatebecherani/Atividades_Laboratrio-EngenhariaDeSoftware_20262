import { useEffect, useId, useRef, useState } from "react";

import {
  avaliarFilmeTmdb,
  buscarFilmesTmdb,
  definirStatusFilmeTmdb,
  descobrirFilmesTmdb,
  desfavoritarFilmeTmdb,
  favoritarFilmeTmdb,
  listarFilmesTmdb,
  listarGenerosTmdb,
  obterEstadoFilmeTmdb,
  obterFilmeTmdb,
  removerStatusFilmeTmdb,
} from "../api";
import ComentariosFilme from "./ComentariosFilme";

const CATEGORIAS = [
  ["populares", "Populares"],
  ["top-rated", "Mais bem avaliados"],
  ["now-playing", "Em cartaz"],
  ["upcoming", "Em breve"],
];

const TITULOS_CATEGORIA = {
  populares: "Populares no TMDb",
  "top-rated": "Mais bem avaliados no TMDb",
  "now-playing": "Filmes em cartaz",
  upcoming: "Próximos lançamentos",
};

function formatarData(valor) {
  if (!valor) return "Data de lançamento indisponível";
  return new Date(`${valor}T00:00:00`).toLocaleDateString("pt-BR");
}

function nota(valor) {
  return valor == null ? "Sem nota" : `⭐ ${valor.toFixed(1)}`;
}

function TmdbSearch({ token, usuario, compacto = false, categoria = "populares" }) {
  const tituloId = useId();
  const resultadosRef = useRef(null);
  const paginaRef = useRef(1);
  const totalPaginasRef = useRef(0);
  const carregandoRef = useRef(false);
  const rolarDepoisDeCarregarRef = useRef(false);
  const [query, setQuery] = useState("");
  const [modo, setModo] = useState(compacto ? categoria : "buscar");
  const [termoPesquisado, setTermoPesquisado] = useState("");
  const [resultados, setResultados] = useState([]);
  const [generos, setGeneros] = useState([]);
  const [generoIds, setGeneroIds] = useState([]);
  const [operadorGeneros, setOperadorGeneros] = useState("AND");
  const [ano, setAno] = useState("");
  const [dataDe, setDataDe] = useState("");
  const [dataAte, setDataAte] = useState("");
  const [notaMinima, setNotaMinima] = useState("");
  const [notaMaxima, setNotaMaxima] = useState("");
  const [idioma, setIdioma] = useState("pt-BR");
  const [ordenacao, setOrdenacao] = useState("popularity.desc");
  const [detalhe, setDetalhe] = useState(null);
  const [estadoUsuario, setEstadoUsuario] = useState(null);
  const [notaPessoal, setNotaPessoal] = useState("");
  const [comentarioPessoal, setComentarioPessoal] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [detalheCarregando, setDetalheCarregando] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [erroAcao, setErroAcao] = useState("");

  useEffect(() => {
    if (compacto) return undefined;
    let ativo = true;
    listarGenerosTmdb()
      .then((resposta) => {
        if (ativo) setGeneros(resposta);
      })
      .catch((error) => {
        if (ativo) setErro(error.message);
      });
    return () => {
      ativo = false;
    };
  }, [compacto]);

  useEffect(() => {
    if (!compacto) return undefined;
    let ativo = true;
    listarFilmesTmdb(categoria)
      .then((resposta) => {
        if (ativo) {
          setResultados(resposta.resultados);
          paginaRef.current = resposta.pagina;
          totalPaginasRef.current = resposta.total_paginas;
        }
      })
      .catch((error) => {
        if (ativo) setErro(error.message);
      });
    return () => {
      ativo = false;
    };
  }, [compacto, categoria]);

  useEffect(() => {
    if (!rolarDepoisDeCarregarRef.current) return;
    rolarDepoisDeCarregarRef.current = false;
    requestAnimationFrame(() => {
      const faixa = resultadosRef.current;
      faixa?.scrollBy({ left: faixa.clientWidth, behavior: "smooth" });
    });
  }, [resultados]);

  const carregarResultados = async (novoModo, numeroPagina = 1, anexar = false) => {
    const termo = numeroPagina === 1 ? query.trim() : termoPesquisado;
    if (novoModo === "buscar" && !termo) return;
    if (anexar && carregandoRef.current) return;
    carregandoRef.current = true;
    setCarregando(true);
    setErro("");
    setDetalhe(null);
    try {
      let resposta;
      if (novoModo === "buscar") {
        setTermoPesquisado(termo);
        resposta = await buscarFilmesTmdb(termo, numeroPagina);
      } else if (novoModo === "discover") {
        resposta = await descobrirFilmesTmdb({
          page: numeroPagina,
          genre_ids: generoIds.join(","),
          genre_operator: operadorGeneros,
          year: ano,
          release_date_from: dataDe,
          release_date_to: dataAte,
          min_rating: notaMinima,
          max_rating: notaMaxima,
          language: idioma,
          sort_by: ordenacao,
        });
      } else {
        resposta = await listarFilmesTmdb(novoModo, numeroPagina);
      }
      paginaRef.current = resposta.pagina;
      totalPaginasRef.current = resposta.total_paginas;
      setResultados((atuais) => anexar ? [...atuais, ...resposta.resultados] : resposta.resultados);
    } catch (error) {
      if (!anexar) setResultados([]);
      setErro(error.message);
    } finally {
      carregandoRef.current = false;
      setCarregando(false);
    }
  };

  const moverResultados = (direcao) => {
    const faixa = resultadosRef.current;
    if (!faixa) return;

    const chegouAoFinal = faixa.scrollLeft + faixa.clientWidth >= faixa.scrollWidth - 8;
    if (
      direcao > 0
      && chegouAoFinal
      && paginaRef.current < totalPaginasRef.current
      && !carregandoRef.current
    ) {
      rolarDepoisDeCarregarRef.current = true;
      carregarResultados(modo, paginaRef.current + 1, true);
      return;
    }

    faixa.scrollBy({ left: direcao * faixa.clientWidth, behavior: "smooth" });
  };

  const selecionarModo = (novoModo) => {
    setModo(novoModo);
    setErro("");
    setDetalhe(null);
    setTermoPesquisado("");
    setResultados([]);
    paginaRef.current = 1;
    totalPaginasRef.current = 0;
    if (novoModo !== "buscar" && novoModo !== "discover") {
      carregarResultados(novoModo);
    }
  };

  const alternarGenero = (generoId) => {
    setGeneroIds((atuais) =>
      atuais.includes(generoId)
        ? atuais.filter((id) => id !== generoId)
        : [...atuais, generoId],
    );
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    carregarResultados(modo);
  };

  const abrirDetalhe = async (tmdbId) => {
    setDetalheCarregando(true);
    setErro("");
    setErroAcao("");
    try {
      const filme = await obterFilmeTmdb(tmdbId);
      const estado = await obterEstadoFilmeTmdb(tmdbId, token).catch(() => null);
      setDetalhe(filme);
      setEstadoUsuario(estado);
      setNotaPessoal(estado?.nota_pessoal == null ? "" : String(estado.nota_pessoal));
      setComentarioPessoal(estado?.comentario || "");
    } catch (error) {
      setErro(error.message);
    } finally {
      setDetalheCarregando(false);
    }
  };

  const atualizarEstadoUsuario = async () => {
    setEstadoUsuario(await obterEstadoFilmeTmdb(detalhe.tmdb_id, token));
  };

  const alterarStatus = async (event) => {
    const status = event.target.value;
    setSalvando(true);
    setErroAcao("");
    try {
      if (status) {
        await definirStatusFilmeTmdb(detalhe.tmdb_id, status, token);
      } else {
        await removerStatusFilmeTmdb(detalhe.tmdb_id, token);
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
    if (!notaPessoal) return;
    setSalvando(true);
    setErroAcao("");
    try {
      await avaliarFilmeTmdb(
        detalhe.tmdb_id,
        Number(notaPessoal),
        comentarioPessoal,
        token,
      );
      await atualizarEstadoUsuario();
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
        await desfavoritarFilmeTmdb(detalhe.tmdb_id, token);
      } else {
        await favoritarFilmeTmdb(detalhe.tmdb_id, token);
      }
      await atualizarEstadoUsuario();
    } catch (error) {
      setErroAcao(error.message);
    } finally {
      setSalvando(false);
    }
  };

  return (
    <section className="tmdb-search" aria-labelledby={tituloId}>
      <div className="tmdb-search-heading">
        <div>
          {!compacto && <span className="eyebrow">Catálogo externo</span>}
          <h2 id={tituloId}>
            {compacto ? TITULOS_CATEGORIA[categoria] : "Filmes do TMDb"}
          </h2>
        </div>
        {detalhe && (
          <button className="tmdb-back-button" onClick={() => setDetalhe(null)}>
            Voltar aos resultados
          </button>
        )}
      </div>

      {!compacto && (
        <div className="tmdb-controls">
          <label className="tmdb-mode-control">
            Catálogo
            <select value={modo} onChange={(event) => selecionarModo(event.target.value)}>
              <option value="buscar">Buscar por título</option>
              {CATEGORIAS.map(([valor, rotulo]) => (
                <option key={valor} value={valor}>{rotulo}</option>
              ))}
              <option value="discover">Filtrar filmes</option>
            </select>
          </label>

          {modo === "buscar" && (
            <form className="tmdb-search-form" onSubmit={handleSubmit}>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Nome do filme"
                aria-label="Pesquisar filmes no TMDb"
                required
              />
              <button type="submit" disabled={carregando}>
                {carregando ? "Buscando..." : "Buscar"}
              </button>
            </form>
          )}

          {modo === "discover" && (
            <form className="tmdb-discover-form" onSubmit={handleSubmit}>
              <div className="tmdb-primary-filters">
                <label>
                  Gênero
                  <select
                    value={generoIds.length === 1 ? generoIds[0] : ""}
                    onChange={(event) =>
                      setGeneroIds(event.target.value ? [Number(event.target.value)] : [])
                    }
                  >
                    <option value="">Todos</option>
                    {generos.map((genero) => (
                      <option key={genero.id} value={genero.id}>{genero.nome}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Ano
                  <input
                    type="number"
                    min="1870"
                    max="2100"
                    value={ano}
                    onChange={(event) => setAno(event.target.value)}
                    placeholder="Todos"
                  />
                </label>
                <label>
                  Nota mínima
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    value={notaMinima}
                    onChange={(event) => setNotaMinima(event.target.value)}
                    placeholder="0"
                  />
                </label>
                <label>
                  Nota máxima
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    value={notaMaxima}
                    onChange={(event) => setNotaMaxima(event.target.value)}
                    placeholder="10"
                  />
                </label>
                <label>
                  Ordenar
                  <select value={ordenacao} onChange={(event) => setOrdenacao(event.target.value)}>
                    <option value="popularity.desc">Popularidade</option>
                    <option value="vote_average.desc">Nota: maior</option>
                    <option value="vote_average.asc">Nota: menor</option>
                    <option value="primary_release_date.desc">Lançamento: recente</option>
                    <option value="primary_release_date.asc">Lançamento: antigo</option>
                    <option value="title.asc">Título A-Z</option>
                    <option value="title.desc">Título Z-A</option>
                  </select>
                </label>
                <button type="submit" disabled={carregando}>
                  {carregando ? "Filtrando..." : "Filtrar"}
                </button>
              </div>
              <details className="tmdb-advanced-filters">
                <summary>Mais filtros</summary>
                <div className="tmdb-advanced-fields">
                  <fieldset>
                    <legend>Gêneros adicionais</legend>
                    <div className="tmdb-genre-options">
                      {generos.map((genero) => (
                        <label key={genero.id}>
                          <input
                            type="checkbox"
                            checked={generoIds.includes(genero.id)}
                            onChange={() => alternarGenero(genero.id)}
                          />
                          {genero.nome}
                        </label>
                      ))}
                    </div>
                    <label>
                      Combinar gêneros
                      <select
                        value={operadorGeneros}
                        onChange={(event) => setOperadorGeneros(event.target.value)}
                      >
                        <option value="AND">Todos (AND)</option>
                        <option value="OR">Qualquer um (OR)</option>
                      </select>
                    </label>
                  </fieldset>
                  <label>
                    Lançamento de
                    <input type="date" value={dataDe} onChange={(event) => setDataDe(event.target.value)} />
                  </label>
                  <label>
                    Lançamento até
                    <input type="date" value={dataAte} onChange={(event) => setDataAte(event.target.value)} />
                  </label>
                  <label>
                    Idioma da resposta
                    <select value={idioma} onChange={(event) => setIdioma(event.target.value)}>
                      <option value="pt-BR">Português</option>
                      <option value="en-US">English</option>
                      <option value="es-ES">Español</option>
                      <option value="fr-FR">Français</option>
                    </select>
                  </label>
                </div>
              </details>
            </form>
          )}
        </div>
      )}

      {erro && <p className="tmdb-error" role="alert">{erro}</p>}
      {detalheCarregando && <p role="status">Carregando detalhes...</p>}

      {detalhe && (
        <article className="tmdb-detail">
          {detalhe.backdrop_url && (
            <img
              className="tmdb-detail-backdrop"
              src={detalhe.backdrop_url}
              alt=""
            />
          )}
          <div className="tmdb-detail-body">
            {detalhe.poster_url && (
              <img
                className="tmdb-detail-poster"
                src={detalhe.poster_url}
                alt={`Pôster de ${detalhe.titulo}`}
              />
            )}
            <div>
              <h3>{detalhe.titulo}</h3>
              {detalhe.titulo_original !== detalhe.titulo && (
                <p className="tmdb-original-title">{detalhe.titulo_original}</p>
              )}
              <p>{formatarData(detalhe.data_lancamento)} · {nota(detalhe.nota_tmdb)}</p>
              <p>{detalhe.sinopse || "Sinopse não disponível."}</p>
              {detalhe.diretor && <p><strong>Direção:</strong> {detalhe.diretor}</p>}
              {detalhe.elenco?.length > 0 && (
                <p>
                  <strong>Elenco:</strong> {detalhe.elenco.map((pessoa) => pessoa.nome).join(", ")}
                </p>
              )}
              {detalhe.equipe_principal?.length > 0 && (
                <p>
                  <strong>Equipe:</strong>{" "}
                  {detalhe.equipe_principal
                    .map((pessoa) => `${pessoa.nome} (${pessoa.funcao})`)
                    .join(", ")}
                </p>
              )}
              <div className="tmdb-user-actions">
                <label>
                  Minha lista
                  <select
                    value={estadoUsuario?.status || ""}
                    onChange={alterarStatus}
                    disabled={salvando}
                  >
                    <option value="">Não está na lista</option>
                    <option value="quero_assistir">Quero assistir</option>
                    <option value="assistindo">Assistindo</option>
                    <option value="assistido">Assistido</option>
                  </select>
                </label>
                <button type="button" onClick={alternarFavorito} disabled={salvando}>
                  {estadoUsuario?.favorito ? "Remover dos favoritos" : "Favoritar"}
                </button>
                <form onSubmit={salvarAvaliacao}>
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
                  <textarea
                    value={comentarioPessoal}
                    onChange={(event) => setComentarioPessoal(event.target.value)}
                    placeholder="Comentário pessoal"
                    maxLength={2000}
                  />
                  <button type="submit" disabled={salvando || !notaPessoal}>
                    Salvar minha avaliação
                  </button>
                </form>
                {estadoUsuario?.nota_pessoal != null && (
                  <p>
                    Minha nota: {estadoUsuario.nota_pessoal} / 5 · TMDb: {nota(detalhe.nota_tmdb)}
                  </p>
                )}
              </div>
              {erroAcao && <p className="tmdb-error" role="alert">{erroAcao}</p>}
            </div>
          </div>
          <ComentariosFilme tmdbId={detalhe.tmdb_id} token={token} usuarioAtual={usuario} />
        </article>
      )}

      {!detalhe && resultados.length > 0 && (
        <>
          <div className="tmdb-carousel">
            {resultados.length > 5 && (
              <button
                className="carousel-button carousel-button-previous"
                type="button"
                aria-label="Rolar filmes para a esquerda"
                title="Anterior"
                onClick={() => moverResultados(-1)}
              >
                ‹
              </button>
            )}
            <div className={`tmdb-results${compacto ? " tmdb-results-compact" : ""}`} aria-busy={carregando} ref={resultadosRef}>
              {resultados.map((filme) => (
                <button
                  className="tmdb-result"
                  key={filme.tmdb_id}
                  onClick={() => abrirDetalhe(filme.tmdb_id)}
                  type="button"
                  aria-label={`Ver ${filme.titulo}, ${nota(filme.nota_tmdb)}`}
                >
                  {filme.poster_url ? (
                    <img src={filme.poster_url} alt={`Pôster de ${filme.titulo}`} loading="lazy" />
                  ) : (
                    <span className="tmdb-no-poster">Sem pôster</span>
                  )}
                  <span className="tmdb-result-info">
                    <strong>{filme.titulo}</strong>
                    <span>{formatarData(filme.data_lancamento)}</span>
                  </span>
                  <span className="tmdb-result-rating">{nota(filme.nota_tmdb)}</span>
                </button>
              ))}
            </div>
            {resultados.length > 5 && (
              <button
                className="carousel-button carousel-button-next"
                type="button"
                aria-label="Rolar filmes para a direita"
                title="Próximo"
                onClick={() => moverResultados(1)}
              >
                ›
              </button>
            )}
          </div>
        </>
      )}

      {!compacto && modo === "buscar" && !detalhe && !carregando && termoPesquisado && !erro && resultados.length === 0 && (
        <p>Nenhum filme encontrado para “{termoPesquisado}”.</p>
      )}

      <p className="tmdb-attribution">
        This product uses the TMDB API but is not endorsed or certified by TMDB.
      </p>
    </section>
  );
}

export default TmdbSearch;
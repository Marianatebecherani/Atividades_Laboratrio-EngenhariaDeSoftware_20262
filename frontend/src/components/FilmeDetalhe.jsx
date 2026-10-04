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

function FilmeDetalhe({ tmdbId, token, usuario }) {
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

  const alterarStatus = async (event) => {
    const status = event.target.value;
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

  return (
    <article className="tmdb-detail">
      {filme.backdrop_url && <img className="tmdb-detail-backdrop" src={filme.backdrop_url} alt="" />}
      <div className="tmdb-detail-body">
        {filme.poster_url && (
          <img
            className="tmdb-detail-poster"
            src={filme.poster_url}
            alt={`Pôster de ${filme.titulo}`}
          />
        )}
        <div>
          <h3>{filme.titulo}</h3>
          {filme.titulo_original !== filme.titulo && (
            <p className="tmdb-original-title">{filme.titulo_original}</p>
          )}
          <p>{formatarData(filme.data_lancamento)} · {nota(filme.nota_tmdb)}</p>
          <p>{filme.sinopse || "Sinopse não disponível."}</p>
          {filme.diretor && <p><strong>Direção:</strong> {filme.diretor}</p>}
          {filme.elenco?.length > 0 && (
            <p>
              <strong>Elenco:</strong> {filme.elenco.map((pessoa) => pessoa.nome).join(", ")}
            </p>
          )}
          {filme.equipe_principal?.length > 0 && (
            <p>
              <strong>Equipe:</strong>{" "}
              {filme.equipe_principal
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
            {token && (
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
                  placeholder="Comentário público"
                  maxLength={2000}
                />
                <button
                  type="submit"
                  disabled={salvando || !notaPessoal || !comentarioPessoal.trim()}
                >
                  {meuComentario ? "Atualizar meu comentário" : "Publicar meu comentário"}
                </button>
              </form>
            )}
          </div>
          {erroAcao && <p className="tmdb-error" role="alert">{erroAcao}</p>}
        </div>
      </div>
      <ComentariosFilme
        tmdbId={tmdbId}
        token={token}
        usuarioAtual={usuario}
        comentarioProprioId={meuComentario?.id}
        aoAlterarComentarioProprio={handleAlterarComentarioProprio}
        atualizarSinal={atualizarComentarios}
      />
    </article>
  );
}

export default FilmeDetalhe;

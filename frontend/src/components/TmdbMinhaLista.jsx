import { useEffect, useState } from "react";

import { listarFilmesUsuarioTmdb, obterFilmeTmdb } from "../api";

const ROTULOS_STATUS = {
  quero_assistir: "Quero assistir",
  assistindo: "Assistindo",
  assistido: "Assistido",
};

function TmdbMinhaLista({ token }) {
  const [itens, setItens] = useState([]);
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const tamanho = 8;

  useEffect(() => {
    let ativo = true;
    listarFilmesUsuarioTmdb(token, pagina)
      .then(async (resposta) => {
        const filmes = await Promise.all(
          resposta.itens.map(async (estado) => {
            try {
              return { estado, filme: await obterFilmeTmdb(estado.tmdb_id) };
            } catch {
              return { estado, filme: null };
            }
          }),
        );
        if (ativo) {
          setItens(filmes);
          setTotal(resposta.total);
          setErro("");
        }
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
  }, [token, pagina]);

  if (carregando && itens.length === 0) {
    return <p className="data-loading">Carregando seus filmes TMDb...</p>;
  }

  return (
    <section className="tmdb-user-list">
      <h2>Seus filmes TMDb</h2>
      {erro && <p className="tmdb-error" role="alert">{erro}</p>}
      {!carregando && itens.length === 0 && !erro && (
        <p>Seus status, avaliações e favoritos de filmes TMDb aparecerão aqui.</p>
      )}
      <div className="tmdb-user-list-grid">
        {itens.map(({ estado, filme }) => (
          <article className="tmdb-user-list-item" key={estado.tmdb_id}>
            {filme?.poster_url ? (
              <img src={filme.poster_url} alt={`Pôster de ${filme.titulo}`} loading="lazy" />
            ) : (
              <span className="tmdb-no-poster">TMDb {estado.tmdb_id}</span>
            )}
            <div>
              <h3>{filme?.titulo || `Filme TMDb ${estado.tmdb_id}`}</h3>
              {estado.status && <p>{ROTULOS_STATUS[estado.status]}</p>}
              {estado.favorito && <p>Favorito</p>}
              {estado.nota_pessoal != null && <p>Sua nota: {estado.nota_pessoal} / 5</p>}
              {filme?.nota_tmdb != null && <p>TMDb: {filme.nota_tmdb.toFixed(1)} / 10</p>}
              {estado.comentario && <p>{estado.comentario}</p>}
            </div>
          </article>
        ))}
      </div>
      {total > tamanho && (
        <nav className="tmdb-pagination" aria-label="Paginação dos seus filmes TMDb">
          <button
            type="button"
            disabled={pagina <= 1 || carregando}
            onClick={() => {
              setCarregando(true);
              setPagina(pagina - 1);
            }}
          >
            Anterior
          </button>
          <span>Página {pagina} de {Math.ceil(total / tamanho)}</span>
          <button
            type="button"
            disabled={pagina >= Math.ceil(total / tamanho) || carregando}
            onClick={() => {
              setCarregando(true);
              setPagina(pagina + 1);
            }}
          >
            Próxima
          </button>
        </nav>
      )}
    </section>
  );
}

export default TmdbMinhaLista;
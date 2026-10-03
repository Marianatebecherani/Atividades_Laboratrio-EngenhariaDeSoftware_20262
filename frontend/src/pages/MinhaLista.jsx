import MovieCard from "../components/MovieCard";
import TmdbMinhaLista from "../components/TmdbMinhaLista";

function MinhaLista({
  movies,
  onMovieClick,
  token
}) {

  return (
    <section className="page-section">

      <div className="page-heading">

        <span className="eyebrow">
          Sua coleção
        </span>

        <h1>
          Minha Lista
        </h1>

        <p>
          Obras salvas na sua lista pessoal.
        </p>

      </div>

      {movies.length > 0 ? (

        <div className="movie-grid">

          {movies.map((movie) => (

            <MovieCard
              key={movie.id}
              movie={movie}
              onClick={onMovieClick}
            />

          ))}

        </div>

      ) : (

        <div className="empty-state">

          <span className="empty-icon">
            🎬
          </span>

          <h2>
            Sua lista local está vazia
          </h2>

          <p>
            Você ainda não adicionou obras do catálogo local à sua lista.
          </p>

        </div>

      )}

      <TmdbMinhaLista token={token} />

    </section>
  );
}

export default MinhaLista;
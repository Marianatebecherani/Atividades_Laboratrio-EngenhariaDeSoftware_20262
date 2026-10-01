import MovieCard from "../components/MovieCard";

function MinhaLista({
  movies,
  onMovieClick
}) {

  const filmesAvaliados =
    movies.filter(
      (movie) => movie.avaliado
    );

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
          Filmes que você já avaliou.
        </p>

      </div>

      {filmesAvaliados.length > 0 ? (

        <div className="movie-grid">

          {filmesAvaliados.map((movie) => (

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
            Sua lista está vazia
          </h2>

          <p>
            Você ainda não avaliou nenhum filme.
          </p>

        </div>

      )}

    </section>
  );
}

export default MinhaLista;
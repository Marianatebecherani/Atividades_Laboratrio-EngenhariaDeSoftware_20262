import MovieCard from "./MovieCard";

function MovieRow({
  title,
  movies,
  onMovieClick
}) {
  if (!movies.length) return null;

  return (
    <section className="movie-section">

      <div className="movie-section-header">

        <h2>
          {title}
        </h2>

        <button className="see-all">
          Ver todos →
        </button>

      </div>

      <div className="movie-row">

        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onClick={onMovieClick}
          />
        ))}

      </div>

    </section>
  );
}

export default MovieRow;
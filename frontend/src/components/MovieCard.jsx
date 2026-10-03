function MovieCard({ movie, onClick }) {
  return (
    <div
      className="movie-card-dashboard"
      onClick={() => onClick(movie)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onClick(movie);
      }}
    >
      <div className="movie-poster">
        {movie.posterUrl ? (
          <img src={movie.posterUrl} alt={`Pôster de ${movie.title}`} loading="lazy" />
        ) : (
          <span className="movie-emoji">{movie.emoji}</span>
        )}

        <div className="poster-gradient"></div>

        <div className="poster-rating">
          {movie.rating == null ? "Sem nota" : `⭐ ${movie.rating.toFixed(1)}`}
        </div>

      </div>

      <div className="movie-card-info">

        <h3>
          {movie.title}
        </h3>

        <span>
          {movie.listStatus || movie.genre}
        </span>

      </div>
    </div>
  );
}

export default MovieCard;
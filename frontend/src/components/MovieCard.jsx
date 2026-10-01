function MovieCard({ movie, onClick }) {
  return (
    <div
      className="movie-card-dashboard"
      onClick={() => onClick(movie)}
    >
      <div className="movie-poster">

        <span className="movie-emoji">
          {movie.emoji}
        </span>

        <div className="poster-gradient"></div>

        <div className="poster-rating">
          ⭐ {movie.rating}
        </div>

      </div>

      <div className="movie-card-info">

        <h3>
          {movie.title}
        </h3>

        <span>
          {movie.genre}
        </span>

      </div>
    </div>
  );
}

export default MovieCard;
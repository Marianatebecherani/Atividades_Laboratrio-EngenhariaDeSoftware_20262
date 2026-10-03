import MovieCard from "../components/MovieCard";
import TmdbSearch from "../components/TmdbSearch";

function Busca({
  movies,
  genres,
  token,
  searchTerm,
  setSearchTerm,
  selectedGenres,
  selectedRatings,
  selectedClassifications,
  toggleGenre,
  toggleRating,
  toggleClassification,
  onMovieClick
}) {

  const filteredMovies = movies
    .filter((movie) => {

      const matchesSearch =
        movie.title
          .toLowerCase()
          .includes(
            searchTerm.toLowerCase()
          );

      const matchesGenre =
        selectedGenres.length === 0 ||
        selectedGenres.some((genre) =>
          movie.genres.includes(genre)
        );

      const matchesRating =
        selectedRatings.length === 0 ||
        selectedRatings.some((range) => {
          if (movie.rating == null) return false;

          if (range === "0-1") {
            return (
              movie.rating >= 0 &&
              movie.rating < 1
            );
          }

          if (range === "1-2") {
            return (
              movie.rating >= 1 &&
              movie.rating < 2
            );
          }

          if (range === "2-3") {
            return (
              movie.rating >= 2 &&
              movie.rating < 3
            );
          }

          if (range === "3-4") {
            return (
              movie.rating >= 3 &&
              movie.rating < 4
            );
          }

          if (range === "4-4.5") {
            return (
              movie.rating >= 4 &&
              movie.rating < 4.5
            );
          }

          if (range === "4.5-5") {
            return (
              movie.rating >= 4.5 &&
              movie.rating <= 5
            );
          }

          return false;
        });

      const matchesClassification =
        selectedClassifications.length === 0 ||
        selectedClassifications.includes(
          movie.classification
        );

      return (
        matchesSearch &&
        matchesGenre &&
        matchesRating &&
        matchesClassification
      );
    })
    .sort(
      (a, b) => (b.rating ?? 0) - (a.rating ?? 0)
    );

  return (
    <section className="page-section search-page">

      <TmdbSearch token={token} />

      <div className="page-heading">

        <span className="eyebrow">
          Explore o catálogo
        </span>

        <h1>
          Buscar filmes
        </h1>

        <p>
          Encontre seu próximo filme favorito.
        </p>

      </div>

      <div className="search-box">

        <span>🔎</span>

        <input
          type="text"
          placeholder="Pesquisar pelo nome do filme..."
          value={searchTerm}
          onChange={(event) =>
            setSearchTerm(event.target.value)
          }
        />

      </div>

      <div className="filters">

        <div className="filter-group">

          <h3>
            Gêneros
          </h3>

          <div className="filter-options">

            {genres.map((genre) => (

              <button
                key={genre}
                className={
                  selectedGenres.includes(genre)
                    ? "filter-button active"
                    : "filter-button"
                }
                onClick={() =>
                  toggleGenre(genre)
                }
              >
                {genre}
              </button>

            ))}

          </div>

        </div>

        <div className="filter-group">
                <h3>
                  Nota
                </h3>
                <div className="filter-options">
                  {[
                    ["0-1", "0 - 1 ⭐"],
                    ["1-2", "1 - 2 ⭐"],
                    ["2-3", "2 - 3 ⭐"],
                    ["3-4", "3 - 4 ⭐"],
                    ["4-4.5", "4 - 4.5 ⭐"],
                    ["4.5-5", "4.5 - 5 ⭐"],
                  ].map(([value, label]) => (
                    <button
                      key={value}
                      className={
                        selectedRatings.includes(value)
                          ? "filter-button active"
                          : "filter-button"
                      }
                      onClick={() =>
                        toggleRating(value)
                      }
                    >
                      {label}
                    </button>
                  ))}
                </div>
            </div>

            <div className="filter-group">
              <h3>Classificação indicativa</h3>
              <div className="filter-options">
                {[
                  [0, "Livre"],
                  [10, "10 anos"],
                  [12, "12 anos"],
                  [14, "14 anos"],
                  [16, "16 anos"],
                  [18, "18 anos"],
                ].map(([value, label]) => (
                  <button
                    key={value}
                    className={
                      selectedClassifications.includes(value)
                        ? "filter-button active"
                        : "filter-button"
                    }
                    onClick={() => toggleClassification(value)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
        </div>


      {filteredMovies.length > 0 ? (

        <div className="movie-grid">

          {filteredMovies.map((movie) => (

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
            🔎
          </span>

          <h2>
            Nenhum filme encontrado
          </h2>

          <p>
            Tente alterar sua busca ou seus filtros.
          </p>

        </div>

      )}

    </section>
  );
}

export default Busca;
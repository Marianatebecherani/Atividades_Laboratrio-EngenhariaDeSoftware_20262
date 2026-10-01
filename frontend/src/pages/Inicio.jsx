import MovieRow from "../components/MovieRow";

function Inicio({
  movies,
  onMovieClick
}) {
  return (
    <div className="home-content">

      <section className="welcome-section">

        <div>

          <span>
            BEM-VINDO AO FILM STAR
          </span>

          <h1>
            O que você quer
            <br />
            assistir hoje?
          </h1>

          <p>
            Descubra novos filmes e encontre
            histórias que combinam com você.
          </p>

        </div>

      </section>

      <MovieRow
        title="Recomendações pessoais"
        movies={movies.filter(
          (movie) =>
            movie.type === "pessoal"
        )}
        onMovieClick={onMovieClick}
      />

      <MovieRow
        title="Comédia"
        movies={movies.filter(
          (movie) =>
            movie.type === "comedia"
        )}
        onMovieClick={onMovieClick}
      />

      <MovieRow
        title="Drama"
        movies={movies.filter(
          (movie) =>
            movie.type === "drama"
        )}
        onMovieClick={onMovieClick}
      />

      <MovieRow
        title="Terror"
        movies={movies.filter(
          (movie) =>
            movie.type === "terror"
        )}
        onMovieClick={onMovieClick}
      />

    </div>
  );
}

export default Inicio;
import MovieRow from "../components/MovieRow";
import TmdbSearch from "../components/TmdbSearch";

function Inicio({
  movies,
  recommendations,
  token,
  onMovieClick
}) {
  const filmes = movies.filter((movie) => movie.type === "filme");
  const series = movies.filter((movie) => movie.type === "serie");

  return (
    <div className="home-content">

      <TmdbSearch token={token} compacto />

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
        title="Recomendados para você"
        movies={recommendations}
        onMovieClick={onMovieClick}
      />

      <MovieRow
        title="Mais bem avaliados"
        movies={movies}
        onMovieClick={onMovieClick}
      />

      <MovieRow
        title="Filmes"
        movies={filmes}
        onMovieClick={onMovieClick}
      />

      <MovieRow
        title="Séries"
        movies={series}
        onMovieClick={onMovieClick}
      />

    </div>
  );
}

export default Inicio;
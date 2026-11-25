import { useEffect, useState } from "react";
import { listarFilmesTmdb } from "../api";

function HorizontalMovieSection({ titulo, categoria, maxFilmes = 6 }) {
  const [filmes, setFilmes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    const carregar = async () => {
      try {
        setCarregando(true);
        const dados = await listarFilmesTmdb(categoria, 1);
        setFilmes(dados.resultados?.slice(0, maxFilmes) || []);
        setErro(null);
      } catch {
        setErro("Erro ao carregar filmes");
      } finally {
        setCarregando(false);
      }
    };

    carregar();
  }, [categoria, maxFilmes]);

  if (carregando) {
    return (
      <section className="landing-horizontal-section">
        <div className="landing-horizontal-container">
          <div className="landing-section-loading">Carregando {titulo}...</div>
        </div>
      </section>
    );
  }

  if (erro || filmes.length === 0) {
    return null;
  }

  return (
    <section className="landing-horizontal-section">
      <div className="landing-horizontal-container">
        <h2 className="landing-section-title">{titulo}</h2>

        <div className="landing-movies-grid">
          {filmes.map((filme) => (
            <a
              key={filme.id}
              href={`/filme/${filme.id}`}
              className="landing-movie-card"
            >
              <div className="landing-movie-poster-wrapper">
                <img
                  src={
                    filme.poster_url
                      ? filme.poster_url
                      : "/placeholder.png"
                  }
                  alt={filme.titulo}
                  className="landing-movie-poster"
                  loading="lazy"
                />
                <div className="landing-movie-overlay">
                  <span className="landing-play-button">▶</span>
                </div>
              </div>

              <div className="landing-movie-info">
                <h3>{filme.titulo}</h3>
                {filme.nota_tmdb !== undefined && (
                  <div className="landing-movie-rating">
                    <span className="landing-stars">★</span>
                    <span>{(filme.nota_tmdb / 2).toFixed(1)}</span>
                  </div>
                )}
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HorizontalMovieSection;

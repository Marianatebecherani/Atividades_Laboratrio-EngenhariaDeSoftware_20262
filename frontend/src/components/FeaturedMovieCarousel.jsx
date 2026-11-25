import { useEffect, useState } from "react";
import { listarFilmesTmdb } from "../api";

function FeaturedMovieCarousel() {
  const [filmes, setFilmes] = useState([]);
  const [ativo, setAtivo] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    const carregar = async () => {
      try {
        setCarregando(true);
        const dados = await listarFilmesTmdb("popular", 1);
        setFilmes(dados.resultados?.slice(0, 10) || []);
        setErro(null);
      } catch {
        setErro("Erro ao carregar filmes");
      } finally {
        setCarregando(false);
      }
    };

    carregar();
  }, []);

  const proximoFilme = () => {
    setAtivo((prev) => (prev + 1) % filmes.length);
  };

  const filmeAnterior = () => {
    setAtivo((prev) => (prev - 1 + filmes.length) % filmes.length);
  };

  if (carregando) {
    return (
      <section className="landing-carousel-section">
        <div className="landing-carousel-container">
          <div className="landing-carousel-loading">Carregando filmes...</div>
        </div>
      </section>
    );
  }

  if (erro || filmes.length === 0) {
    return null;
  }

  const filmeAtual = filmes[ativo];
  const proximos = [
    filmes[(ativo + 1) % filmes.length],
    filmes[(ativo + 2) % filmes.length],
  ];

  return (
    <section className="landing-carousel-section">
      <div className="landing-carousel-container">
        <h2 className="landing-carousel-title">Filmes em Destaque</h2>

        <div className="landing-carousel-wrapper">
          <button
            className="landing-carousel-arrow landing-carousel-arrow-prev"
            onClick={filmeAnterior}
            aria-label="Filme anterior"
          >
            ←
          </button>

          <div className="landing-carousel-track">
            <div className="landing-carousel-items">
              {proximos.map((filme, indice) => (
                <div key={`prev-${indice}`} className="landing-carousel-item landing-carousel-item-side">
                  <div className="landing-poster-wrapper">
                    <img
                      src={
                        filme.poster_url
                          ? filme.poster_url
                          : "/placeholder.png"
                      }
                      alt={filme.titulo}
                      className="landing-poster"
                      loading="lazy"
                    />
                  </div>
                </div>
              ))}

              <div className="landing-carousel-item landing-carousel-item-center">
                <div className="landing-poster-wrapper landing-poster-wrapper-featured">
                  <img
                    src={
                      filmeAtual.poster_url
                        ? filmeAtual.poster_url
                        : "/placeholder.png"
                    }
                    alt={filmeAtual.titulo}
                    className="landing-poster landing-poster-featured"
                  />
                </div>

                <div className="landing-carousel-info">
                  <h3>{filmeAtual.titulo}</h3>
                  <p className="landing-year">{filmeAtual.ano || filmeAtual.data_lancamento?.substring(0, 4) || "N/A"}</p>
                  {filmeAtual.nota_tmdb !== undefined && (
                    <div className="landing-rating">
                      <span className="landing-stars">★</span>
                      <span>{(filmeAtual.nota_tmdb / 2).toFixed(1)} / 5</span>
                    </div>
                  )}
                  {filmeAtual.sinopse && (
                    <p className="landing-synopsis">{filmeAtual.sinopse.substring(0, 150)}...</p>
                  )}
                  <a href={`/filme/${filmeAtual.id}`} className="landing-btn-details">
                    Ver Detalhes
                  </a>
                </div>
              </div>

              <div className="landing-carousel-item landing-carousel-item-side">
                <div className="landing-poster-wrapper">
                  <img
                    src={
                      filmes[(ativo + 3) % filmes.length].poster_url
                        ? filmes[(ativo + 3) % filmes.length].poster_url
                        : "/placeholder.png"
                    }
                    alt={filmes[(ativo + 3) % filmes.length].titulo}
                    className="landing-poster"
                    loading="lazy"
                  />
                </div>
              </div>
            </div>
          </div>

          <button
            className="landing-carousel-arrow landing-carousel-arrow-next"
            onClick={proximoFilme}
            aria-label="Próximo filme"
          >
            →
          </button>
        </div>

        <div className="landing-carousel-indicators">
          {filmes.map((_, indice) => (
            <button
              key={indice}
              className={`landing-indicator ${indice === ativo ? "landing-indicator-active" : ""}`}
              onClick={() => setAtivo(indice)}
              aria-label={`Ir para filme ${indice + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturedMovieCarousel;

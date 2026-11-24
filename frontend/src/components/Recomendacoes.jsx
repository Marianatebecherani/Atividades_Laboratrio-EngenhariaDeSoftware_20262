import { useState } from "react";

import { useRecomendacoes } from "../hooks/useRecomendacoes";
import FilmeDetalhe from "./FilmeDetalhe";

const ESTRATEGIAS = [
  {
    valor: "perfil",
    rotulo: "Seu perfil",
    descricao: "Filmes dos gêneros e países que você avaliou melhor.",
  },
  {
    valor: "similares",
    rotulo: "Parecidos com seus favoritos",
    descricao: "Filmes parecidos com os que você avaliou com 4 ou 5 estrelas.",
  },
  {
    valor: "populares",
    rotulo: "Em alta",
    descricao: "Filmes populares no TMDb que você ainda não avaliou nem assistiu.",
  },
];

function formatarData(valor) {
  if (!valor) return "Data de lançamento indisponível";

  return new Date(`${valor}T00:00:00`).toLocaleDateString("pt-BR");
}

function nota(valor) {
  return valor == null ? "Sem nota" : `⭐ ${valor.toFixed(1)}`;
}

function Recomendacoes({ token, usuario }) {
  const [estrategia, setEstrategia] = useState("perfil");
  const [detalhe, setDetalhe] = useState(null);
  const { filmes, estrategiaUsada, carregando, erro, tentarNovamente } = useRecomendacoes(
    token,
    estrategia,
  );

  const escolhida = ESTRATEGIAS.find((item) => item.valor === estrategia);
  const usouReserva =
    !carregando && !erro && estrategiaUsada !== null && estrategiaUsada !== estrategia;

  return (
    <section className="tmdb-search" aria-labelledby="titulo-recomendacoes">
      <div className="tmdb-search-heading">
        <div>
          <span className="eyebrow">Sua experiência personalizada</span>
          <h2 id="titulo-recomendacoes">Recomendados para você</h2>
          <p>{escolhida.descricao}</p>
        </div>

        {detalhe && (
          <button
            className="tmdb-back-button"
            type="button"
            onClick={() => setDetalhe(null)}
          >
            Voltar às recomendações
          </button>
        )}
      </div>

      {!detalhe && (
        <div className="tmdb-controls tmdb-recomendacao-controles">
          <label className="tmdb-mode-control">
            Recomendar por
            <select value={estrategia} onChange={(event) => setEstrategia(event.target.value)}>
              {ESTRATEGIAS.map((item) => (
                <option key={item.valor} value={item.valor}>
                  {item.rotulo}
                </option>
              ))}
            </select>
          </label>
        </div>
      )}

      {carregando && (
        <p aria-live="polite">Buscando recomendações para você...</p>
      )}

      {erro && (
        <div className="tmdb-error" role="alert">
          <p>Não foi possível carregar suas recomendações: {erro}</p>
          <button type="button" onClick={tentarNovamente}>
            Tentar novamente
          </button>
        </div>
      )}

      {usouReserva && !detalhe && (
        <p className="tmdb-recomendacao-aviso" aria-live="polite">
          Ainda não há avaliações suficientes para essa opção, então mostramos os filmes em
          alta. Avalie alguns filmes para personalizar suas sugestões.
        </p>
      )}

      {!carregando && !erro && filmes.length === 0 && (
        <p>
          Ainda não temos recomendações para você. Avalie alguns filmes
          para receber sugestões personalizadas!
        </p>
      )}

      {detalhe && (
        <FilmeDetalhe
          tmdbId={detalhe}
          token={token}
          usuario={usuario}
        />
      )}

      {!detalhe && filmes.length > 0 && (
        <div className="tmdb-carousel">
          <div className="tmdb-results tmdb-results-compact">
            {filmes.map((filme) => (
              <button
                className="tmdb-result"
                key={filme.tmdb_id}
                type="button"
                onClick={() => setDetalhe(filme.tmdb_id)}
                aria-label={`Ver ${filme.titulo}, ${nota(filme.nota_tmdb)}. ${filme.motivo}`}
                title={filme.motivo}
              >
                {filme.poster_url ? (
                  <img
                    src={filme.poster_url}
                    alt={`Pôster de ${filme.titulo}`}
                    loading="lazy"
                  />
                ) : (
                  <span className="tmdb-no-poster">Sem pôster</span>
                )}

                <span className="tmdb-result-info">
                  <strong>{filme.titulo}</strong>
                  <span className="tmdb-result-motivo">{filme.motivo}</span>
                  <span>{formatarData(filme.data_lancamento)}</span>
                </span>

                <span className="tmdb-result-rating">
                  {nota(filme.nota_tmdb)}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      <p className="tmdb-attribution">
        This product uses the TMDB API but is not endorsed or certified by TMDB.
      </p>
    </section>
  );
}

export default Recomendacoes;

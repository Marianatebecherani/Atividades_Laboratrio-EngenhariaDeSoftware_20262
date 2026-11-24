import { useEffect, useState } from "react";

import { listarRecomendacoesTmdb } from "../api";
import FilmeDetalhe from "./FilmeDetalhe";

function formatarData(valor) {
  if (!valor) return "Data de lançamento indisponível";

  return new Date(`${valor}T00:00:00`).toLocaleDateString("pt-BR");
}

function nota(valor) {
  return valor == null ? "Sem nota" : `⭐ ${valor.toFixed(1)}`;
}

function Recomendacoes({ token, usuario }) {
  const [filmes, setFilmes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [detalhe, setDetalhe] = useState(null);

  useEffect(() => {
    let ativo = true;

    async function carregarRecomendacoes() {
        setCarregando(true);
        setErro("");

        try {
        const resposta = await listarRecomendacoesTmdb(token, 10);

        if (ativo) {
            setFilmes(resposta.itens || []);
        }
        } catch (error) {
        if (ativo) {
            setErro(error.message);
        }
        } finally {
        if (ativo) {
            setCarregando(false);
        }
        }
    }

    if (token) {
        carregarRecomendacoes();

        window.addEventListener(
        "recomendacoes:atualizar",
        carregarRecomendacoes,
        );
    } else {
        setFilmes([]);
        setCarregando(false);
    }

    return () => {
        ativo = false;
        window.removeEventListener(
        "recomendacoes:atualizar",
        carregarRecomendacoes,
        );
    };
    }, [token]);

  return (
    <section className="tmdb-search">
      <div className="tmdb-search-heading">
        <div>
          <span className="eyebrow">Sua experiência personalizada</span>
          <h2>Recomendados para você</h2>
          <p>
            Filmes selecionados com base nas suas avaliações.
          </p>
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

      {carregando && (
        <p aria-live="polite">Buscando recomendações para você...</p>
      )}

      {erro && (
        <div className="tmdb-error" role="alert">
          <p>Não foi possível carregar suas recomendações: {erro}</p>
          <button
            type="button"
            onClick={() => {
              setFilmes([]);
              setErro("");
              setCarregando(true);
              listarRecomendacoesTmdb(token, 10)
                .then((resposta) => setFilmes(resposta.itens || []))
                .catch((error) => setErro(error.message))
                .finally(() => setCarregando(false));
            }}
          >
            Tentar novamente
          </button>
        </div>
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
                aria-label={`Ver ${filme.titulo}, ${nota(filme.nota_tmdb)}`}
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

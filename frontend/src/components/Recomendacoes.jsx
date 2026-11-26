import { useLayoutEffect, useRef, useState } from "react";

import { useRecomendacoes } from "../hooks/useRecomendacoes";
import FilmeDetalheModal from "./FilmeDetalheModal";

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
  const [activeCardIndex, setActiveCardIndex] = useState(0);
  const resultadosRef = useRef(null);
  const quantidadeFilmesAnteriorRef = useRef(0);
  const { filmes, estrategiaUsada, tempoMs, carregando, erro, tentarNovamente } =
    useRecomendacoes(token, estrategia);

  const escolhida = ESTRATEGIAS.find((item) => item.valor === estrategia);
  const usouReserva =
    !carregando && !erro && estrategiaUsada !== null && estrategiaUsada !== estrategia;

  useLayoutEffect(() => {
    const faixa = resultadosRef.current;
    if (!filmes.length) {
      quantidadeFilmesAnteriorRef.current = 0;
      return;
    }
    if (!faixa) return;

    const quantidadeAnterior = quantidadeFilmesAnteriorRef.current;
    const deslocamentoInicial = Math.min(2, Math.floor((filmes.length - 1) / 2));
    const indiceRelativo = quantidadeAnterior
      ? Math.max(0, activeCardIndex - quantidadeAnterior)
      : deslocamentoInicial;
    const indiceInicial = filmes.length + Math.min(indiceRelativo, filmes.length - 1);
    const cardInicial = faixa.children[indiceInicial];
    if (!cardInicial) return;

    quantidadeFilmesAnteriorRef.current = filmes.length;
    setActiveCardIndex(indiceInicial);
    const centroFaixa = faixa.getBoundingClientRect().left + faixa.clientWidth / 2;
    const retanguloCard = cardInicial.getBoundingClientRect();
    faixa.scrollLeft += retanguloCard.left + retanguloCard.width / 2 - centroFaixa;
  }, [activeCardIndex, filmes.length]);

  const atualizarCardAtivo = (event) => {
    const faixa = event.currentTarget;
    const centroFaixa = faixa.getBoundingClientRect().left + faixa.clientWidth / 2;
    let indiceMaisProximo = 0;
    let menorDistancia = Number.POSITIVE_INFINITY;

    Array.from(faixa.children).forEach((card, index) => {
      const retangulo = card.getBoundingClientRect();
      const centroCard = retangulo.left + retangulo.width / 2;
      const distancia = Math.abs(centroFaixa - centroCard);

      if (distancia < menorDistancia) {
        menorDistancia = distancia;
        indiceMaisProximo = index;
      }
    });

    let indiceNormalizado = indiceMaisProximo;
    if (indiceMaisProximo < filmes.length) {
      indiceNormalizado += filmes.length;
    } else if (indiceMaisProximo >= filmes.length * 2) {
      indiceNormalizado -= filmes.length;
    }

    if (indiceNormalizado !== indiceMaisProximo) {
      const cardAtivo = faixa.children[indiceMaisProximo];
      const cardEquivalente = faixa.children[indiceNormalizado];
      const centroAtivo = cardAtivo.getBoundingClientRect().left + cardAtivo.getBoundingClientRect().width / 2;
      const centroEquivalente =
        cardEquivalente.getBoundingClientRect().left + cardEquivalente.getBoundingClientRect().width / 2;
      faixa.scrollLeft += centroEquivalente - centroAtivo;
    }

    setActiveCardIndex((atual) => atual === indiceNormalizado ? atual : indiceNormalizado);
  };

  const moverRecomendacoes = (direcao) => {
    const faixa = resultadosRef.current;
    const primeiroCard = faixa?.firstElementChild;
    if (!faixa || !primeiroCard) return;

    const proximoCard = primeiroCard.nextElementSibling;
    const intervalo = proximoCard
      ? proximoCard.offsetLeft - primeiroCard.offsetLeft
      : primeiroCard.offsetWidth;

    faixa.scrollBy({ left: direcao * intervalo, behavior: "smooth" });
  };

  const selecionarEstrategia = (event) => {
    setEstrategia(event.target.value);
    setActiveCardIndex(0);
    resultadosRef.current?.scrollTo({ left: 0 });
  };
  const filmesDoCarrossel = [...filmes, ...filmes, ...filmes];

  return (
    <section className="tmdb-search home-recommendations" aria-labelledby="titulo-recomendacoes">
      <div className="home-recommendation-toolbar">
        <div className="tmdb-search-heading">
          <div>
            <span className="eyebrow">Sua experiência personalizada</span>
            <h2 id="titulo-recomendacoes">Recomendados para você</h2>
            <p>{escolhida.descricao}</p>
          </div>
        </div>
        <div className="tmdb-controls tmdb-recomendacao-controles">
          <label className="tmdb-mode-control">
            Recomendar por
            <select value={estrategia} onChange={selecionarEstrategia}>
              {ESTRATEGIAS.map((item) => (
                <option key={item.valor} value={item.valor}>
                  {item.rotulo}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

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

      {usouReserva && (
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
        <FilmeDetalheModal
          tmdbId={detalhe}
          token={token}
          usuario={usuario}
          onClose={() => setDetalhe(null)}
        />
      )}

      {filmes.length > 0 && (
        <div className="tmdb-carousel">
          {filmes.length > 1 && (
            <button
              className="carousel-button carousel-button-previous"
              type="button"
              aria-label="Rolar recomendações para a esquerda"
              title="Anterior"
              onClick={() => moverRecomendacoes(-1)}
            >
              ‹
            </button>
          )}
          <div
            className="tmdb-results tmdb-results-compact"
            onScroll={atualizarCardAtivo}
            ref={resultadosRef}
          >
            {filmesDoCarrossel.map((filme, index) => (
              <button
                className="tmdb-result"
                data-carousel-position={
                  index === activeCardIndex
                    ? "active"
                    : Math.abs(index - activeCardIndex) === 1
                      ? "near"
                      : "far"
                }
                key={`${filme.tmdb_id}-${index}`}
                type="button"
                aria-hidden={Math.floor(index / filmes.length) !== 1}
                tabIndex={Math.floor(index / filmes.length) !== 1 ? -1 : undefined}
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
          {filmes.length > 1 && (
            <button
              className="carousel-button carousel-button-next"
              type="button"
              aria-label="Rolar recomendações para a direita"
              title="Próximo"
              onClick={() => moverRecomendacoes(1)}
            >
              ›
            </button>
          )}
        </div>
      )}

      {!carregando && !erro && filmes.length > 0 && tempoMs !== null && (
        <p className="tmdb-recomendacao-tempo">Calculado em {tempoMs} ms</p>
      )}

      <p className="tmdb-attribution">
        This product uses the TMDB API but is not endorsed or certified by TMDB.
      </p>
    </section>
  );
}

export default Recomendacoes;

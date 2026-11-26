import { useCallback, useEffect, useState } from "react";

import { listarRecomendacoesTmdb } from "../api";

const LIMITE = 10;

// Carrega as recomendações da estratégia escolhida. Recarrega quando a estratégia muda,
// quando o usuário pede uma nova tentativa e quando um filme é avaliado
// (evento "recomendacoes:atualizar", disparado pelo detalhe do filme).
export function useRecomendacoes(token, estrategia) {
  const [estado, setEstado] = useState({
    filmes: [],
    estrategiaUsada: null,
    tempoMs: null,
    carregando: Boolean(token),
    erro: "",
  });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    if (!token) return undefined;

    let ativo = true;

    async function carregar(limparAnteriores) {
      setEstado((atual) => ({
        ...atual,
        filmes: limparAnteriores ? [] : atual.filmes,
        carregando: true,
        erro: "",
      }));

      try {
        const resposta = await listarRecomendacoesTmdb(token, estrategia, LIMITE);
        if (ativo) {
          setEstado({
            filmes: resposta.itens || [],
            estrategiaUsada: resposta.estrategia,
            tempoMs: resposta.tempo_ms ?? null,
            carregando: false,
            erro: "",
          });
        }
      } catch (error) {
        if (ativo) {
          setEstado({
            filmes: [],
            estrategiaUsada: null,
            tempoMs: null,
            carregando: false,
            erro: error.message,
          });
        }
      }
    }

    // Depois de uma avaliação, mantém os filmes na tela até a nova lista chegar.
    const recarregar = () => carregar(false);

    carregar(true);
    window.addEventListener("recomendacoes:atualizar", recarregar);

    return () => {
      ativo = false;
      window.removeEventListener("recomendacoes:atualizar", recarregar);
    };
  }, [token, estrategia, tentativa]);

  const tentarNovamente = useCallback(() => setTentativa((atual) => atual + 1), []);

  return { ...estado, tentarNovamente };
}

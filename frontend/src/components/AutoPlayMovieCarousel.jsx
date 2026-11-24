import { useEffect, useState } from "react";
import { listarFilmesTmdb } from "../api";

function AutoPlayMovieCarousel() {
  const [filmes, setFilmes] = useState([]);
  const [ativo, setAtivo] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [pausado, setPausado] = useState(false);

  useEffect(() => {
    const carregar = async () => {
      try {
        setCarregando(true);
        const dados = await listarFilmesTmdb("populares", 1);
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

  // Auto-play do carrossel
  useEffect(() => {
    if (filmes.length === 0 || pausado) return;

    const intervalo = setInterval(() => {
      setAtivo((prev) => (prev + 1) % filmes.length);
    }, 5000);

    return () => clearInterval(intervalo);
  }, [filmes, pausado]);

  // Atualiza o background da hero-wrapper
  useEffect(() => {
    if (filmes.length === 0) return;

    const filmeAtual = filmes[ativo];
    const wrapper = document.querySelector(".landing-hero-wrapper");
    
    if (wrapper && filmeAtual.poster_url) {
      wrapper.style.backgroundImage = `url(${filmeAtual.poster_url})`;
    }
  }, [ativo, filmes]);

  if (carregando || filmes.length === 0) {
    return null;
  }

  if (erro) {
    return null;
  }

  return null;
}

export default AutoPlayMovieCarousel;

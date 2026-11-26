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

  // Atualiza o background do carousel
  useEffect(() => {
    if (filmes.length === 0) return;

    const filmeAtual = filmes[ativo];
    const carousel = document.querySelector(".landing-carousel-background");
    
    if (carousel && filmeAtual.poster_url) {
      carousel.style.backgroundImage = `url(${filmeAtual.poster_url})`;
    }
  }, [ativo, filmes]);

  if (erro) {
    return null;
  }

  return null;
}

export default AutoPlayMovieCarousel;

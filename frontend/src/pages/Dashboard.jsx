import { useEffect, useState } from "react";

import {
  avaliarObra,
  avaliacaoDaApi,
  definirStatusLista,
  filmeDaApi,
  listarAvaliacoes,
  listarGeneros,
  listarMinhaLista,
  listarObras,
  obterRecomendacoes,
} from "../api";

import Sidebar from "../components/Sidebar";

import Inicio from "./Inicio";
import Busca from "./Busca";
import MinhaLista from "./MinhaLista";
import Filme from "./Filme";

async function carregarDados(token) {
  const [catalogo, generos, lista] = await Promise.all([
    listarObras(token),
    listarGeneros(token),
    listarMinhaLista(token),
  ]);

  let recomendacoes = [];
  try {
    const resposta = await obterRecomendacoes(token);
    recomendacoes = resposta.itens.map((item) => filmeDaApi(item.obra));
  } catch {
    recomendacoes = [];
  }

  return {
    movies: catalogo.itens.map(filmeDaApi),
    genres: generos.map((genero) => genero.nome),
    myList: lista.itens.map((item) => ({
      ...filmeDaApi(item.obra),
      listStatus: item.status,
    })),
    recommendations: recomendacoes,
  };
}

function Dashboard({ token, usuario, onLogout }) {
  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState([]);
  const [myList, setMyList] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [menuOpen, setMenuOpen] =
    useState(true);

  const [activePage, setActivePage] =
    useState("inicio");

  const [selectedMovie, setSelectedMovie] =
    useState(null);

  const [searchTerm, setSearchTerm] =
    useState("");

  const [selectedGenres, setSelectedGenres] =
    useState([]);

  const [selectedRatings, setSelectedRatings] =
    useState([]);

  const [selectedClassifications, setSelectedClassifications] =
    useState([]);

  const aplicarDados = (dados) => {
    setMovies(dados.movies);
    setGenres(dados.genres);
    setMyList(dados.myList);
    setRecommendations(dados.recommendations);
  };

  useEffect(() => {
    let ativo = true;
    carregarDados(token)
      .then((dados) => {
        if (ativo) aplicarDados(dados);
      })
      .catch((error) => {
        if (ativo) setLoadError(error.message);
      })
      .finally(() => {
        if (ativo) setLoading(false);
      });
    return () => {
      ativo = false;
    };
  }, [token]);


  const toggleGenre = (genre) => {

    setSelectedGenres((current) => {

      if (current.includes(genre)) {
        return current.filter(
          (item) => item !== genre
        );
      }

      return [...current, genre];
    });
  };


  const toggleRating = (rating) => {

    setSelectedRatings((current) => {

      if (current.includes(rating)) {
        return current.filter(
          (item) => item !== rating
        );
      }

      return [...current, rating];
    });
  };


  const toggleClassification =
    (classification) => {

      setSelectedClassifications(
        (current) => {

          if (
            current.includes(classification)
          ) {
            return current.filter(
              (item) =>
                item !== classification
            );
          }

          return [
            ...current,
            classification
          ];
        }
      );
    };


  const handleMovieClick = (movie) => {
    setSelectedMovie({ ...movie, avaliacoes: [], carregandoAvaliacoes: true });
  };

  const selectedMovieId = selectedMovie?.id;

  useEffect(() => {
    if (!selectedMovieId) return undefined;
    let ativo = true;
    listarAvaliacoes(selectedMovieId, token)
      .then((resposta) => {
        if (ativo) {
          setSelectedMovie((atual) =>
            atual?.id === selectedMovieId
              ? {
                  ...atual,
                  avaliacoes: resposta.itens.map(avaliacaoDaApi),
                  carregandoAvaliacoes: false,
                }
              : atual,
          );
        }
      })
      .catch(() => {
        if (ativo) {
          setSelectedMovie((atual) =>
            atual?.id === selectedMovieId
              ? { ...atual, carregandoAvaliacoes: false }
              : atual,
          );
        }
      });
    return () => {
      ativo = false;
    };
  }, [selectedMovieId, token]);

  const handleReview = async (nota, comentario) => {
    await avaliarObra(selectedMovie.id, nota, comentario, token);
    const [avaliacoes, dados] = await Promise.all([
      listarAvaliacoes(selectedMovie.id, token),
      carregarDados(token),
    ]);
    aplicarDados(dados);
    setSelectedMovie((atual) => ({
      ...atual,
      avaliacoes: avaliacoes.itens.map(avaliacaoDaApi),
      rating: dados.movies.find((movie) => movie.id === atual.id)?.rating ?? atual.rating,
    }));
  };

  const handleListStatus = async (status) => {
    await definirStatusLista(selectedMovie.id, status, token);
    aplicarDados(await carregarDados(token));
    setSelectedMovie((atual) => ({ ...atual, meuStatus: status }));
  };


  if (selectedMovie) {

    return (
      <Filme
        movie={selectedMovie}
        onReview={handleReview}
        onSetStatus={handleListStatus}
        onBack={() =>
          setSelectedMovie(null)
        }
      />
    );

  }


  return (
    <div className="dashboard">

      <Sidebar
        menuOpen={menuOpen}
        activePage={activePage}
        setActivePage={setActivePage}
        onLogout={onLogout}
      />

      <main
        className={`dashboard-main ${
          menuOpen
            ? "sidebar-open"
            : ""
        }`}
      >

        <header className="dashboard-header">

          <button
            className="menu-button"
            onClick={() =>
              setMenuOpen(!menuOpen)
            }
          >
            ☰
          </button>

          <div className="dashboard-user">

            <div className="user-avatar">
              {usuario?.nome?.[0]?.toUpperCase() || "U"}
            </div>

            <span>
              {usuario?.nome || "Usuário"}
            </span>

          </div>

        </header>


        {loadError && <div className="data-error" role="alert">{loadError}</div>}
        {loading && <div className="data-loading">Carregando catálogo...</div>}

        {!loading && !loadError && activePage === "inicio" && (

          <Inicio
            movies={movies}
            recommendations={recommendations}
            token={token}
            onMovieClick={
              handleMovieClick
            }
          />

        )}


        {!loading && !loadError && activePage === "busca" && (

          <Busca
            movies={movies}
            genres={genres}
            token={token}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            selectedGenres={
              selectedGenres
            }
            selectedRatings={
              selectedRatings
            }
            selectedClassifications={
              selectedClassifications
            }
            toggleGenre={toggleGenre}
            toggleRating={toggleRating}
            toggleClassification={
              toggleClassification
            }
            onMovieClick={
              handleMovieClick
            }
          />

        )}


        {!loading && !loadError && activePage === "lista" && (

          <MinhaLista
            movies={myList}
            token={token}
            onMovieClick={
              handleMovieClick
            }
          />

        )}

      </main>

    </div>
  );
}

export default Dashboard;
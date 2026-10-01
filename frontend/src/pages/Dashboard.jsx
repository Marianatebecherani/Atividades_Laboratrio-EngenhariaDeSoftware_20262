import { useState } from "react";

import Sidebar from "../components/Sidebar";

import Inicio from "./Inicio";
import Busca from "./Busca";
import MinhaLista from "./MinhaLista";
import Filme from "./Filme";

function Dashboard({
  movies,
  onLogout
}) {

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
    setSelectedMovie(movie);
  };


  if (selectedMovie) {

    return (
      <Filme
        movie={selectedMovie}
        onBack={() =>
          setSelectedMovie(null)
        }
        onLogout={onLogout}
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
              U
            </div>

            <span>
              Usuário
            </span>

          </div>

        </header>


        {activePage === "inicio" && (

          <Inicio
            movies={movies}
            onMovieClick={
              handleMovieClick
            }
          />

        )}


        {activePage === "busca" && (

          <Busca
            movies={movies}
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


        {activePage === "lista" && (

          <MinhaLista
            movies={movies}
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
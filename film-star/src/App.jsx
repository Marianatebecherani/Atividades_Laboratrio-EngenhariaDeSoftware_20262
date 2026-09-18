import { useState } from "react";
import "./App.css";

/* =========================================================
   FILMES
========================================================= */

const movies = [
  {
    id: 1,
    title: "Interestelar",
    genres: ["Drama", "Ficção Científica"],
    genre: "Drama",
    rating: 4.9,
    classification: 10,
    emoji: "🚀",
    avaliado: true,
    type: "pessoal",

    sinopse:
      "Um grupo de astronautas viaja através de um buraco de minhoca em busca de um novo planeta que possa abrigar a humanidade.",

    avaliacoes: [
      {
        usuario: "Carlos",
        nota: 5,
        comentario: "Um dos melhores filmes que já assisti.",
      },
      {
        usuario: "Mariana",
        nota: 4.5,
        comentario: "A história é incrível e os efeitos são excelentes.",
      },
      {
        usuario: "Lucas",
        nota: 5,
        comentario: "Filme emocionante do começo ao fim.",
      },
    ],
  },
  {
    id: 2,
    title: "O Poderoso Chefão",
    genres: ["Drama", "Crime"],
    genre: "Drama",
    rating: 4.9,
    classification: 16,
    emoji: "🎩",
    avaliado: true,
    type: "pessoal",
  },
  {
    id: 3,
    title: "O Senhor dos Anéis",
    genres: ["Aventura", "Fantasia"],
    genre: "Aventura",
    rating: 4.8,
    classification: 12,
    emoji: "💍",
    avaliado: false,
    type: "pessoal",
  },
  {
    id: 4,
    title: "Matrix",
    genres: ["Ação", "Ficção Científica"],
    genre: "Ação",
    rating: 4.8,
    classification: 14,
    emoji: "💊",
    avaliado: false,
    type: "pessoal",
  },
  {
    id: 5,
    title: "Forrest Gump",
    genres: ["Drama", "Romance"],
    genre: "Drama",
    rating: 4.7,
    classification: 12,
    emoji: "🏃",
    avaliado: false,
    type: "pessoal",
  },
  {
    id: 6,
    title: "Invocação do Mal",
    genres: ["Terror", "Mistério"],
    genre: "Terror",
    rating: 4.7,
    classification: 16,
    emoji: "👻",
    avaliado: true,
    type: "terror",
  },
  {
    id: 7,
    title: "O Exorcista",
    genres: ["Terror"],
    genre: "Terror",
    rating: 4.7,
    classification: 18,
    emoji: "😈",
    avaliado: false,
    type: "terror",
  },
  {
    id: 8,
    title: "Batman",
    genres: ["Ação", "Crime"],
    genre: "Ação",
    rating: 4.6,
    classification: 14,
    emoji: "🦇",
    avaliado: false,
    type: "pessoal",
  },
  {
    id: 9,
    title: "Clube da Luta",
    genres: ["Drama", "Crime"],
    genre: "Drama",
    rating: 4.6,
    classification: 18,
    emoji: "🥊",
    avaliado: false,
    type: "drama",
  },
  {
    id: 10,
    title: "Toy Story",
    genres: ["Animação", "Comédia"],
    genre: "Comédia",
    rating: 4.5,
    classification: 0,
    emoji: "🤠",
    avaliado: false,
    type: "comedia",
  },
  {
    id: 11,
    title: "O Iluminado",
    genres: ["Terror", "Drama"],
    genre: "Terror",
    rating: 4.5,
    classification: 18,
    emoji: "🔪",
    avaliado: false,
    type: "terror",
  },
  {
    id: 12,
    title: "A Origem",
    genres: ["Ação", "Ficção Científica"],
    genre: "Ficção Científica",
    rating: 4.5,
    classification: 14,
    emoji: "🌀",
    avaliado: false,
    type: "pessoal",
  },
  {
    id: 13,
    title: "Os Bons Companheiros",
    genres: ["Crime", "Drama"],
    genre: "Crime",
    rating: 4.4,
    classification: 18,
    emoji: "🔫",
    avaliado: false,
    type: "drama",
  },
  {
    id: 14,
    title: "Pulp Fiction",
    genres: ["Crime", "Drama"],
    genre: "Crime",
    rating: 4.4,
    classification: 18,
    emoji: "💼",
    avaliado: false,
    type: "drama",
  },
  {
    id: 15,
    title: "Gladiador",
    genres: ["Ação", "Drama"],
    genre: "Ação",
    rating: 4.4,
    classification: 16,
    emoji: "⚔️",
    avaliado: false,
    type: "pessoal",
  },
  {
    id: 16,
    title: "De Volta para o Futuro",
    genres: ["Aventura", "Ficção Científica", "Comédia"],
    genre: "Ficção Científica",
    rating: 4.3,
    classification: 10,
    emoji: "⏰",
    avaliado: false,
    type: "comedia",
  },
  {
    id: 17,
    title: "Superbad",
    genres: ["Comédia"],
    genre: "Comédia",
    rating: 4.2,
    classification: 16,
    emoji: "😂",
    avaliado: false,
    type: "comedia",
  },
  {
    id: 18,
    title: "As Branquelas",
    genres: ["Comédia"],
    genre: "Comédia",
    rating: 4.1,
    classification: 12,
    emoji: "👯",
    avaliado: false,
    type: "comedia",
  },
  {
    id: 19,
    title: "Se Beber, Não Case",
    genres: ["Comédia"],
    genre: "Comédia",
    rating: 4.1,
    classification: 16,
    emoji: "🍻",
    avaliado: false,
    type: "comedia",
  },
  {
    id: 20,
    title: "O Máskara",
    genres: ["Comédia", "Fantasia"],
    genre: "Comédia",
    rating: 4.0,
    classification: 10,
    emoji: "🎭",
    avaliado: false,
    type: "comedia",
  },
  {
    id: 21,
    title: "Corra!",
    genres: ["Terror", "Mistério"],
    genre: "Terror",
    rating: 4.3,
    classification: 14,
    emoji: "🏃‍♂️",
    avaliado: false,
    type: "terror",
  },
  {
    id: 22,
    title: "Hereditário",
    genres: ["Terror", "Drama"],
    genre: "Terror",
    rating: 4.2,
    classification: 16,
    emoji: "🏚️",
    avaliado: false,
    type: "terror",
  },
  {
    id: 23,
    title: "Um Lugar Silencioso",
    genres: ["Terror", "Drama"],
    genre: "Terror",
    rating: 4.1,
    classification: 14,
    emoji: "🤫",
    avaliado: false,
    type: "terror",
  },
  {
    id: 24,
    title: "O Auto da Compadecida",
    genres: ["Comédia", "Drama"],
    genre: "Comédia",
    rating: 4.8,
    classification: 12,
    emoji: "🎭",
    avaliado: true,
    type: "pessoal",
  },
  {
    id: 25,
    title: "Cidade de Deus",
    genres: ["Crime", "Drama"],
    genre: "Crime",
    rating: 4.8,
    classification: 18,
    emoji: "🏙️",
    avaliado: false,
    type: "drama",
  },
  {
    id: 26,
    title: "Tropa de Elite",
    genres: ["Ação", "Crime", "Drama"],
    genre: "Ação",
    rating: 4.7,
    classification: 16,
    emoji: "🛡️",
    avaliado: false,
    type: "drama",
  },
  {
    id: 27,
    title: "O Labirinto do Fauno",
    genres: ["Fantasia", "Drama"],
    genre: "Fantasia",
    rating: 4.6,
    classification: 14,
    emoji: "🧚",
    avaliado: false,
    type: "drama",
  },
  {
    id: 28,
    title: "Parasita",
    genres: ["Drama", "Crime"],
    genre: "Drama",
    rating: 4.6,
    classification: 16,
    emoji: "🏠",
    avaliado: false,
    type: "drama",
  },
  {
    id: 29,
    title: "Whiplash",
    genres: ["Drama", "Música"],
    genre: "Drama",
    rating: 4.5,
    classification: 12,
    emoji: "🥁",
    avaliado: false,
    type: "drama",
  },
  {
    id: 30,
    title: "O Show de Truman",
    genres: ["Drama", "Comédia"],
    genre: "Drama",
    rating: 4.5,
    classification: 10,
    emoji: "📺",
    avaliado: false,
    type: "pessoal",
  },
];

/* =========================================================
   CARD DE FILME
========================================================= */

function MovieCard({ movie, onClick }) {
  return (
    <div
      className="movie-card-dashboard"
      onClick={() => onClick(movie)}
    >
      <div className="movie-poster">
        <span className="movie-emoji">
          {movie.emoji}
        </span>

        <div className="poster-gradient"></div>

        <div className="poster-rating">
          ⭐ {movie.rating}
        </div>
      </div>

      <div className="movie-card-info">
        <h3>{movie.title}</h3>
        <span>{movie.genre}</span>
      </div>
    </div>
  );
}


/* =========================================================
   FILA DE FILMES
========================================================= */

function MovieRow({ title, movies, onMovieClick }) {
  return (
    <section className="movie-section">

      <div className="movie-section-header">

        <h2>{title}</h2>

        <button className="see-all">
          Ver todos →
        </button>

      </div>

      <div className="movie-row">

        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onClick={onMovieClick}
          />
        ))}

      </div>

    </section>
  );
}


/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard({ onLogout }) {

  const [menuOpen, setMenuOpen] = useState(true);
  const [activePage, setActivePage] = useState("inicio");
  const [selectedMovie, setSelectedMovie] = useState(null);
  const filmesAvaliados = movies.filter((movie) => movie.avaliado);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [selectedRatings, setSelectedRatings] = useState([]);
  const [selectedClassifications, setSelectedClassifications] = useState([]);

  //pra avaliações dos usuários
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState("");


  const handleMovieClick = (movie) => {
    setSelectedMovie(movie);
  };

  const genres = [
  "Ação",
  "Aventura",
  "Animação",
  "Comédia",
  "Crime",
  "Drama",
  "Fantasia",
  "Ficção Científica",
  "Mistério",
  "Romance",
  "Terror",
];

const filteredMovies = movies
  .filter((movie) => {
    const matchesSearch = movie.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    const matchesGenre =
      selectedGenres.length === 0 ||
      selectedGenres.some((genre) =>
        movie.genres.includes(genre)
      );

    const matchesRating =
      selectedRatings.length === 0 ||
      selectedRatings.some((range) => {
        if (range === "0-1") {
          return movie.rating >= 0 && movie.rating < 1;
        }

        if (range === "1-2") {
          return movie.rating >= 1 && movie.rating < 2;
        }

        if (range === "2-3") {
          return movie.rating >= 2 && movie.rating < 3;
        }

        if (range === "3-4") {
          return movie.rating >= 3 && movie.rating < 4;
        }

        if (range === "4-4.5") {
          return movie.rating >= 4 && movie.rating < 4.5;
        }

        if (range === "4.5-5") {
          return movie.rating >= 4.5 && movie.rating <= 5;
        }

        return false;
      });

    const matchesClassification =
      selectedClassifications.length === 0 ||
      selectedClassifications.includes(movie.classification);

    return (
      matchesSearch &&
      matchesGenre &&
      matchesRating &&
      matchesClassification
    );
  })
  .sort((a, b) => b.rating - a.rating);

  const toggleGenre = (genre) => {
    setSelectedGenres((current) => {
      if (current.includes(genre)) {
        return current.filter((item) => item !== genre);
      }

      return [...current, genre];
    });
  };

  const toggleRating = (rating) => {
    setSelectedRatings((current) => {
      if (current.includes(rating)) {
        return current.filter((item) => item !== rating);
      }

      return [...current, rating];
    });
  };

  const toggleClassification = (classification) => {
    setSelectedClassifications((current) => {
      if (current.includes(classification)) {
        return current.filter((item) => item !== classification);
      }

      return [...current, classification];
    });
  };

  /* ==========================================
     PÁGINA DO FILME
  ========================================== */

  if (selectedMovie) {

  return (
    <div className="dashboard">

      {/* ======================================
        SIDEBAR
      ====================================== */}

        <aside
          className={`sidebar ${menuOpen ? "open" : ""}`}
        >

          <div className="sidebar-logo">

            <span>★</span>

            {menuOpen && (
              <strong>
                Film<span>Star</span>
              </strong>
            )}

          </div>


          <nav className="sidebar-nav">

            <button
              className={
                activePage === "inicio"
                  ? "active"
                  : ""
              }
              onClick={() => {
                setActivePage("inicio");
                setSelectedMovie(null);
              }}
            >
              <span>🏠</span>

              {menuOpen && (
                <span>Início</span>
              )}
            </button>


            <button
              className={
                activePage === "busca"
                  ? "active"
                  : ""
              }
              onClick={() => {
                setActivePage("busca");
                setSelectedMovie(null);
              }}
            >
              <span>🔍</span>

              {menuOpen && (
                <span>Busca</span>
              )}
            </button>


            <button
              className={
                activePage === "lista"
                  ? "active"
                  : ""
              }
              onClick={() => {
                setActivePage("lista");
                setSelectedMovie(null);
              }}
            >
              <span>❤️</span>

              {menuOpen && (
                <span>Minha Lista</span>
              )}
            </button>

          </nav>


          <button
            className="logout-button"
            onClick={onLogout}
          >
            <span>↪</span>

            {menuOpen && (
              <span>Sair</span>
            )}
          </button>

        </aside>


        {/* ======================================
            CONTEÚDO DO FILME
        ====================================== */}

        <main
          className={`dashboard-main ${
            menuOpen ? "sidebar-open" : ""
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


          <section className="movie-detail-page">

            {/* VOLTAR */}

            <button
              className="back-button"
              onClick={() =>
                setSelectedMovie(null)
              }
            >
              ← Voltar
            </button>


            {/* ====================================
                INFORMAÇÕES DO FILME
            ==================================== */}

            <div className="movie-detail-main">

              {/* CAPA */}

              <div className="detail-poster">

                <span>
                  {selectedMovie.emoji}
                </span>

              </div>


              {/* INFORMAÇÕES */}

              <div className="detail-info">

                <h1>
                  {selectedMovie.title}
                </h1>


                <div className="detail-rating">

                  ⭐ {selectedMovie.rating}

                </div>


                <div className="detail-genres">

                  {selectedMovie.genres.map(
                    (genre) => (
                      <span
                        key={genre}
                        className="genre-tag"
                      >
                        {genre}
                      </span>
                    )
                  )}

                </div>


                <div className="detail-synopsis">

                  <h2>
                    Sinopse
                  </h2>

                  <p>
                    {selectedMovie.sinopse ||
                      "Sinopse deste filme será adicionada em breve."}
                  </p>

                </div>

              </div>

            </div>


            {/* ====================================
                AVALIAÇÕES
            ==================================== */}

            <div className="reviews-section">

              <div className="reviews-header">

                <div>

                  <span className="eyebrow">
                    Comunidade
                  </span>

                  <h2>
                    Avaliações dos usuários
                  </h2>

                </div>


                <button
                  className="rate-button"
                  onClick={() =>
                    setShowReviewModal(true)
                  }
                >
                  ⭐ Avaliar filme
                </button>

              </div>


              <div className="reviews-list">

                {selectedMovie.avaliacoes &&
                selectedMovie.avaliacoes.length > 0 ? (

                  selectedMovie.avaliacoes.map(
                    (review, index) => (

                      <div
                        className="review-card"
                        key={index}
                      >

                        <div className="review-header">

                          <strong>
                            {review.usuario}
                          </strong>

                          <span className="review-rating">
                            ⭐ {review.nota}
                          </span>

                        </div>


                        <p>
                          {review.comentario}
                        </p>

                      </div>

                    )
                  )

                ) : (

                  <div className="empty-state">

                    <span className="empty-icon">
                      💬
                    </span>

                    <h2>
                      Ainda não existem avaliações
                    </h2>

                    <p>
                      Seja o primeiro a avaliar este filme.
                    </p>

                  </div>

                )}

              </div>

            </div>

          </section>


          {/* ====================================
              MODAL DE AVALIAÇÃO
          ==================================== */}

          {showReviewModal && (

            <div
              className="review-modal-overlay"
              onClick={() =>
                setShowReviewModal(false)
              }
            >

              <div
                className="review-modal"
                onClick={(event) =>
                  event.stopPropagation()
                }
              >

                <button
                  className="modal-close"
                  onClick={() =>
                    setShowReviewModal(false)
                  }
                >
                  ×
                </button>


                <div className="modal-icon">
                  ⭐
                </div>


                <h2>
                  Avaliar filme
                </h2>


                <p className="modal-description">
                  Compartilhe sua opinião sobre{" "}
                  <strong>
                    {selectedMovie.title}
                  </strong>
                </p>


                {/* NOTA */}

                <div className="review-rating-selector">

                  <label>
                    Sua nota
                  </label>

                  <div className="rating-stars">

                    {[1, 2, 3, 4, 5].map(
                      (star) => (

                        <button
                          key={star}
                          type="button"
                          className={
                            star <= reviewRating
                              ? "star selected"
                              : "star"
                          }
                          onClick={() =>
                            setReviewRating(star)
                          }
                        >
                          ★
                        </button>

                      )
                    )}

                  </div>

                </div>


                {/* COMENTÁRIO */}

                <div className="input-group">

                  <label>
                    Comentário
                  </label>

                  <textarea
                    placeholder="Digite seu comentário..."
                    value={reviewComment}
                    onChange={(event) =>
                      setReviewComment(
                        event.target.value
                      )
                    }
                  />

                </div>


                <button
                  className="modal-button"
                  disabled={
                    reviewRating === 0 ||
                    reviewComment.trim() === ""
                  }
                  onClick={() => {

                    console.log({
                      filme: selectedMovie.title,
                      nota: reviewRating,
                      comentario: reviewComment,
                    });

                    setShowReviewModal(false);

                    setReviewRating(0);

                    setReviewComment("");
                  }}
                >
                  Publicar avaliação
                </button>

              </div>

            </div>

          )}

        </main>

      </div>
    );
  }


  /* ==========================================
     DASHBOARD NORMAL
  ========================================== */

  return (
    <div className="dashboard">

      {/* ======================================
          SIDEBAR
      ====================================== */}

      <aside
        className={`sidebar ${menuOpen ? "open" : ""}`}
      >

        <div className="sidebar-logo">

          <span>★</span>

          {menuOpen && (
            <strong>
              Film<span>Star</span>
            </strong>
          )}

        </div>


        <nav className="sidebar-nav">

          <button
            className={
              activePage === "inicio"
                ? "active"
                : ""
            }
            onClick={() => setActivePage("inicio")}
          >

            <span>🏠</span>

            {menuOpen && (
              <span>Início</span>
            )}

          </button>


          <button
            className={
              activePage === "busca"
                ? "active"
                : ""
            }
            onClick={() => setActivePage("busca")}
          >

            <span>🔍</span>

            {menuOpen && (
              <span>Busca</span>
            )}

          </button>


          <button
            className={
              activePage === "lista"
                ? "active"
                : ""
            }
            onClick={() => setActivePage("lista")}
          >

            <span>❤️</span>

            {menuOpen && (
              <span>Minha Lista</span>
            )}

          </button>

        </nav>


        <button
          className="logout-button"
          onClick={onLogout}
        >

          <span>↪</span>

          {menuOpen && (
            <span>Sair</span>
          )}

        </button>

      </aside>


      {/* ======================================
          CONTEÚDO
      ====================================== */}

      <main
        className={`dashboard-main ${
          menuOpen ? "sidebar-open" : ""
        }`}
      >

        {/* HEADER */}

        <header className="dashboard-header">

          <button
            className="menu-button"
            onClick={() => setMenuOpen(!menuOpen)}
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


        {/* ====================================
            INÍCIO
        ==================================== */}

        {activePage === "inicio" && (

          <div className="home-content">

            <section className="welcome-section">

              <div>

                <span>
                  BEM-VINDO AO FILM STAR
                </span>

                <h1>
                  O que você quer
                  <br />
                  assistir hoje?
                </h1>

                <p>
                  Descubra novos filmes e encontre
                  histórias que combinam com você.
                </p>

              </div>

            </section>


            <MovieRow
              title="Recomendações pessoais"
              movies={movies.filter(
                (movie) => movie.type === "pessoal"
              )}
              onMovieClick={handleMovieClick}
            />


            <MovieRow
              title="Comédia"
              movies={movies.filter(
                (movie) => movie.type === "comedia"
              )}
              onMovieClick={handleMovieClick}
            />


            <MovieRow
              title="Drama"
              movies={movies.filter(
                (movie) => movie.type === "drama"
              )}
              onMovieClick={handleMovieClick}
            />


            <MovieRow
              title="Terror"
              movies={movies.filter(
                (movie) => movie.type === "terror"
              )}
              onMovieClick={handleMovieClick}
            />

          </div>

        )}


        {/* ====================================
            BUSCA
        ==================================== */}

        {activePage === "busca" && (
          <section className="page-section search-page">

            <div className="page-heading">
              <span className="eyebrow">
                Explore o catálogo
              </span>

              <h1>
                Buscar filmes
              </h1>

              <p>
                Encontre seu próximo filme favorito.
              </p>
            </div>


            {/* ====================================
                BARRA DE BUSCA
            ==================================== */}

            <div className="search-box">

              <span>🔎</span>

              <input
                type="text"
                placeholder="Pesquisar pelo nome do filme..."
                value={searchTerm}
                onChange={(event) =>
                  setSearchTerm(event.target.value)
                }
              />

            </div>


            {/* ====================================
                FILTROS
            ==================================== */}

            <div className="filters">

              {/* GÊNEROS */}

              <div className="filter-group">

                <h3>
                  Gêneros
                </h3>

                <div className="filter-options">

                  {genres.map((genre) => (

                    <button
                      key={genre}
                      className={
                        selectedGenres.includes(genre)
                          ? "filter-button active"
                          : "filter-button"
                      }
                      onClick={() =>
                        toggleGenre(genre)
                      }
                    >
                      {genre}
                    </button>

                  ))}

                </div>

              </div>


              {/* NOTA */}

              <div className="filter-group">

                <h3>
                  Nota
                </h3>

                <div className="filter-options">

                  {[
                    ["0-1", "0 - 1 ⭐"],
                    ["1-2", "1 - 2 ⭐"],
                    ["2-3", "2 - 3 ⭐"],
                    ["3-4", "3 - 4 ⭐"],
                    ["4-4.5", "4 - 4.5 ⭐"],
                    ["4.5-5", "4.5 - 5 ⭐"],
                  ].map(([value, label]) => (

                    <button
                      key={value}
                      className={
                        selectedRatings.includes(value)
                          ? "filter-button active"
                          : "filter-button"
                      }
                      onClick={() =>
                        toggleRating(value)
                      }
                    >
                      {label}
                    </button>

                  ))}

                </div>

              </div>


              {/* CLASSIFICAÇÃO */}

              <div className="filter-group">

                <h3>
                  Classificação indicativa
                </h3>

                <div className="filter-options">

                  {[
                    [0, "Livre"],
                    [10, "10 anos"],
                    [12, "12 anos"],
                    [14, "14 anos"],
                    [16, "16 anos"],
                    [18, "18 anos"],
                  ].map(([value, label]) => (

                    <button
                      key={value}
                      className={
                        selectedClassifications.includes(value)
                          ? "filter-button active"
                          : "filter-button"
                      }
                      onClick={() =>
                        toggleClassification(value)
                      }
                    >
                      {label}
                    </button>

                  ))}

                </div>

              </div>

            </div>


            {/* ====================================
                RESULTADOS
            ==================================== */}

            <div className="search-results">

              <div className="results-header">

                <div>

                  <span className="eyebrow">

                    {searchTerm ||
                    selectedGenres.length > 0 ||
                    selectedRatings.length > 0 ||
                    selectedClassifications.length > 0
                      ? "Resultados"
                      : "Em destaque"}

                  </span>

                  <h2>
                    {filteredMovies.length} filmes encontrados
                  </h2>

                </div>

              </div>


              {/* FILMES */}

              {filteredMovies.length > 0 ? (

                <div className="movie-grid">

                  {filteredMovies.map((movie) => (

                    <MovieCard
                      key={movie.id}
                      movie={movie}
                      onClick={() =>
                        setSelectedMovie(movie)
                      }
                    />

                  ))}

                </div>

              ) : (

                <div className="empty-state">

                  <span className="empty-icon">
                    🔎
                  </span>

                  <h2>
                    Nenhum filme encontrado
                  </h2>

                  <p>
                    Tente alterar sua busca ou seus filtros.
                  </p>

                </div>

              )}

            </div>

          </section>
        )}

        {/* ====================================
            MINHA LISTA
        ==================================== */}

        {activePage === "lista" && (
          <section className="page-section">
            <div className="page-heading">
              <span className="eyebrow">Sua coleção</span>
              <h1>Minha Lista</h1>
              <p>
                Filmes que você já avaliou.
              </p>
            </div>

            {filmesAvaliados.length > 0 ? (
              <div className="movie-grid">
                {filmesAvaliados.map((movie) => (
                  <MovieCard
                    key={movie.id}
                    movie={movie}
                    onClick={() => setSelectedMovie(movie)}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <span className="empty-icon">🎬</span>

                <h2>Sua lista está vazia</h2>

                <p>
                  Você ainda não avaliou nenhum filme.
                </p>

                <button
                  className="primary-button"
                  onClick={() => setActivePage("inicio")}
                >
                  Explorar filmes
                </button>
              </div>
            )}
          </section>
        )}

      </main>

    </div>
  );
}


/* =========================================================
   APP PRINCIPAL
========================================================= */

function App() {

  const [modal, setModal] = useState(null);

  const [loggedIn, setLoggedIn] = useState(false);


  const openModal = (type) => {
    setModal(type);
  };


  const closeModal = () => {
    setModal(null);
  };


  const handleSubmit = (event) => {

    event.preventDefault();

    /*
      Por enquanto simulamos o login.

      Quando o backend estiver pronto,
      aqui entra a requisição para a API.
    */

    setModal(null);

    setLoggedIn(true);
  };


  const handleLogout = () => {
    setLoggedIn(false);
  };


  /* ==========================================
     USUÁRIO LOGADO
  ========================================== */

  if (loggedIn) {

    return (
      <Dashboard
        onLogout={handleLogout}
      />
    );

  }


  /* ==========================================
     LANDING PAGE
  ========================================== */

  return (
    <div className="app">

      <header className="header">

        <div className="logo">

          <span className="logo-star">
            ★
          </span>

          <span>
            Film<span>Star</span>
          </span>

        </div>


        <nav className="nav">

          <button
            className="btn btn-login"
            onClick={() => openModal("login")}
          >
            Login
          </button>


          <button
            className="btn btn-register"
            onClick={() => openModal("register")}
          >
            Registrar
          </button>

        </nav>

      </header>


      <main>

        <section className="hero">

          <div className="hero-content">

            <div className="badge">
              ⭐ O seu lugar para falar de filmes
            </div>

            <h1>
              Descubra.
              <br />

              <span>Avalie.</span>

              <br />

              Compartilhe.
            </h1>

            <p className="hero-description">
              Encontre seus próximos filmes favoritos,
              avalie o que você assistiu e descubra
              o que outros apaixonados por cinema estão assistindo.
            </p>

            <div className="hero-buttons">

              <button
                className="main-button"
                onClick={() => openModal("register")}
              >
                Começar agora
                <span>→</span>
              </button>

              <button
                className="secondary-button"
                onClick={() => openModal("login")}
              >
                Já tenho uma conta
              </button>

            </div>

          </div>


          <div className="hero-visual">

            <div className="glow glow-pink"></div>
            <div className="glow glow-blue"></div>

            <div className="movie-card card-back">

              <div className="movie-image image-three">
                🎥
              </div>

              <div className="movie-info">

                <span>
                  Drama
                </span>

                <strong>
                  Minha História
                </strong>

                <div className="stars">
                  ★★★★★
                </div>

              </div>

            </div>


            <div className="movie-card card-middle">

              <div className="movie-image image-two">
                🍿
              </div>

              <div className="movie-info">

                <span>
                  Aventura
                </span>

                <strong>
                  Além do Tempo
                </strong>

                <div className="stars">
                  ★★★★☆
                </div>

              </div>

            </div>


            <div className="movie-card card-front">

              <div className="movie-image image-one">
                🎬
              </div>

              <div className="movie-info">

                <span>
                  Filme em destaque
                </span>

                <strong>
                  O Último Filme
                </strong>

                <div className="rating">

                  <span className="stars">
                    ★★★★★
                  </span>

                  <span className="rating-number">
                    4.9
                  </span>

                </div>

              </div>

            </div>

          </div>

        </section>


        <section className="features">

          <div className="section-title">

            <span>
              POR QUE FILM STAR?
            </span>

            <h2>
              Cinema é melhor
              <span> compartilhado.</span>
            </h2>

          </div>


          <div className="feature-grid">

            <div className="feature-card">

              <div className="feature-icon">
                ⭐
              </div>

              <h3>
                Avalie filmes
              </h3>

              <p>
                Dê sua nota para os filmes que você
                assistiu e compartilhe sua opinião.
              </p>

            </div>


            <div className="feature-card">

              <div className="feature-icon">
                🎬
              </div>

              <h3>
                Descubra novos filmes
              </h3>

              <p>
                Encontre histórias incríveis através
                das avaliações da comunidade.
              </p>

            </div>


            <div className="feature-card">

              <div className="feature-icon">
                💜
              </div>

              <h3>
                Compartilhe sua paixão
              </h3>

              <p>
                Conecte-se com pessoas que também
                amam cinema.
              </p>

            </div>

          </div>

        </section>

      </main>


      <footer className="footer">

        <div className="logo">

          <span className="logo-star">
            ★
          </span>

          <span>
            Film<span>Star</span>
          </span>

        </div>

        <p>
          Seu universo cinematográfico.
        </p>

      </footer>


      {/* ======================================
          MODAL
      ====================================== */}

      {modal && (

        <div
          className="modal-overlay"
          onClick={closeModal}
        >

          <div
            className="modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <button
              className="modal-close"
              onClick={closeModal}
            >
              ×
            </button>


            {modal === "login" ? (

              <>

                <div className="modal-icon">
                  🔐
                </div>

                <h2>
                  Bem-vindo de volta!
                </h2>

                <p className="modal-description">
                  Entre na sua conta para continuar
                  sua jornada pelo mundo do cinema.
                </p>


                <form onSubmit={handleSubmit}>

                  <div className="input-group">

                    <label>
                      Username
                    </label>

                    <input
                      type="text"
                      placeholder="Digite seu username"
                      required
                    />

                  </div>


                  <div className="input-group">

                    <label>
                      Senha
                    </label>

                    <input
                      type="password"
                      placeholder="Digite sua senha"
                      required
                    />

                  </div>


                  <button
                    type="submit"
                    className="modal-button"
                  >
                    Entrar
                  </button>

                </form>


                <p className="modal-footer-text">

                  Ainda não possui uma conta?

                  <button
                    type="button"
                    onClick={() =>
                      setModal("register")
                    }
                  >
                    Registrar
                  </button>

                </p>

              </>

            ) : (

              <>

                <div className="modal-icon">
                  ⭐
                </div>

                <h2>
                  Crie sua conta
                </h2>

                <p className="modal-description">
                  Faça parte da comunidade Film Star.
                </p>


                <form onSubmit={handleSubmit}>

                  <div className="input-group">

                    <label>
                      Username
                    </label>

                    <input
                      type="text"
                      placeholder="Escolha seu username"
                      required
                    />

                  </div>


                  <div className="input-group">

                    <label>
                      Senha
                    </label>

                    <input
                      type="password"
                      placeholder="Crie uma senha"
                      required
                    />

                  </div>


                  <div className="input-group">

                    <label>
                      Idade
                    </label>

                    <input
                      type="number"
                      placeholder="Digite sua idade"
                      min="1"
                      max="120"
                      required
                    />

                  </div>


                  <button
                    type="submit"
                    className="modal-button"
                  >
                    Criar minha conta
                  </button>

                </form>


                <p className="modal-footer-text">

                  Já possui uma conta?

                  <button
                    type="button"
                    onClick={() =>
                      setModal("login")
                    }
                  >
                    Fazer login
                  </button>

                </p>

              </>

            )}

          </div>

        </div>

      )}

    </div>
  );
}

export default App;
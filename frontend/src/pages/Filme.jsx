import { useState } from "react";

import ReviewModal from "../components/ReviewModal";

function Filme({
  movie,
  onBack,
  onLogout
}) {

  const [showReviewModal, setShowReviewModal] =
    useState(false);

  const [reviewRating, setReviewRating] =
    useState(0);

  const [reviewComment, setReviewComment] =
    useState("");


  const handleSubmitReview = () => {

    console.log({
      movie: movie.title,
      rating: reviewRating,
      comment: reviewComment
    });

    setShowReviewModal(false);
    setReviewRating(0);
    setReviewComment("");
  };


  return (
    <div className="dashboard">

      {/* sua sidebar aqui */}

      <main className="dashboard-main">

        <header className="dashboard-header">

          <button
            className="menu-button"
            onClick={onBack}
          >
            ←
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

          <button
            className="back-button"
            onClick={onBack}
          >
            ← Voltar
          </button>


          <div className="movie-detail-main">

            <div className="detail-poster">

              <span>
                {movie.emoji}
              </span>

            </div>


            <div className="movie-detail-info">

              <h1>
                {movie.title}
              </h1>

              <div className="detail-rating">
                ⭐ {movie.rating}
              </div>

              <div className="detail-genres">

                {movie.genres.map(
                  (genre) => (
                    <span key={genre}>
                      {genre}
                    </span>
                  )
                )}

              </div>

              <p>
                {movie.sinopse ||
                  "Sinopse não disponível."}
              </p>

            </div>

          </div>


          <section className="reviews-section">

            <h2>
              Avaliações
            </h2>


            {movie.avaliacoes?.map(
              (review, index) => (

                <div
                  className="review"
                  key={index}
                >

                  <strong>
                    {review.usuario}
                  </strong>

                  <span>
                    ⭐ {review.nota}
                  </span>

                  <p>
                    {review.comentario}
                  </p>

                </div>

              )
            )}


            <button
              className="primary-button"
              onClick={() =>
                setShowReviewModal(true)
              }
            >
              Avaliar filme
            </button>

          </section>

        </section>


        {showReviewModal && (

          <ReviewModal
            rating={reviewRating}
            setRating={setReviewRating}
            comment={reviewComment}
            setComment={setReviewComment}
            onClose={() =>
              setShowReviewModal(false)
            }
            onSubmit={
              handleSubmitReview
            }
          />

        )}

      </main>

    </div>
  );
}

export default Filme;
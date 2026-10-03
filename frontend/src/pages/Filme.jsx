import { useState } from "react";

import ReviewModal from "../components/ReviewModal";

function Filme({
  movie,
  onReview,
  onSetStatus,
  onBack
}) {

  const [showReviewModal, setShowReviewModal] =
    useState(false);

  const [reviewRating, setReviewRating] =
    useState(0);

  const [reviewComment, setReviewComment] =
    useState("");
  const [actionError, setActionError] = useState("");


  const handleSubmitReview = async () => {
    setActionError("");
    try {
      await onReview(reviewRating, reviewComment);
      setShowReviewModal(false);
      setReviewRating(0);
      setReviewComment("");
    } catch (error) {
      setActionError(error.message);
    }
  };

  const handleStatusChange = async (event) => {
    const status = event.target.value;
    if (!status) return;
    setActionError("");
    try {
      await onSetStatus(status);
    } catch (error) {
      setActionError(error.message);
    }
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
              {movie.posterUrl ? (
                <img src={movie.posterUrl} alt={`Pôster de ${movie.title}`} />
              ) : (
                <span>{movie.emoji}</span>
              )}

            </div>


            <div className="movie-detail-info">

              <h1>
                {movie.title}
              </h1>

              <div className="detail-rating">
                {movie.rating == null ? "Sem avaliações" : `⭐ ${movie.rating.toFixed(1)}`}
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

              <label className="list-status-control">
                Minha lista
                <select value={movie.meuStatus || ""} onChange={handleStatusChange}>
                  <option value="">Adicionar à lista...</option>
                  <option value="quero_assistir">Quero assistir</option>
                  <option value="assistindo">Assistindo</option>
                  <option value="assistido">Assistido</option>
                </select>
              </label>

            </div>

          </div>


          <section className="reviews-section">

            <h2>
              Avaliações
            </h2>


            {movie.carregandoAvaliacoes && <p>Carregando avaliações...</p>}

            {!movie.carregandoAvaliacoes && movie.avaliacoes?.length === 0 && (
              <p>Esta obra ainda não tem avaliações.</p>
            )}

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

            {actionError && <p className="form-error" role="alert">{actionError}</p>}

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
            disabled={reviewRating === 0}
          />

        )}

      </main>

    </div>
  );
}

export default Filme;
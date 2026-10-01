function ReviewModal({
  rating,
  setRating,
  comment,
  setComment,
  onClose,
  onSubmit
}) {
  return (
    <div
      className="modal-overlay"
      onClick={onClose}
    >

      <div
        className="modal review-modal"
        onClick={(event) =>
          event.stopPropagation()
        }
      >

        <button
          className="modal-close"
          onClick={onClose}
        >
          ×
        </button>

        <h2>
          Avaliar filme
        </h2>

        <div className="rating-selector">

          {[1, 2, 3, 4, 5].map(
            (star) => (

              <button
                key={star}
                type="button"
                onClick={() =>
                  setRating(star)
                }
              >
                {star <= rating
                  ? "★"
                  : "☆"}
              </button>

            )
          )}

        </div>

        <textarea
          placeholder="Escreva seu comentário..."
          value={comment}
          onChange={(event) =>
            setComment(
              event.target.value
            )
          }
        />

        <button
          className="modal-button"
          onClick={onSubmit}
        >
          Enviar avaliação
        </button>

      </div>

    </div>
  );
}

export default ReviewModal;
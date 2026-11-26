import { createPortal } from "react-dom";

import FilmeDetalhe from "./FilmeDetalhe";
import "./TmdbMinhaLista.css";

function FilmeDetalheModal({ tmdbId, token, usuario, onClose }) {
  return createPortal(
    <div
      className="tmdb-detalhe-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Detalhes do filme"
      onClick={onClose}
      onKeyDown={(event) => {
        if (event.key === "Escape") onClose();
      }}
    >
      <div className="tmdb-detalhe-modal" onClick={(event) => event.stopPropagation()}>
        <button
          type="button"
          className="tmdb-detalhe-modal-fechar"
          onClick={onClose}
          aria-label="Fechar detalhes do filme"
          autoFocus
        >
          ✕
        </button>
        <FilmeDetalhe tmdbId={tmdbId} token={token} usuario={usuario} modal />
      </div>
    </div>,
    document.body,
  );
}

export default FilmeDetalheModal;

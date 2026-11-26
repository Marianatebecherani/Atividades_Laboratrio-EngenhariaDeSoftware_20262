function Sidebar({
  menuOpen,
  activePage,
  setActivePage,
  onClose,
  onLogout
}) {
  return (
    <aside
      className={`sidebar ${
        menuOpen ? "open" : ""
      }`}
    >

      <div className="sidebar-logo">

        <span>★</span>

        {menuOpen && (
          <strong>
            Film<span>Star</span>
          </strong>
        )}

        {menuOpen && (
          <button
            type="button"
            className="sidebar-close"
            onClick={onClose}
            aria-label="Fechar menu lateral"
          >
            ×
          </button>
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
          aria-label="Início"
        >
          <span aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 10.5 12 3l9 7.5" />
              <path d="M5 9.5V20h14V9.5M9 20v-6h6v6" />
            </svg>
          </span>

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
          aria-label="Busca"
        >
          <span aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="10.5" cy="10.5" r="6.5" />
              <path d="m15.5 15.5 4 4" />
            </svg>
          </span>

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
          aria-label="Minha Lista"
        >
          <span aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.5 9c0 4.5-8.5 10-8.5 10S3.5 13.5 3.5 9A4.5 4.5 0 0 1 12 6.9 4.5 4.5 0 0 1 20.5 9Z" />
            </svg>
          </span>

          {menuOpen && (
            <span>Minha Lista</span>
          )}
        </button>

      </nav>

      <button
        className="logout-button"
        onClick={onLogout}
        aria-label="Sair"
      >
        <span aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 4H5v16h5M14 8l4 4-4 4M8 12h10" />
          </svg>
        </span>

        {menuOpen && (
          <span>Sair</span>
        )}
      </button>

    </aside>
  );
}

export default Sidebar;
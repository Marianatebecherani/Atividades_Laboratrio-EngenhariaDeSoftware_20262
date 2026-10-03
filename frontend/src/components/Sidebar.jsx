function Sidebar({
  menuOpen,
  activePage,
  setActivePage,
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
  );
}

export default Sidebar;
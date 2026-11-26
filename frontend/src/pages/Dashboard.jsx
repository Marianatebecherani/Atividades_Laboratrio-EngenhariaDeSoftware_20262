import { useRef, useState } from "react";

import Sidebar from "../components/Sidebar";

import Inicio from "./Inicio";
import Busca from "./Busca";
import MinhaLista from "./MinhaLista";

function Dashboard({ token, usuario, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(true);
  const menuButtonRef = useRef(null);
  const [activePage, setActivePage] = useState("inicio");
  const [termoHome, setTermoHome] = useState("");
  const [termoInicialBusca, setTermoInicialBusca] = useState("");

  const navegar = (pagina) => {
    setTermoInicialBusca("");
    setActivePage(pagina);
  };

  const pesquisarNaHome = (event) => {
    event.preventDefault();
    const termo = termoHome.trim();
    if (!termo) return;

    setTermoInicialBusca(termo);
    setTermoHome("");
    setActivePage("busca");
  };

  return (
    <div className={`dashboard${activePage === "inicio" ? " dashboard-home" : ""}`}>

      <Sidebar
        menuOpen={menuOpen}
        activePage={activePage}
        setActivePage={navegar}
        onClose={() => {
          setMenuOpen(false);
          menuButtonRef.current?.focus();
        }}
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
            ref={menuButtonRef}
            type="button"
            className="menu-button"
            aria-label={menuOpen ? "Recolher menu lateral" : "Expandir menu lateral"}
            aria-expanded={menuOpen}
            onClick={() =>
              setMenuOpen(!menuOpen)
            }
          >
            ☰
          </button>

          {activePage === "inicio" && (
            <form className="home-header-search" role="search" onSubmit={pesquisarNaHome}>
              <button type="submit" aria-label="Pesquisar filmes">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle cx="10.5" cy="10.5" r="6.5" />
                  <path d="m15.5 15.5 4 4" />
                </svg>
              </button>
              <input
                type="search"
                value={termoHome}
                onChange={(event) => setTermoHome(event.target.value)}
                placeholder="Pesquisar filmes..."
                aria-label="Pesquisar filmes"
                required
              />
            </form>
          )}

          <div className="dashboard-user">

            <div className="user-avatar">
              {usuario?.nome?.[0]?.toUpperCase() || "U"}
            </div>

            <span>
              {usuario?.nome || "Usuário"}
            </span>

          </div>

        </header>


        {activePage === "inicio" && <Inicio token={token} usuario={usuario} />}
        {activePage === "busca" && <Busca token={token} usuario={usuario} termoInicial={termoInicialBusca} />}
        {activePage === "lista" && <MinhaLista token={token} usuario={usuario} />}

      </main>

    </div>
  );
}

export default Dashboard;
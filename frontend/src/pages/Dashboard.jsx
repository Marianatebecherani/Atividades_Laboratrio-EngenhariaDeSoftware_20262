import { useState } from "react";

import Sidebar from "../components/Sidebar";

import Inicio from "./Inicio";
import Busca from "./Busca";
import MinhaLista from "./MinhaLista";

function Dashboard({ token, usuario, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(true);
  const [activePage, setActivePage] = useState("inicio");

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


        {activePage === "inicio" && <Inicio token={token} />}
        {activePage === "busca" && <Busca token={token} />}
        {activePage === "lista" && <MinhaLista token={token} />}

      </main>

    </div>
  );
}

export default Dashboard;
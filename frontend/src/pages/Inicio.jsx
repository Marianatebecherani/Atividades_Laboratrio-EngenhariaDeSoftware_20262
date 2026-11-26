import TmdbSearch from "../components/TmdbSearch";
import Recomendacoes from "../components/Recomendacoes";
import "./Inicio.css";

function Inicio({ token, usuario }) {
  return (
    <div className="home-content">
      <section className="welcome-section">
        <div>
          <span>BEM-VINDO AO FILM STAR</span>

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

      <Recomendacoes token={token} usuario={usuario} />

      <TmdbSearch token={token} usuario={usuario} compacto />

      <TmdbSearch
        token={token}
        usuario={usuario}
        compacto
        categoria="now-playing"
      />

      <TmdbSearch
        token={token}
        usuario={usuario}
        compacto
        categoria="top-rated"
      />
    </div>
  );
}

export default Inicio;

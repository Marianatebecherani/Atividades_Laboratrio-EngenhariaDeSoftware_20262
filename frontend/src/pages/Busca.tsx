import TmdbSearch from "../components/TmdbSearch";

function Busca({ token, usuario, termoInicial = "" }) {
  return (
    <section className="page-section search-page">
      <TmdbSearch token={token} usuario={usuario} termoInicial={termoInicial} />
    </section>
  );
}

export default Busca;
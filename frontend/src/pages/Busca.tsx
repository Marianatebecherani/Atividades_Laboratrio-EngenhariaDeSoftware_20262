import TmdbSearch from "../components/TmdbSearch";

function Busca({ token, usuario }) {
  return (
    <section className="page-section search-page">
      <TmdbSearch token={token} usuario={usuario} />
    </section>
  );
}

export default Busca;
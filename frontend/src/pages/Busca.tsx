import TmdbSearch from "../components/TmdbSearch";

function Busca({ token }) {
  return (
    <section className="page-section search-page">
      <TmdbSearch token={token} />
    </section>
  );
}

export default Busca;
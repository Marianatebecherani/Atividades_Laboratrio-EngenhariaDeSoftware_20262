import TmdbMinhaLista from "../components/TmdbMinhaLista";

function MinhaLista({ token }) {
  return (
    <section className="page-section">
      <TmdbMinhaLista token={token} />
    </section>
  );
}

export default MinhaLista;
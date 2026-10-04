import TmdbMinhaLista from "../components/TmdbMinhaLista";

function MinhaLista({ token, usuario }) {
  return (
    <section className="page-section">
      <TmdbMinhaLista token={token} usuario={usuario} />
    </section>
  );
}

export default MinhaLista;
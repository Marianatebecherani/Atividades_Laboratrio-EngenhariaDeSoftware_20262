import { useCallback, useEffect, useState } from "react";

import { listarFilmesUsuarioTmdb, obterFilmeTmdb } from "../api";
import FilmeDetalheModal from "./FilmeDetalheModal";

const ROTULOS_STATUS = {
  quero_assistir: "Quero assistir",
  assistindo: "Assistindo",
  assistido: "Assistido",
};

// "" mostra todos os filmes acompanhados (com ou sem status na lista).
const FILTROS = [["", "Todos"], ...Object.entries(ROTULOS_STATUS)];

function TmdbMinhaLista({ token, usuario }) {
  const [itens, setItens] = useState([]);
  const [pagina, setPagina] = useState(1);
  const [filtro, setFiltro] = useState("");
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [detalheAberto, setDetalheAberto] = useState(null);
  const tamanho = 8;

  const carregarLista = useCallback(() => {
    let ativo = true;
    listarFilmesUsuarioTmdb(token, pagina, filtro)
      .then(async (resposta) => {
        const filmes = await Promise.all(
          resposta.itens.map(async (estado) => {
            try {
              return { estado, filme: await obterFilmeTmdb(estado.tmdb_id) };
            } catch {
              return { estado, filme: null };
            }
          }),
        );
        if (ativo) {
          setItens(filmes);
          setTotal(resposta.total);
          setErro("");
        }
      })
      .catch((error) => {
        if (ativo) setErro(error.message);
      })
      .finally(() => {
        if (ativo) setCarregando(false);
      });
    return () => {
      ativo = false;
    };
  }, [token, pagina, filtro]);

  useEffect(() => carregarLista(), [carregarLista]);

  const fecharDetalhe = () => {
    setDetalheAberto(null);
    carregarLista();
  };

  const selecionarFiltro = (valor) => {
    if (valor === filtro) return;
    // Limpa a lista para não mostrar filmes de outro status enquanto a nova carrega.
    setItens([]);
    setTotal(0);
    setErro("");
    setCarregando(true);
    setPagina(1);
    setFiltro(valor);
  };

  return (
    <section className="tmdb-user-list">
      <h2>Seus filmes TMDb</h2>
      <div className="tmdb-category-tabs" role="group" aria-label="Filtrar seus filmes por status">
        {FILTROS.map(([valor, rotulo]) => (
          <button
            key={valor || "todos"}
            type="button"
            aria-pressed={filtro === valor}
            onClick={() => selecionarFiltro(valor)}
          >
            {rotulo}
          </button>
        ))}
      </div>
      {carregando && itens.length === 0 && (
        <p className="data-loading" aria-live="polite">Carregando seus filmes TMDb...</p>
      )}
      {erro && <p className="tmdb-error" role="alert">{erro}</p>}
      {!carregando && itens.length === 0 && !erro && (
        <p>
          {filtro
            ? `Nenhum filme marcado como "${ROTULOS_STATUS[filtro]}".`
            : "Seus status, avaliações e favoritos de filmes TMDb aparecerão aqui."}
        </p>
      )}
      <div className="tmdb-user-list-grid">
        {itens.map(({ estado, filme }) => (
          <article className="tmdb-user-list-item" key={estado.tmdb_id}>
            <button
              type="button"
              className="tmdb-user-list-item-button"
              onClick={() => setDetalheAberto(estado.tmdb_id)}
            >
              {filme?.poster_url ? (
                <img src={filme.poster_url} alt={`Pôster de ${filme.titulo}`} loading="lazy" />
              ) : (
                <span className="tmdb-no-poster">TMDb {estado.tmdb_id}</span>
              )}
              <div>
                <h3>{filme?.titulo || `Filme TMDb ${estado.tmdb_id}`}</h3>
                {estado.status && <p>{ROTULOS_STATUS[estado.status]}</p>}
                {estado.favorito && <p>Favorito</p>}
                {estado.nota_pessoal != null && <p>Sua nota: {estado.nota_pessoal} / 5</p>}
                {filme?.nota_tmdb != null && <p>TMDb: {filme.nota_tmdb.toFixed(1)} / 10</p>}
                {estado.comentario && <p>{estado.comentario}</p>}
              </div>
            </button>
          </article>
        ))}
      </div>
      {total > tamanho && (
        <nav className="tmdb-pagination" aria-label="Paginação dos seus filmes TMDb">
          <button
            type="button"
            disabled={pagina <= 1 || carregando}
            onClick={() => {
              setCarregando(true);
              setPagina(pagina - 1);
            }}
          >
            Anterior
          </button>
          <span>Página {pagina} de {Math.ceil(total / tamanho)}</span>
          <button
            type="button"
            disabled={pagina >= Math.ceil(total / tamanho) || carregando}
            onClick={() => {
              setCarregando(true);
              setPagina(pagina + 1);
            }}
          >
            Próxima
          </button>
        </nav>
      )}
      {detalheAberto && (
        <FilmeDetalheModal
          tmdbId={detalheAberto}
          token={token}
          usuario={usuario}
          onClose={fecharDetalhe}
        />
      )}
    </section>
  );
}

export default TmdbMinhaLista;
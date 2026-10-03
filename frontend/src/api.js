const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

async function requisicao(caminho, opcoes = {}) {
  const { token, ...configuracao } = opcoes;
  const cabecalhos = new Headers(configuracao.headers);

  if (token) {
    cabecalhos.set("Authorization", `Bearer ${token}`);
  }

  if (configuracao.body && !(configuracao.body instanceof URLSearchParams)) {
    cabecalhos.set("Content-Type", "application/json");
  }

  const resposta = await fetch(`${API_BASE}${caminho}`, {
    ...configuracao,
    headers: cabecalhos,
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.detail || `Erro HTTP ${resposta.status}`);
  }

  if (resposta.status === 204) {
    return null;
  }

  return resposta.json();
}

export function entrar(email, senha) {
  const formulario = new URLSearchParams({ username: email, password: senha });
  return requisicao("/auth/login", { method: "POST", body: formulario });
}

export function cadastrar(nome, email, senha) {
  return requisicao("/auth/cadastro", {
    method: "POST",
    body: JSON.stringify({ nome, email, senha }),
  });
}

export function obterPerfil(token) {
  return requisicao("/usuarios/me", { token });
}

export function listarObras(token) {
  return requisicao("/obras?pagina=1&tamanho=100&ordenar_por=media&direcao=desc", {
    token,
  });
}

export function listarGeneros(token) {
  return requisicao("/generos", { token });
}

export function listarMinhaLista(token) {
  return requisicao("/usuarios/me/lista?pagina=1&tamanho=100", { token });
}

export function obterRecomendacoes(token) {
  return requisicao("/usuarios/me/recomendacoes?estrategia=generos&limite=20", {
    token,
  });
}

export function listarAvaliacoes(obraId, token) {
  return requisicao(`/obras/${obraId}/avaliacoes?pagina=1&tamanho=100`, { token });
}

export function avaliarObra(obraId, nota, comentario, token) {
  return requisicao(`/obras/${obraId}/avaliacoes/me`, {
    method: "PUT",
    token,
    body: JSON.stringify({ nota, comentario }),
  });
}

export function definirStatusLista(obraId, status, token) {
  return requisicao(`/usuarios/me/lista/${obraId}`, {
    method: "PUT",
    token,
    body: JSON.stringify({ status }),
  });
}

export function buscarFilmesTmdb(query, page = 1) {
  const parametros = new URLSearchParams({ query, page: String(page) });
  return requisicao(`/filmes/buscar?${parametros}`);
}

export function obterFilmeTmdb(tmdbId) {
  return requisicao(`/filmes/${tmdbId}`);
}

export function listarFilmesTmdb(categoria, page = 1) {
  return requisicao(`/filmes/${categoria}?page=${page}`);
}

export function descobrirFilmesTmdb(filtros = {}) {
  const parametros = new URLSearchParams();
  Object.entries(filtros).forEach(([chave, valor]) => {
    if (valor !== undefined && valor !== null && valor !== "") {
      parametros.set(chave, String(valor));
    }
  });
  return requisicao(`/filmes/discover?${parametros}`);
}

export function listarGenerosTmdb() {
  return requisicao("/filmes/generos");
}

export function obterEstadoFilmeTmdb(tmdbId, token) {
  return requisicao(`/usuarios/me/filmes/${tmdbId}`, { token });
}

export function definirStatusFilmeTmdb(tmdbId, status, token) {
  return requisicao(`/usuarios/me/filmes/${tmdbId}/lista`, {
    method: "PUT",
    token,
    body: JSON.stringify({ status }),
  });
}

export function removerStatusFilmeTmdb(tmdbId, token) {
  return requisicao(`/usuarios/me/filmes/${tmdbId}/lista`, { method: "DELETE", token });
}

export function avaliarFilmeTmdb(tmdbId, nota, comentario, token) {
  return requisicao(`/usuarios/me/filmes/${tmdbId}/avaliacao`, {
    method: "PUT",
    token,
    body: JSON.stringify({ nota, comentario }),
  });
}

export function favoritarFilmeTmdb(tmdbId, token) {
  return requisicao(`/filmes/${tmdbId}/favoritar`, { method: "POST", token });
}

export function desfavoritarFilmeTmdb(tmdbId, token) {
  return requisicao(`/filmes/${tmdbId}/favoritar`, { method: "DELETE", token });
}

export function listarFavoritosTmdb(token, page = 1) {
  return requisicao(`/usuarios/me/favoritos?pagina=${page}&tamanho=20`, { token });
}

export function listarFilmesUsuarioTmdb(token, page = 1) {
  return requisicao(`/usuarios/me/filmes?pagina=${page}&tamanho=8`, { token });
}

export function filmeDaApi(obra) {
  return {
    id: obra.id,
    title: obra.titulo,
    genres: obra.generos.map((genero) => genero.nome),
    genre: obra.generos[0]?.nome || (obra.tipo === "serie" ? "Série" : "Filme"),
    rating: obra.media_notas,
    classification: obra.classificacao_indicativa,
    emoji: "🎬",
    type: obra.tipo,
    sinopse: obra.sinopse,
    posterUrl: obra.url_poster,
    meuStatus: obra.meu_status,
  };
}

export function avaliacaoDaApi(avaliacao) {
  return {
    usuario: avaliacao.usuario.nome,
    nota: avaliacao.nota,
    comentario: avaliacao.comentario,
  };
}
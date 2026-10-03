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


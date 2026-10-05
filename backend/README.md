# Backend

API REST do Filmstar. Os filmes, séries, gêneros, imagens e demais metadados são consultados no TMDb; o PostgreSQL guarda apenas contas e estado pessoal associado a IDs TMDb.

## Tecnologias

- Python 3.12+ com FastAPI
- SQLAlchemy 2 e Alembic
- PostgreSQL com psycopg 3
- HTTPX para integração assíncrona com o TMDb
- pwdlib com Argon2 e PyJWT
- uv, pytest e Ruff

## Configuração

Pré-requisitos: `uv` e PostgreSQL em execução. Para iniciar o banco local, consulte [infra/](../infra/README.md).

Na pasta `backend/`, copie `.env.example` para `.env` e configure:

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | Banco da aplicação. |
| `TEST_DATABASE_URL` | Banco isolado dos testes. |
| `CORS_ORIGENS` | Origens autorizadas do frontend. |
| `JWT_SEGREDO` | Segredo obrigatório para assinar tokens. |
| `JWT_EXPIRACAO_MINUTOS` | Validade do token (padrão: 60). |
| `TMDB_API_TOKEN` | Token de leitura do TMDb, necessário para buscas e detalhes. |
| `ADMIN_NOME`, `ADMIN_EMAIL`, `ADMIN_SENHA` | Dados opcionais do administrador inicial. |

Obtenha `TMDB_API_TOKEN` em [Configurações da API TMDb](https://www.themoviedb.org/settings/api). Mantenha-o apenas no backend; ele não é enviado ao frontend. O arquivo `.env` é ignorado pelo Git.

Gere `JWT_SEGREDO` com:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Banco de dados

Aplique as migrações a partir de `backend/`:

```bash
uv run alembic upgrade head
```

Opcionalmente, crie o administrador inicial após configurar `ADMIN_EMAIL` e `ADMIN_SENHA`:

```bash
uv run python -m app.db.seed
```

Esse comando cria somente o administrador; não carrega filmes nem metadados locais.

A migration `9d3c7a1b5e20` remove o catálogo local, gêneros e pôsteres. Ela também remove registros antigos de lista e avaliação que não possuíam `tmdb_id`; usuários, favoritos e registros pessoais TMDb são preservados. A reversão restaura tabelas locais vazias, pois os dados removidos não podem ser recuperados.

## Execução

```bash
uv sync
uv run fastapi dev app/main.py
```

A API fica em `http://localhost:8000`. Swagger: `http://localhost:8000/docs`.

## Endpoints

Todas as rotas usam o prefixo `/api/v1`.

| Método | Rota | Autenticação | Descrição |
| --- | --- | --- | --- |
| `GET` | `/saude` | — | Estado da API e do banco. |
| `POST` | `/auth/cadastro` | — | Cria uma conta comum. |
| `POST` | `/auth/login` | — | Autentica (`username` é o e-mail) e retorna JWT. |
| `GET`, `PATCH`, `DELETE` | `/usuarios/me` | Token | Consulta, altera ou remove a própria conta. |
| `GET` | `/filmes/buscar?query=Batman&page=1` | — | Pesquisa filmes no TMDb. |
| `GET` | `/filmes/populares?page=1` | — | Filmes populares. |
| `GET` | `/filmes/top-rated?page=1` | — | Filmes mais bem avaliados. |
| `GET` | `/filmes/now-playing?page=1` | — | Filmes em cartaz. |
| `GET` | `/filmes/upcoming?page=1` | — | Próximos lançamentos. |
| `GET` | `/filmes/discover` | — | Descoberta com filtros TMDb. |
| `GET` | `/filmes/generos` | — | Gêneros de filmes do TMDb. |
| `GET` | `/filmes/{tmdb_id}` | — | Detalhes, créditos e imagens de um filme. |
| `GET` | `/usuarios/me/filmes` | Token | Estado pessoal agregado, paginado. |
| `GET` | `/usuarios/me/filmes/{tmdb_id}` | Token | Status, avaliação e favorito para um filme. |
| `PUT`, `DELETE` | `/usuarios/me/filmes/{tmdb_id}/lista` | Token | Define ou remove status pessoal. |
| `PUT`, `DELETE` | `/usuarios/me/filmes/{tmdb_id}/avaliacao` | Token | Salva ou remove nota pessoal e comentário. |
| `GET` | `/usuarios/me/favoritos` | Token | Lista IDs TMDb favoritados. |
| `POST`, `DELETE` | `/filmes/{tmdb_id}/favoritar` | Token | Adiciona ou remove favorito. |
| `DELETE` | `/avaliacoes/{id}` | Admin | Modera uma avaliação pessoal. |
| `GET` | `/filmes/{tmdb_id}/comentarios?pagina=1&tamanho=20` | — | Lista comentários públicos de um filme, mais recentes primeiro. |
| `GET` | `/filmes/{tmdb_id}/comentarios/meu` | Token | Obtém o comentário público próprio (se existir) nesse filme. |
| `POST` | `/filmes/{tmdb_id}/comentarios` | Token | Cria um comentário público no filme (1 a 2000 caracteres, nota opcional de 1 a 5). |
| `PATCH` | `/comentarios/{id}` | Token (autor) | Edita o conteúdo/nota de um comentário próprio. |
| `DELETE` | `/comentarios/{id}` | Token (autor) | Remove (exclusão lógica) um comentário próprio. |

Nas rotas autenticadas, envie `Authorization: Bearer <token>`. O endpoint `/filmes/discover` aceita gêneros, ano, intervalo de lançamento, nota, idioma, ordenação e página. Os resultados e imagens são obtidos do TMDb em tempo real; o token do provedor nunca é retornado pela API.

A lista, as avaliações e os favoritos guardam apenas o `tmdb_id` e os dados pessoais do usuário. A nota pessoal (1 a 5) é independente da nota pública do TMDb.

Este produto usa a API TMDb, mas não é endossado nem certificado pelo TMDb.

## Testes e qualidade

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
